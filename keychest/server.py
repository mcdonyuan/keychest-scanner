#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Server part of the script
"""

from daemon import Daemon
from core import Core
from config import Config
from dbutil import MySQL

import threading
import pid
import time
import os
import sys
import util
import json
import itertools
import argparse
import calendar
from threading import RLock as RLock
import logging
import coloredlogs
import traceback
import collections
import redis
from datetime import datetime, timedelta
import sqlalchemy as salch


__author__ = 'dusanklinec'
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.INFO)


class AppDeamon(Daemon):
    """
    Daemon wrapper
    """
    def __init__(self, *args, **kwargs):
        Daemon.__init__(self, *args, **kwargs)
        self.app = kwargs.get('app')

    def run(self, *args, **kwargs):
        self.app.work()


class Server(object):
    """
    Main server object
    """

    def __init__(self, *args, **kwargs):
        self.core = Core()
        self.args = None
        self.config = None

        self.logdir = '/var/log/enigma-keychest'
        self.piddir = '/var/run'

        self.daemon = None
        self.running = True
        self.run_thread = None
        self.stop_event = threading.Event()

        self.last_result = None

        self.db = None
        self.redis_pool = None
        self.redis = None

        self.cleanup_last_check = 0
        self.cleanup_check_time = 60
        self.cleanup_thread = None
        self.cleanup_thread_lock = RLock()

    def check_pid(self, retry=True):
        """
        Check the PID lock ownership
        :param retry:
        :return:
        """
        first_retry = True
        attempt_ctr = 0
        while first_retry or retry:
            try:
                first_retry = False
                attempt_ctr += 1

                self.core.pidlock_create()
                if attempt_ctr > 1:
                    print('\nPID lock acquired')
                return True

            except pid.PidFileAlreadyRunningError as e:
                return True

            except pid.PidFileError as e:
                pidnum = self.core.pidlock_get_pid()
                print('\nError: CLI already running in exclusive mode by PID: %d' % pidnum)

                if self.args.pidlock >= 0 and attempt_ctr > self.args.pidlock:
                    return False

                print('Next check will be performed in few seconds. Waiting...')
                time.sleep(3)
        pass

    def return_code(self, code=0):
        self.last_result = code
        return code

    def init_config(self):
        """
        Initializes configuration
        :return:
        """
        if self.args.ebstall:
            self.config = Config.from_file('/etc/enigma/config.json')
            self.config.mysql_user = 'keychest'
            return

        self.config = Core.read_configuration()
        if self.config is None or not self.config.has_nonempty_config():
            sys.stderr.write('Configuration is empty: %s\nCreating default one... (fill in access credentials)\n'
                             % Core.get_config_file_path())

            Core.write_configuration(Config.default_config())
            return self.return_code(1)

        if self.args.server_debug and self.args.daemon:
            # Server debug causes flask to restart the whole daemon (due to server reloading on code change)
            logger.error('Server debug and daemon are mutually exclusive')
            raise ValueError('Invalid start arguments')

    def init_log(self):
        """
        Initializes logging
        :return:
        """
        util.make_or_verify_dir(self.logdir)

    def init_db(self):
        """
        Initializes the database
        :return:
        """
        self.db = MySQL(config=self.config)
        self.db.init_db()

        # redis init
        self.redis_pool = redis.ConnectionPool(host=self.config.redis_host, port=self.config.redis_port, db=0)
        self.redis = redis.Redis(connection_pool=self.redis_pool)

    #
    # Interface
    #

    def on_scan_job(self):
        """
        pass
        :return: 
        """

    #
    # DB Update
    #

    #
    # DB cleanup
    #

    def cleanup_main(self):
        """
        DB trimming & general cleanup thread
        :return:
        """
        logger.info('Cleanup thread started %s %s %s' % (os.getpid(), os.getppid(), threading.current_thread()))
        try:
            while not self.stop_event.is_set():
                try:
                    time.sleep(0.2)
                    cur_time = time.time()
                    if self.cleanup_last_check + self.cleanup_check_time > cur_time:
                        continue

                    # self.trim_sessions_db()
                    self.cleanup_last_check = cur_time

                except Exception as e:
                    logger.error('Exception in DB cleanup: %s' % e)
                    logger.debug(traceback.format_exc())

        except Exception as e:
            logger.error('Exception: %s' % e)
            logger.debug(traceback.format_exc())

        logger.info('Status loop terminated')

    #
    # Server
    #

    def start_daemon(self):
        """
        Starts daemon mode
        :return:
        """
        self.daemon = AppDeamon('/var/run/enigma-keychest-server.pid',
                                stderr=os.path.join(self.logdir, "stderr.log"),
                                stdout=os.path.join(self.logdir, "stdout.log"),
                                app=self)
        self.daemon.start()

    def shutdown_server(self):
        """
        Shutdown flask server
        :return:
        """

    def terminating(self):
        """
        Set state to terminating
        :return:
        """
        self.running = False
        self.stop_event.set()

    def work(self):
        """
        Main work method for the server - accepting incoming connections.
        :return:
        """
        logger.info('Main thread started %s %s %s' % (os.getpid(), os.getppid(), threading.current_thread()))
        try:
            logger.info('Terminating')

        except Exception as e:
            logger.error('Exception: %s' % e)
            logger.error(traceback.format_exc())

        self.terminating()
        logger.info('Work loop terminated')

    def work_loop(self):
        """
        Process configuration, initialize connections, databases, start threads.
        :return:
        """
        # Init
        self.init_config()
        self.init_log()
        self.init_db()

        self.cleanup_thread = threading.Thread(target=self.cleanup_main, args=())
        self.cleanup_thread.setDaemon(True)
        self.cleanup_thread.start()

        # Daemon vs. run mode.
        if self.args.daemon:
            logger.info('Starting daemon')
            self.start_daemon()

        else:
            # if not self.check_pid():
            #     return self.return_code(1)
            self.work()

    def app_main(self):
        """
        Argument parsing & startup
        :return:
        """
        # Parse our argument list
        parser = argparse.ArgumentParser(description='EnigmaBridge keychest server')

        parser.add_argument('-l', '--pid-lock', dest='pidlock', type=int, default=-1,
                            help='number of attempts for pidlock acquire')

        parser.add_argument('--debug', dest='debug', default=False, action='store_const', const=True,
                            help='enables debug mode')

        parser.add_argument('--server-debug', dest='server_debug', default=False, action='store_const', const=True,
                            help='enables server debug mode')

        parser.add_argument('--verbose', dest='verbose', action='store_const', const=True,
                            help='enables verbose mode')

        parser.add_argument('-d', '--daemon', dest='daemon', default=False, action='store_const', const=True,
                            help='Runs in daemon mode')

        parser.add_argument('--ebstall', dest='ebstall', default=False, action='store_const', const=True,
                            help='ebstall compatible mode - uses enigma configuration')

        parser.add_argument('--dump-stats', dest='dump_stats_file', default=None,
                            help='Dumping stats to a file')

        self.args = parser.parse_args()
        if self.args.debug:
            coloredlogs.install(level=logging.DEBUG)

        self.work_loop()


def main():
    """
    Main server starter
    :return:
    """
    app = Server()
    app.app_main()


if __name__ == '__main__':
    main()


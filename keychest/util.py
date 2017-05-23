#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import stat
import json
import hashlib
import base64
import collections
import datetime
import shutil
import calendar
import string
import random
import types
import decimal
import phpserialize

import errno
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

import errors


PAYLOAD_ENC_TYPE = 'AES-256-GCM-SHA256'


class AutoJSONEncoder(json.JSONEncoder):
    """
    JSON encoder trying to_json() first
    """
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, obj):
        try:
            return obj.to_json()
        except AttributeError:
            return self.default_classic(obj)

    def default_classic(self, o):
        if isinstance(o, set):
            return list(o)
        elif isinstance(o, datetime.datetime):
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(AutoJSONEncoder, self).default(o)


def php_obj_hook(obj):
    """
    Object hook for objects with defined php serialization support
    :param obj: 
    :return: 
    """
    try:
        return obj.to_php()
    except AttributeError as e:
        return '%s' % obj


def php_set_protected(obj, name, value):
    """
    Sets protected value for php
    :param obj: 
    :param name: 
    :param value: 
    :return: 
    """
    obj.__php_vars__["\x00*\x00%s" % name] = value
    return obj


def phpize(x):
    """
    Calls to_php if not already a phpobject
    :param x: 
    :return: 
    """
    if isinstance(x, phpserialize.phpobject):
        return x
    try:
        return x.to_php()
    except AttributeError:
        return x


def protect_payload(payload, config):
    """
    Builds a new JSON payload
    :param payload:
    :param config:
    :return:
    """
    js = json.dumps(payload)
    key = make_key(config.vpnauth_enc_password)

    iv, ciphertext, tag = encrypt(key, plaintext=js)

    ret = collections.OrderedDict()
    ret['enctype'] = PAYLOAD_ENC_TYPE
    ret['iv'] = base64.b64encode(iv)
    ret['tag'] = base64.b64encode(tag)
    ret['payload'] = base64.b64encode(ciphertext)
    return ret


def unprotect_payload(payload, config):
    """
    Processes protected request payload
    :param payload:
    :param config:
    :return:
    """
    if payload is None:
        raise ValueError('payload is None')
    if 'enctype' not in payload:
        raise ValueError('Enctype not in payload')
    if payload['enctype'] != PAYLOAD_ENC_TYPE:
        raise ValueError('Unknown payload protection: %s' % payload['enctype'])

    key = make_key(config.vpnauth_enc_password)
    iv = base64.b64decode(payload['iv'])
    tag = base64.b64decode(payload['tag'])
    ciphertext = base64.b64decode(payload['payload'])
    plaintext = decrypt(key=key, iv=iv, ciphertext=ciphertext, tag=tag)

    js = json.loads(plaintext)
    return js


def make_or_verify_dir(directory, mode=0o755, uid=0, strict=False):
    """Make sure directory exists with proper permissions.

    :param str directory: Path to a directory.
    :param int mode: Directory mode.
    :param int uid: Directory owner.
    :param bool strict: require directory to be owned by current user

    :raises .errors.Error: if a directory already exists,
        but has wrong permissions or owner

    :raises OSError: if invalid or inaccessible file names and
        paths, or other arguments that have the correct type,
        but are not accepted by the operating system.

    """
    try:
        os.makedirs(directory, mode)
    except OSError as exception:
        if exception.errno == errno.EEXIST:
            if strict and not check_permissions(directory, mode, uid):
                raise errors.Error(
                    "%s exists, but it should be owned by user %d with"
                    "permissions %s" % (directory, uid, oct(mode)))
        else:
            raise


def check_permissions(filepath, mode, uid=0):
    """Check file or directory permissions.

    :param str filepath: Path to the tested file (or directory).
    :param int mode: Expected file mode.
    :param int uid: Expected file owner.

    :returns: True if `mode` and `uid` match, False otherwise.
    :rtype: bool

    """
    file_stat = os.stat(filepath)
    return stat.S_IMODE(file_stat.st_mode) == mode and file_stat.st_uid == uid


def unique_file(path, mode=0o777):
    """Safely finds a unique file.

    :param str path: path/filename.ext
    :param int mode: File mode

    :returns: tuple of file object and file name

    """
    path, tail = os.path.split(path)
    filename, extension = os.path.splitext(tail)
    return _unique_file(
        path, filename_pat=(lambda count: "%s_%04d%s" % (filename, count, extension if not None else '')),
        count=0, mode=mode)


def _unique_file(path, filename_pat, count, mode):
    while True:
        current_path = os.path.join(path, filename_pat(count))
        try:
            return safe_open(current_path, chmod=mode),\
                os.path.abspath(current_path)
        except OSError as err:
            # "File exists," is okay, try a different name.
            if err.errno != errno.EEXIST:
                raise
        count += 1


def safe_open(path, mode="w", chmod=None, buffering=None):
    """Safely open a file.

    :param str path: Path to a file.
    :param str mode: Same os `mode` for `open`.
    :param int chmod: Same as `mode` for `os.open`, uses Python defaults
        if ``None``.
    :param int buffering: Same as `bufsize` for `os.fdopen`, uses Python
        defaults if ``None``.

    """
    # pylint: disable=star-args
    open_args = () if chmod is None else (chmod,)
    fdopen_args = () if buffering is None else (buffering,)
    return os.fdopen(
        os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, *open_args),
        mode, *fdopen_args)


def make_key(key):
    """
    Returns SHA256 key
    :param key:
    :return:
    """
    h = hashlib.sha256()
    h.update(key)
    return h.digest()


def encrypt(key, plaintext, associated_data=None):
    """
    Uses AES-GCM for encryption
    :param key:
    :param plaintext:
    :param associated_data:
    :return: iv, ciphertext, tag
    """

    # Generate a random 96-bit IV.
    iv = os.urandom(12)

    # Construct an AES-GCM Cipher object with the given key and a
    # randomly generated IV.
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()

    # associated_data will be authenticated but not encrypted,
    # it must also be passed in on decryption.
    if associated_data is not None:
        encryptor.authenticate_additional_data(associated_data)

    # Encrypt the plaintext and get the associated ciphertext.
    # GCM does not require padding.
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    return (iv, ciphertext, encryptor.tag)


def decrypt(key, iv, ciphertext, tag, associated_data=None):
    """
    AES-GCM decryption
    :param key:
    :param associated_data:
    :param iv:
    :param ciphertext:
    :param tag:
    :return:
    """
    # Construct a Cipher object, with the key, iv, and additionally the
    # GCM tag used for authenticating the message.
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()

    # We put associated_data back in or the tag will fail to verify
    # when we finalize the decryptor.
    if associated_data is not None:
        decryptor.authenticate_additional_data(associated_data)

    # Decryption gets us the authenticated plaintext.
    # If the tag does not match an InvalidTag exception will be raised.
    return decryptor.update(ciphertext) + decryptor.finalize()


def silent_close(c):
    # noinspection PyBroadException
    try:
        if c is not None:
            c.close()
    except:
        pass


def unix_time(dt):
    if dt is None:
        return None
    return (dt - datetime.datetime.utcfromtimestamp(0)).total_seconds()


def flush_file(data, filepath):
    """
    Flushes a file to the file e using move strategy
    :param data:
    :param filepath:
    :return:
    """
    abs_filepath = os.path.abspath(filepath)
    fw, tmp_filepath = unique_file(abs_filepath, mode=0o644)
    with fw:
        fw.write(data)
        fw.flush()

    shutil.move(tmp_filepath, abs_filepath)


def get_user_from_cname(cname):
    """
    Get user name from the cname.
    :param cname:
    :return:
    """
    if cname is None:
        return None
    return cname.split('/', 1)[0]


def is_utc_today(utc):
    """
    Returns true if the UTC is today
    :param utc: 
    :return: 
    """
    current_time = datetime.datetime.utcnow()
    day_start = current_time - datetime.timedelta(hours=current_time.hour, minutes=current_time.minute,
                                                  seconds=current_time.second)

    day_start_utc = unix_time(day_start)
    return (utc - day_start_utc) >= 0


def is_dbdate_today(dbdate):
    """
    Returns true if the database DateTime column is today
    :param dbdate: 
    :return: 
    """
    utc = calendar.timegm(dbdate.timetuple())
    return is_utc_today(utc)


def get_yesterday_date_end():
    """
    Returns yesterday midnight date time.
    :return: 
    """
    ct = datetime.datetime.utcnow()
    return datetime.datetime(year=ct.year, month=ct.month, day=ct.day, hour=23, minute=59, second=59) - \
           datetime.timedelta(days=1)


def get_7days_before_date_end():
    """
    Returns yesterday midnight date time.
    :return: 
    """
    ct = datetime.datetime.utcnow()
    return datetime.datetime(year=ct.year, month=ct.month, day=ct.day, hour=23, minute=59, second=59) - \
           datetime.timedelta(days=7)


def get_today_date_start():
    """
    Returns yesterday midnight date time.
    :return: 
    """
    ct = datetime.datetime.utcnow()
    return datetime.datetime(year=ct.year, month=ct.month, day=ct.day, hour=0, minute=0, second=0)


def random_nonce(length):
    """
    Generates a random password which consists of digits, lowercase and uppercase characters
    :param length:
    :return:
    """
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits + "_") for _ in range(length))


def random_alphanum(length):
    """
    Generates a random password which consists of digits, lowercase and uppercase characters
    :param length:
    :return:
    """
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(length))


def strip(x):
    """
    Strips string x (if non empty) or each string in x if it is a list
    :param x:
    :return:
    """
    if x is None:
        return None
    if isinstance(x, types.ListType):
        return [y.strip() if y is not None else y for y in x]
    else:
        return x.strip()


def defval(val, default=None):
    """
    Returns val if is not None, default instead
    :param val:
    :param default:
    :return:
    """
    return val if val is not None else default


def defvalkey(js, key, default=None, take_none=True):
    """
    Returns js[key] if set, otherwise default. Note js[key] can be None.
    :param js:
    :param key:
    :param default:
    :param take_none:
    :return:
    """
    if js is None:
        return default
    if key not in js:
        return default
    if js[key] is None and not take_none:
        return default
    return js[key]


def defvalkeys(js, key, default=None):
    """
    Returns js[key] if set, otherwise default. Note js[key] can be None.
    Key is array of keys. js[k1][k2][k3]...

    :param js:
    :param key:
    :param default:
    :param take_none:
    :return:
    """
    if js is None:
        return default
    try:
        cur = js
        for ckey in key:
            cur = cur[ckey]
        return cur
    except:
        pass
    return default

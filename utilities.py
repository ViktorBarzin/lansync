'''
Read and parse commandline arguments
'''
import argparse
import os
import re
import socket
import sys
from sshpubkeys import SSHKey, InvalidKeyError
from typing import Optional, List
from urllib.request import urlopen
from settings import SECURE_OPTIONS, AUTHORIZED_KEYS_PATH, PATH_TO_PUBLIC_DIR_FILE


def log(msg, level=0) -> None:
    '''
    TODO: implemente some more advanced logging some time. Print for now
    '''
    print(msg)


class ArgParser(object):
    '''
    Arguments list:
        --import <public key file path>
        #--import <public key string> [--key-server <gpg server url>]
    '''
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Parse server arguments')
        # self.parser.add_argument('--import', type=str, help='Add public key to authorized_keys')
        self.parser.add_argument('-i', '--import', dest='pub_key_arg', help='Public key to import. Can import from raw string, file and Github username')
        self.parser.add_argument('--dir', dest='setup_dir', default=os.path.expanduser('~/public/'), help='Directory that will be allowed to share files to.')
        self.parser.add_argument('--size', dest='setup_dir_size', help='Limit of the shared directory. Can use letters e.g: 1M, 2G, 512B, 1024K. Default size is in bytes')

    def parse_args(self, inp=[]) -> argparse.Namespace:
        if inp == []:
            return self.parser.parse_args()
        return self.parser.parse_args(inp)


def get_pub_keys(key: str) -> List[str]:
    '''
    Multi-line string where each line is either:
        - a public key string
        - a location to file containing a public key
        - a url to download a key
    '''
    if key is None or key == '':
        return []
    keys = []
    try:
        for line in key.split('\n'):
            extracted = None
            if os.path.exists(line):
                extracted = get_pub_keys_from_file(line)
                keys.extend(extracted)
            elif is_valid_web_url(line):
                extracted = get_pub_keys_from_url(line)
                keys.extend(extracted)
            elif is_valid_username(line) and not line.startswith('ssh-rsa'):
                # treat line as Github username
                url = get_github_keys_url(line)
                if url is None:
                    continue
                res = get_pub_keys_from_url(url)
                if res is not None:
                    for key in res:
                        keys.append(key)
            else:
                # key is string
                key_to_import = get_pub_key_from_string(line)
                if key_to_import is not None:
                    keys.append(key_to_import)

                # there may be a better way to do this
        return keys
    except ValueError as err:
        print(f'Invalid input: {err}')
        return keys  # maybe return empty to signal error?


def get_pub_keys_from_file(path: str) -> List[str]:
    try:
        keys = []  # type: List[str]
        file_lines = map(lambda x: x.replace('\n', ''), open(path, 'r').readlines())
        for line in file_lines:
            extracted = get_pub_key_from_string(line)
            if extracted is not None:
                keys.append(extracted)
        return keys
    except OSError as err:
        print(f'Couldn\'t read file: {err}')
        return []
    except ValueError as err:
        print(f'Invalid path: {err}')
        return []


def get_pub_key_from_string(key: str) -> Optional[str]:
    if key is None or key == '':
        return None
    ssh_key = SSHKey(key, strict=True)
    try:
        ssh_key.parse()
    except InvalidKeyError as err:
        print(f'Invalid key: {err}')
        return None
    except NotImplementedError as err:
        print(f'Invalid key type: {err}')
        return None
    # Library can return some hash functions of the key
    # I'm just using it for checking - if valid key, return it
    return key


def get_pub_keys_from_url(url: str) -> List[str]:
    # TODO: I mostly use github and it allows multiple keys, maybe adjust this
    # to allow retrieving multiple keys?
    if not is_valid_web_url(url):
        return []
    lines = map(lambda x: x.decode('utf-8').replace('\n', ''), urlopen(url).readlines())
    keys = []
    for line in lines:
        key = get_pub_key_from_string(line)  # allow string entries only
        if key is not None:
            keys.append(key)
    return keys


def is_valid_web_url(url: str) -> bool:
    return not re.match(r'^(https?://)?[a-zA-Z0-9]+\.[a-z]{0,5}', url) is None


def is_valid_username(username: str) -> bool:
    # source - https://github.com/shinnn/github-username-regex
    if username is None or username == '':
        return False
    # Github username may only contain alphanumeric characters or hyphens.
    if not re.search(r'^[a-zA-Z0-9]+[-?\[a-zA-Z0-9\]+]*$', username):
        return False
    # Github username cannot have multiple consecutive hyphens.
    if re.search(r'--', username):
        return False
    # Github username cannot begin or end with a hyphen.
    if re.search(r'^- | -$', username):
        return False
    # Maximum is 39 characters.
    if len(username) > 39:
        return False
    # should be valid
    return True


def is_key_imported(key: str, auth_keys_path=AUTHORIZED_KEYS_PATH) -> bool:
    '''
    Check if ~/.ssh/authorized_keys exists and if key is in there
    '''
    if not os.path.exists(auth_keys_path):
        return False
    return SECURE_OPTIONS + ' ' + key + '\n' in open(auth_keys_path).readlines()


def import_key(key: str, auth_keys_path=AUTHORIZED_KEYS_PATH) -> Optional[str]:
    '''
    Import ssh key only if not imported already
    '''
    if is_key_imported(key, auth_keys_path):
        return None
    with open(auth_keys_path, 'a') as f:
        to_write = SECURE_OPTIONS + ' ' + key + '\n'
        f.write(to_write)
    return key


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    iface = s.getsockname()[0]
    s.close()
    return iface


def get_github_keys_url(username: str) -> Optional[str]:
    if username is None or username == '':
        return None

    url = 'https://github.com/' + username + '.keys'
    req = urlopen(url)
    # if url doesn't exits, exit
    if req.getcode() != 200:
        log(f'User not found: {username}')
        return None
    return url


def parse_size(size: str) -> int:
    # if size is N - where N is a number - just return it
    size_split = re.findall(r'\d+', size)
    if len(size_split) == 0:
        raise ValueError(f'Invalid size: {size}')
    size_int = int(size_split[0])

    units = {'': 1, 'K': 2**10, 'M': 2**20, 'G': 2**30, 'T': 2**40}
    unit = re.findall(r'[^\d]+', size)
    if len(unit) != 1:
        raise ValueError(f'Invalid unit: {unit}')
    unit_str = unit[0]
    return size_int * units[unit_str]


def get_first_partition_offset(drive_path: str) -> int:
    # empirical tests showed that offset is 65536 most of the time
    # if on linux, do some bashing, to extract
    if sys.platform == 'linux' or sys.platform == 'linux2':
        cmd = "parted -s " + drive_path + " unit B print |awk '/^Number/{p=1;next}; p{gsub(/[^[:digit:]]/, \"\", $2); print $2}'"
        result = os.popen(cmd).read()  # run and read output
        size = int(result.split('\n')[0])  # assert first netry is num
    else:
        size = 65536  # seems to work okay
    return size

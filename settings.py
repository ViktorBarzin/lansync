import os
import getpass


# public share path
PATH_TO_PUBLIC_DIR = os.path.expanduser('~/public/')
# path to share virtual filesystem
PATH_TO_PUBLIC_DIR_FILE = os.path.expanduser('~/.pysync/')
PUBLIC_DIR_FILE_NAME = 'share.img'
# options to limit the permissions of the authorized key. change with care!
SECURE_OPTIONS = 'command="rsync --server -e.LsfxC . ' + PATH_TO_PUBLIC_DIR + '",no-pty,no-agent-forwarding,no-port-forwarding'

AUTHORIZED_KEYS_PATH = os.path.expanduser('~/.ssh/authorized_keys')
CURRENT_USER = getpass.getuser()


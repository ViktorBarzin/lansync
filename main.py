'''
Intro point to run.

This script is responsible for setting up the local part of rsync-ing files:
    - Server:
        - read and import source public key and setup secure rsync-ing

    Client:
        - reads address to rsync to
'''
import os
import guestfs
from utilities import ArgParser, get_pub_keys, is_key_imported, import_key, get_local_ip, parse_size, get_first_partition_offset
from settings import CURRENT_USER, PATH_TO_PUBLIC_DIR, AUTHORIZED_KEYS_PATH, PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME


def main() -> None:
    args = ArgParser().parse_args()

    # Check for keys to import
    keys_to_import = get_pub_keys(args.pub_key_arg)
    if keys_to_import is not None and len(keys_to_import) > 0:
        for key in keys_to_import:
            parse_import_key(key)

    # Check for setup dir
    if args.setup_dir_size is not None:
        # if setup dir is passed, make sure dir exists
        if args.setup_dir is not None:
            global PATH_TO_PUBLIC_DIR
            PATH_TO_PUBLIC_DIR = args.setup_dir

            if not os.path.exists(args.setup_dir):
                os.makedirs(args.setup_dir)

        create_share(PUBLIC_DIR_FILE_NAME, args.setup_dir_size)
        part_offset = get_first_partition_offset(os.path.join(PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME))
        print('Created share "' + os.path.join(PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME) + '" and limited it to ' + args.setup_dir_size)
        print('Mount share with the following command: \nsudo mount -o offset=' + str(part_offset) + ',nosuid,uid=' + CURRENT_USER + ',gid=' + CURRENT_USER + ',umask=0077 ' + os.path.join(PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME) + ' ' + PATH_TO_PUBLIC_DIR)

    # run last
    print('\nRsync from client with: rsync <src file> ' + CURRENT_USER + '@' + get_local_ip() + ':' + PATH_TO_PUBLIC_DIR)


def parse_import_key(key_to_import: str) -> None:
    key_imported = is_key_imported(key_to_import)
    if not key_imported:
        import_key(key_to_import, AUTHORIZED_KEYS_PATH)
        print(f'Imported key successfully: {key_to_import[:40]}...<trimmed>...{key_to_import[-20:]}')


def create_share(share_name, share_size='10M') -> str:
    output = os.path.join(PATH_TO_PUBLIC_DIR_FILE, share_name)
    g = guestfs.GuestFS(python_return_dict=True)
    # g.set_trace(1)

    parsed_share_size = parse_size(share_size)
    if parsed_share_size is None:
        raise ValueError(f'Invalid share size: {share_size}')
    g.disk_create(output, 'raw', parsed_share_size)
    g.add_drive_opts(output, format="raw", readonly=0)
    g.launch()
    devices = g.list_devices()
    assert(len(devices) == 1)
    g.part_disk(devices[0], 'mbr')
    partitions = g.list_partitions()
    assert(len(partitions) == 1)
    g.mkfs('fat', partitions[0])
    g.close()
    return share_name


if __name__ == "__main__":
    main()

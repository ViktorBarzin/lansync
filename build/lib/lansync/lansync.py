import os
# import guestfs
from lansync.utilities import ArgParser, get_pub_keys, is_key_imported, import_key, get_local_ip, parse_size, get_first_partition_offset
from lansync.settings import CURRENT_USER, PATH_TO_PUBLIC_DIR, AUTHORIZED_KEYS_PATH, PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME


def main() -> None:
    args = ArgParser().parse_args()
    # make sure conig file exists
    if not os.path.exists(PATH_TO_PUBLIC_DIR_FILE):
        os.makedirs(PATH_TO_PUBLIC_DIR_FILE)

    # Check for keys to import
    keys_to_import = get_pub_keys(args.pub_key_arg)
    if keys_to_import is not None and len(keys_to_import) > 0:
        for key in keys_to_import:
            parse_import_key(key)

    # Check for setup dir
    if args.setup_dir_size is not None:
        # if setup dir is passed, make sure dir exists
        if not os.path.exists(PATH_TO_PUBLIC_DIR):
            os.makedirs(PATH_TO_PUBLIC_DIR)

        create_share(PUBLIC_DIR_FILE_NAME, args.setup_dir_size)
        part_offset = get_first_partition_offset(os.path.join(PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME))
        print('Created share "' + os.path.join(PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME) + '" and limited it to ' + args.setup_dir_size)
        print('Mount share with the following command: \n\nsudo mount -o offset=' + str(part_offset) + ',nosuid,uid=' + CURRENT_USER + ',gid=' + CURRENT_USER + ',umask=0077 ' + os.path.join(PATH_TO_PUBLIC_DIR_FILE, PUBLIC_DIR_FILE_NAME) + ' ' + PATH_TO_PUBLIC_DIR)

    # run last
    print('\nRsync from client with: rsync <src file> ' + CURRENT_USER + '@' + get_local_ip() + ':')


def parse_import_key(key_to_import: str) -> None:
    key_imported = is_key_imported(key_to_import)
    if not key_imported:
        import_key(key_to_import, AUTHORIZED_KEYS_PATH)
        print(f'Imported key successfully: {key_to_import[:40]}...<trimmed>...{key_to_import[-20:]}')

###############################################################################
# guestfs module is dodgy to install so commented out for now
###############################################################################
# def create_share(share_name, share_size='10M') -> str:
#     output = os.path.join(PATH_TO_PUBLIC_DIR_FILE, share_name)
#     g = guestfs.GuestFS(python_return_dict=True)
#     # g.set_trace(1)

#     parsed_share_size = parse_size(share_size)
#     if parsed_share_size is None:
#         raise ValueError(f'Invalid share size: {share_size}')
#     g.disk_create(output, 'raw', parsed_share_size)
#     g.add_drive_opts(output, format="raw", readonly=0)
#     g.launch()
#     devices = g.list_devices()
#     assert(len(devices) == 1)
#     g.part_disk(devices[0], 'mbr')
#     partitions = g.list_partitions()
#     assert(len(partitions) == 1)
#     g.mkfs('fat', partitions[0])
#     g.close()
#     return share_name


def create_share(share_name, share_size='10M') -> str:
    '''
    Utilize some commonly found shell commands to create the share file
    '''
    parsed_share_size = parse_size(share_size)
    output = os.path.join(PATH_TO_PUBLIC_DIR_FILE, share_name)

    # create share file
    fallocate_cmd = 'fallocate -l ' + str(parsed_share_size) + ' ' + output
    os.system(fallocate_cmd)

    # create partition on the file
    os.system('mkfs.fat ' + output)
    return output


if __name__ == "__main__":
    main()

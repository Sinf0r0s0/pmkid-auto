# -*- coding: latin1 -*-
def try_open_read_file(f_name, mode=None):
    try:
        #  read all text
        if mode == 'read':
            return open(f_name).read()
        #  just open
        else:
            try:
                return open(f_name, encoding='latin1')
            except (FileNotFoundError, UnicodeDecodeError) as err:
                print(err)
                exit(1)
    except FileNotFoundError:
        pass


def create_write_file(f_name, f_data, mode='w'):  # to append use mode='a+'
    try:
        with open(f_name, mode) as f:
            f.write((f_data + '\n'))
    except PermissionError as e0:
        print(f'{e0} are you running as a super user?')
        exit(0)


def save_line_in_hashes(file_name, line):
    hashes_file = try_open_read_file(file_name, 'read')
    if hashes_file:
        if line not in hashes_file:
            create_write_file(file_name, line, 'a+')
    else:
        create_write_file(file_name, line, 'a+')


def search_in_potfile(file_name, line, essid_to_print):
    pot_file = try_open_read_file(file_name, 'read')
    if pot_file:
        if line in pot_file:
            print(f'[!] Password of AP "{essid_to_print}" already exist in {file_name}! :)')
            return True

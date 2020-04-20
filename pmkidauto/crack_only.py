import multiprocessing as mp

import pmkidauto.file_man as fm
from pmkidauto.check import Check


class CrackOnly:
    def __init__(self, wordlist_name: str, hash_file='hashes.22000', pot_file='found.potfile'):
        self.hash_file = fm.try_open_read_file(hash_file)
        self.pot_file = pot_file
        self._wordlist_name = wordlist_name
        try:
            self._sem = mp.BoundedSemaphore(value=mp.cpu_count())
        except FileNotFoundError:
            print('Python multiprocessing BoundedSemaphore does not seem to work on your system. Exiting...')
            exit(1)

    def bo_force(self, hash_line):
        wd = fm.try_open_read_file(self._wordlist_name)
        ck = Check(hash_line)
        essid = ck.essid.decode()
        if fm.search_in_potfile(self.pot_file, hash_line, essid):
            return
        self._sem.acquire()
        for line in wd:
            word = line.strip()
            if len(word) <= 7:
                continue
            if ck.check_pass(word):
                print(f'    [FOUND!] => ESSID:"{essid}": PSK:"{word}"')
                to_potfile = f'{hash_line}:{word}'
                print(f'    [HASH] => {to_potfile}')
                fm.create_write_file(self.pot_file, to_potfile, 'a+')
                self._sem.release()
                return
        print(f'[!] AP "{essid}" wordlist exhausted')
        self._sem.release()

    def start(self):
        print('[!] Running...')
        for hash_line in self.hash_file:
            if all([hash_line, not hash_line == '\n']):
                hl = hash_line.rstrip()
                mp.Process(target=self.bo_force, args=(hl,)).start()

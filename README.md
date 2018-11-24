# pmkidauto

Python script to automate capture of PMKID hashes, based on wpa_supplicant

This attack was discovered by the creator of Hashcat @jsteube, described here: https://hashcat.net/forum/thread-7717.html

This script uses the debug mode wpa_suplicant to retrieve pmkid from each parsed AP, and simultaneously uses an internal (very slow) cracker to retrieve the PSK password.

The program creates 3 files:

**hashcat16800.hash** Saves all pmkids found in Hashcat 16800 mode

**pmkidauto.potfile** Saves cracked hashs (hashcat style)

**wpa_supp.conf** wpa_supplicant Configuration file


usage:

    sudo ./pmkidauto.py -i wlan0 -w tiny.txt
    
help:

    -h, --help           show this help message and exit
    -i INTERFACE_TO_USE  wlan interface
    -w WORDLIST_FILE     wordlist file
    -s SCAN_TIME         AP scaning time (default 5 seconds)
    -t TIME_OUT          timeout to retrieve PMKID (default 15 seconds)



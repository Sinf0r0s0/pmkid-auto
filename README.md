# pmkid-auto

Automate capture of PMKID hashes, based on wpa_supplicant manager.

**Without using monitor mode**, runs on any Debian-based distro or architecture like laptops with internal wifi, rooted smartphones (using Termux / NetHunter) or raspberry pi.
And of course with a usb dongle.


This program uses the debug mode from wpa_suplicant to retrieve pmkid from each parsed AP, and simultaneously uses an internal (very slow) cracker to retrieve the PSK password.

The program creates 3 files:

**hashes.22000** Pmkids found in Hashcat 22000 mode

**found.potfile** Cracked hashs (hashcat style)

**wpa_supp.conf** wpa_supplicant Configuration file

## requirements

- wpa_supplicant  (to install: ```sudo apt install wpasupplicant``` )
- python >=3.6

## instalation


    sudo pip3 install git+git://github.com/Sinf0r0s0/pmkid-auto.git
    or
    sudo pip3 install --upgrade https://https://github.com/Sinf0r0s0/pmkid-auto/tarball/master
    

## usage

**Default Mode:**

Once installed, simply call **pmkidauto** from the command line as superuser:

    sudo pmkidauto -i wlan0 -w tiny.txt
    
Use the optional **-s** flags to set the APs **--scan_time** and **-t** for the PMKID hash recovery **--time_out**.
The defaults are scan_time=7  and time_out=15

    sudo pmkidauto -i wlan0 -w tiny_wordlist.txt -s 10 -t 20
    
   
**Crack only mode:**

Use the **-c** flag to only crack the hashes, in the hashes.22000 file.

    
    sudo pmkidauto -c -w tiny_wordlist.txt
    

You can also importing pmkidauto as module and using the Classes Auto and CrackOnly.

    from pmkidauto import Auto, CrackOnly

    auto = Auto('wlx8416f911a4b1',
                wordlist='tiny_wordlist.txt',
                scan_time='5',
                time_out='20')
    auto.start()

    crack_only = CrackOnly('tiny_wordlist.txt',
                           hash_file='my_pmkid_hashes.22000',
                           pot_file='my_potfile.txt')
    crack_only.start()
    
**help:**

    -i, --interface   INTERFACE   wlan interface
    -w, --wordlist    WORDLIST    wordlist file
    -s, --scan_time   SCAN_TIME   AP scaning time (default 7 seconds)
    -t, --time_out    TIME_OUT    timeout to retrieve PMKID (default 15 seconds)
    -c,--crack_only               crack_only-mode on hashes.22000 file


The PMKID hash was discovered by the creator of Hashcat @jsteube, described here: https://hashcat.net/forum/thread-7717.html


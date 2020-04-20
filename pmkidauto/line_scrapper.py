class LineScrapper:
    @staticmethod
    def get_ap_list(lines):
        name_mac = []
        for line in lines.split('\n'):
            line = line.strip()
            if 'Could not read interface' in line:
                print(f'[!] {line}\n')
                exit(1)
            elif 'rfkill: WLAN soft blocked' in line:
                print(f'[!] {line}\n')
                exit(1)
            else:
                if 'BSS: Add new id' in line:
                    ap_name = line.split("'")[1]
                    ap_mac = line.split("'")[0].split()[7]
                    if not any(i == ap_mac for d in name_mac for i in d.values()):
                        name_mac.append({ap_name: ap_mac})
        return name_mac

    @staticmethod
    def get_pmkid(phs):
        for ph in phs.split('\n'):
            ph = ph.strip()
            if 'PMKID from' in ph:
                return ph[49:].replace(" ", "")

#-*- coding: utf-8 -*-
from hashlib import pbkdf2_hmac, sha1
import binascii


t5c = b"""\\]^_XYZ[TUVWPQRSLMNOHIJKDEFG@ABC|}~\x7fxyz{tuvwpqrslmnohijkdefg`abc\x1c\x1d\x1e\x1f\x18\x19\x1a\x1b\x14\x15\x16\x17\x10\x11\x12\x13\x0c\r\x0e\x0f\x08\t\n\x0b\x04\x05\x06\x07\x00\x01\x02\x03<=>?89:;45670123,-./()*+$%&\' !"#\xdc\xdd\xde\xdf\xd8\xd9\xda\xdb\xd4\xd5\xd6\xd7\xd0\xd1\xd2\xd3\xcc\xcd\xce\xcf\xc8\xc9\xca\xcb\xc4\xc5\xc6\xc7\xc0\xc1\xc2\xc3\xfc\xfd\xfe\xff\xf8\xf9\xfa\xfb\xf4\xf5\xf6\xf7\xf0\xf1\xf2\xf3\xec\xed\xee\xef\xe8\xe9\xea\xeb\xe4\xe5\xe6\xe7\xe0\xe1\xe2\xe3\x9c\x9d\x9e\x9f\x98\x99\x9a\x9b\x94\x95\x96\x97\x90\x91\x92\x93\x8c\x8d\x8e\x8f\x88\x89\x8a\x8b\x84\x85\x86\x87\x80\x81\x82\x83\xbc\xbd\xbe\xbf\xb8\xb9\xba\xbb\xb4\xb5\xb6\xb7\xb0\xb1\xb2\xb3\xac\xad\xae\xaf\xa8\xa9\xaa\xab\xa4\xa5\xa6\xa7\xa0\xa1\xa2\xa3"""
t36 = b"""67452301>?<=:;89&\'$%"# !./,-*+()\x16\x17\x14\x15\x12\x13\x10\x11\x1e\x1f\x1c\x1d\x1a\x1b\x18\x19\x06\x07\x04\x05\x02\x03\x00\x01\x0e\x0f\x0c\r\n\x0b\x08\tvwturspq~\x7f|}z{xyfgdebc`anolmjkhiVWTURSPQ^_\\]Z[XYFGDEBC@ANOLMJKHI\xb6\xb7\xb4\xb5\xb2\xb3\xb0\xb1\xbe\xbf\xbc\xbd\xba\xbb\xb8\xb9\xa6\xa7\xa4\xa5\xa2\xa3\xa0\xa1\xae\xaf\xac\xad\xaa\xab\xa8\xa9\x96\x97\x94\x95\x92\x93\x90\x91\x9e\x9f\x9c\x9d\x9a\x9b\x98\x99\x86\x87\x84\x85\x82\x83\x80\x81\x8e\x8f\x8c\x8d\x8a\x8b\x88\x89\xf6\xf7\xf4\xf5\xf2\xf3\xf0\xf1\xfe\xff\xfc\xfd\xfa\xfb\xf8\xf9\xe6\xe7\xe4\xe5\xe2\xe3\xe0\xe1\xee\xef\xec\xed\xea\xeb\xe8\xe9\xd6\xd7\xd4\xd5\xd2\xd3\xd0\xd1\xde\xdf\xdc\xdd\xda\xdb\xd8\xd9\xc6\xc7\xc4\xc5\xc2\xc3\xc0\xc1\xce\xcf\xcc\xcd\xca\xcb\xc8\xc9"""
com = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'


class Check:
    def __init__(self, hash_line):
        hcl = hash_line.split('*')
        self.pmkid = (hcl[2])
        self.mac_ap = (hcl[3])
        self.mac_cli = (hcl[4])
        self.essid = binascii.unhexlify((hcl[5]))
        self._data = binascii.a2b_hex('504d4b204e616d65' + self.mac_ap + self.mac_cli)
    
    def check_pass(self, passwd):
        pmk = pbkdf2_hmac(hash_name='sha1', password=bytes(passwd, 'utf-8'), salt=self.essid, iterations=4096,
                          dklen=32) + com
        _o_pad = pmk.translate(t5c)
        _i_pad = pmk.translate(t36)
        return self.pmkid in sha1(_o_pad + sha1(_i_pad + self._data).digest()).hexdigest()

from __future__ import absolute_import

from pmkidauto.auto import Auto
from pmkidauto.crack_only import CrackOnly


### By Sinf0r0s0/fbfuze  20/04/2020 ###

""" thank's to kcdtv for describing the use of wpa_supplicant here: 
    https://www.wifi-libre.com/topic-1144-revolucion-en-el-crack-wpa-ataque-por-diccionario-contra-pmkid-page-2.html#p11773"""

__project__         = 'pmkidauto'
__version__         = '0.1.0'
__author__          = 'Sinf0r0s0'
__author_email__    = 'noteprof213@gmail.com'
__url__             = 'hhttps://github.com/Sinf0r0s0/pmkid-auto'
__description__     = 'Automatically capture end crack PMKID hashes'
__packages__        = ['pmkidauto', 'pmkidautocli']
__licence__         = 'MIT'
__platforms__       = 'linux'
__python_requires__ = '>=3.6'
__entry_points__ = {
    'console_scripts': [
        'pmkidauto = pmkidautocli.auto_cli:main',
    ],
}
__classifiers__ = [
    "Programming Language :: Python :: 3.6",
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    "License :: OSI Approved :: MIT License",
    "Operating System :: linux",
]

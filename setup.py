################################################################################
# Title:    setup.py
# Project:  Tomado
# Author:   Daniel Gális
#           danielgalis.com
#           danielgalis21@gmail.com
#           GitHub: @mstcgalis
#           Discord: @danielmstc#2967
#           Are.na: are.na/daniel-galis
#
# License:  GPL v3
# 2022
################################################################################

from setuptools import setup

APP = ['Tomado.py']
VERSION = "0.2.3a"
DATA_FILES = ["icons/tomado.icns", 'icons', 'sounds']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps', 'just_playback'],
    'iconfile': "icons/tomado.icns",
}

setup(
    app=APP,
    version=VERSION,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

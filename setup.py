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
# License:  AGPL-3.0
# 2022
################################################################################

from setuptools import setup
from py2app.build_app import py2app as _py2app
from tomado import __version__


class py2app(_py2app):
    # setuptools 61+ reads pyproject.toml and sets install_requires from
    # [project].dependencies. py2app rejects any distribution that has it,
    # expecting deps to already be installed (which uv handles). Clear it
    # before the check runs.
    def finalize_options(self):
        self.distribution.install_requires = []
        super().finalize_options()


APP = ['tomado.py']
DATA_FILES = ['icons', 'sounds']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
    'iconfile': 'icons/tomado.icns',
}

setup(
    app=APP,
    version=__version__,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    cmdclass={'py2app': py2app},
)
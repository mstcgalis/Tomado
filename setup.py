from setuptools import setup

APP = ['Tomado.py']
DATA_FILES = ["tomado.icns", 'icons']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps'],
    'iconfile': "tomado.icns",
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

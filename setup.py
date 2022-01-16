from setuptools import setup

APP = ['Tomado.py']
DATA_FILES = ["tomado.icns", 'icons', 'sounds']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps', 'playsound'],
    'iconfile': "tomado.icns",
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

################################################################################
# Title:    utilities.py
# Project:  Tomado
# Author:   Daniel Gális
#           danielgalis.com
#           danielgalis21@gmail.com
#           GitHub: @mstcgalis
#           Discord: @danielmstc#2967
# License:  GPL v3
#
# 2022
################################################################################

from playsound import playsound
import json
import rumps

def secs_to_time(seconds, hours=False):
    """Takes an integer of seconds and convertes it into a mm:ss string, or a HHh:MMm string

    Args:
        seconds (int): number of seconds to be converted
        hours (bool, optional): if true, returns a HHh:MMm string instead of MM:SS. Defaults to False.

    Returns:
        string: mm:ss string, or a HHh:MMm string
    """
    if hours:
        hours, secs = divmod(seconds, 3600)
        mins, secs = divmod(secs, 60)
        return '{}h {:02d}m'.format(hours, mins)
    else:
        mins, secs = divmod(seconds, 60)
        return '{:02d}:{:02d}'.format(mins, secs)

def button_sound(allow_sound):
    """Plays a button-pressed feedback sound

    Args:
        allow_sound (bool): if true, plays the feedback sound
    """
    if allow_sound:
        playsound("sounds/button.mp3")
    else:
        pass

def create_submenu(button_list, callback, type=""):
    """Creates a submenu containing rumps.MenuItem objects from a list of strings

    Args:
        button_list (list of strings): list of button names in submenu
        type (string): type of interval (pomodoro/break/long)
        callback (function/method): callback function that will be triggered by the buttons

    Returns:
        list: list containing rumps.MenuItem objects
    """
    submenu = []
    for n in button_list:
        if type != "":
            button = rumps.MenuItem("{} Minutes".format(n), callback=callback)
        else:
            button = rumps.MenuItem("{}".format(n), callback=callback)
        button.type = type
        submenu.append(button)
    return submenu

def save_file(file_path, data):
    """saves data into a specified json file, creates one if it doesnt eist

    Args:
        file_path (string): the path of the file
        data (dict, list, tuple, string, int, float, bool): the object to be saved
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def open_file(file_path):
    """opens and parses a json file, which it then returns

    Args:
        file_path (string): the path of the file

    Returns:
        object: data form the file
    """
    with open(file_path) as f:
        try: data = json.load(f)
        except: data = {}
    return data
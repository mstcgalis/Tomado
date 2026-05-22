################################################################################
# Title:    tomado.py
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

__version__ = "0.3.2"

import csv
import json
import os
import time
from datetime import date, datetime

import rumps

from utilities import *

class Tomado(object):
    def __init__(self):
        ## CONFIG
        # settings that cant't be user defined for now
        self.config = {
            "app_name" : "Tomado",
            "pomodoro_message": "Pomodoro is over. Take a break! 🪴",
            "break_message": "Break has concluded. Time to focus! 🍅",
            "long_message": "Session is finished. Good job! 🌻",
            "not_clickable_message": "This button is not clickable yet, sorry 🌸",
            "clock_empty": "◯ ",
            "clock_half": "⏳",
            "clock_full": "🍅",
            "pomodoro_symbol" : "icons/pomodoro.png",
            "break_symbol" : "icons/break.png",
            "long_symbol" : "icons/long.png",
            "pomodoro_length_options" : ["5", "10", "15", "20", "25", "30", "40", "45", "60"],
            "break_length_options" : ["3", "5", "10", "15", "20"],
            "long_length_options" : ["10", "15", "20", "25", "30"],
            "sound_options" : ["Beep", "Birds", "Ding", "Cicadas", "Wood"]
        }
       
        ## SESSION
        # list representing the order and type of intervals in a session
        self.session_general = [
            "pomodoro",
            "break",
            "pomodoro",
            "break",
            "pomodoro",
            "break",
            "pomodoro",
            "long_break",
        ]
        # dictionary representing the active session made from the session_general
        self.session_current = {}
        
        ## APP
        # the quit button is changed to say Quit Tomado and the shortcut key is added
        self.quit_button = rumps.MenuItem("Quit {}".format(self.config.get("app_name")), callback=self.quit, key="q")
        # variable containing the rumps.App class
        self.app = rumps.App(self.config.get("app_name"), quit_button=None)

        ## TIMER
        # variable containing the rumps.Timer class, arugments are its callback function (tick) and interval (1 sec)
        self.timer = rumps.Timer(self.tick, 1)
        # creates application_support folder if there isnt one
        self.folder = rumps.application_support(self.config.get("app_name"))
        
        ## PREFERENCES
        # settings that can be user defined
        # default prefs
        self.default_prefs = {
            "version": __version__,
            "pomodoro_length": 1500,
            "break_length": 300,
            "long_length": 900,
            "autostart_pomodoro": True,
            "autostart_break": True,
            "autostart_session": False,
            "allow_sound": True,
            "sound_volume": 1,
            "timer_sound": "sounds/beep.mp3",
            "current_project": "",
            "projects": []
        }
        # path to the preferences file
        self.prefs_path = str(self.folder + "/prefs.json")

        # open prefs from file
        try:
            with open(self.prefs_path, "r") as f:
                self.prefs = json.load(f)
        # if it is empty (file didnt exist) use default prefs
        except FileNotFoundError:
            self.prefs = self.default_prefs    
            save_file(self.prefs_path, self.prefs)

        # if the version doesnt match, use the saved preferences where possible
        if self.prefs.get("version") != self.config.get("version"):
            self.prefs = prefs_update(self.prefs, self.default_prefs)
            save_file(self.prefs_path, self.prefs)
        # setting up the playback object for notification sounds
        self.notification_playback = load_sound(self.prefs.get("timer_sound"))
        self.notification_playback.setVolume_(self.prefs.get("sound_volume"))
        
        ## STATS
        self.stats_path = str(self.folder + '/stats.json')
        # initialise with empty list if missing or in the old dict format
        if not read_stats(self.stats_path):
            save_file(self.stats_path, [])
        # ISO timestamp set when an interval starts, used as the record's start time
        self.interval_start = ""

        ## PROJECT
        self.project_button = rumps.MenuItem("○ No Project")

        ## GENERAL BUTTONS
        # non clickable button showing info about current session
        self.session_info = rumps.MenuItem("Session info", callback=self.not_clickable_notification)
        # end session button
        self.end_session_button = rumps.MenuItem("End Session", callback=self.end_session, key="e")
        # about button
        self.about_button = rumps.MenuItem("About {}".format(self.config.get("app_name")), callback=self.about_info)
        
        # preferences button
        self.preferences_button = rumps.MenuItem("Preferences")
        # pomodoro interval preference
        self.pomodoro_length_button = rumps.MenuItem("Pomodoro Length")
        self.pomodoro_length_options = create_submenu(self.config.get("pomodoro_length_options"), self.change_length, "pomodoro")
        # break length preference
        self.break_length_button = rumps.MenuItem("Short Break Length")
        self.break_length_options = create_submenu(self.config.get("break_length_options"), self.change_length, "break")
        # long break length preference
        self.long_length_button = rumps.MenuItem("Long Break Length")
        self.long_length_options = create_submenu(self.config.get("long_length_options"), self.change_length, "long")
        # autostart pomodoros toggle
        self.autostart_pomodoro_button = rumps.MenuItem("Autostart Pomodoros", callback=self.autostart_toggle)
        self.autostart_pomodoro_button.type = "pomodoro"
        # autostart breaks toggle
        self.autostart_break_button = rumps.MenuItem("Autostart Breaks", callback=self.autostart_toggle)
        self.autostart_break_button.type = "break"
        # autostart session toggle
        self.autostart_session_button = rumps.MenuItem("Autostart Sessions", callback=self.autostart_toggle)
        self.autostart_session_button.type = "session"
        # sounds toggle
        self.allow_sounds_button = rumps.MenuItem("Allow Sounds", callback=self.sounds_toggle)
        # sound volume
        self.sound_volume = rumps.MenuItem("Sound Volume")
        self.sound_volume_options = create_submenu(list(str(i)+"%" for i in range(10, 110, 10)), self.change_volume)
        # sound preferences
        self.sound_preferences_button = rumps.MenuItem("Timer Sound")
        self.sound_options = create_submenu(self.config.get("sound_options"), self.change_sound)
        
        # stats submenus
        self.stats_today_submenu = rumps.MenuItem("Daily Stats")
        self.stats_week_submenu = rumps.MenuItem("Weekly Stats")
        # shows pomodoros tracked today / this week
        self.stats_today_pomodoros = rumps.MenuItem("Pomodoros:", callback=self.not_clickable_notification)
        self.stats_today_pomodoros.icon = self.config.get("pomodoro_symbol")
        self.stats_week_pomodoros = rumps.MenuItem("Pomodoros:", callback=self.not_clickable_notification)
        self.stats_week_pomodoros.icon = self.config.get("pomodoro_symbol")
        # shows breaks tracked today / this week
        self.stats_today_breaks = rumps.MenuItem("Breaks:", callback=self.not_clickable_notification)
        self.stats_today_breaks.icon = self.config.get("break_symbol")
        self.stats_week_breaks = rumps.MenuItem("Breaks:", callback=self.not_clickable_notification)
        self.stats_week_breaks.icon = self.config.get("break_symbol")
        # active project line and per-project breakdown
        self.stats_today_project = rumps.MenuItem("○ No active project", callback=self.not_clickable_notification)
        self.stats_today_by_project = rumps.MenuItem("By Project")
        self.stats_week_project = rumps.MenuItem("○ No active project", callback=self.not_clickable_notification)
        self.stats_week_by_project = rumps.MenuItem("By Project")
        # all time stats
        self.stats_all_time_submenu = rumps.MenuItem("All Time Stats")
        self.stats_all_time_pomodoros = rumps.MenuItem("Pomodoros:", callback=self.not_clickable_notification)
        self.stats_all_time_pomodoros.icon = self.config.get("pomodoro_symbol")
        self.stats_all_time_breaks = rumps.MenuItem("Breaks:", callback=self.not_clickable_notification)
        self.stats_all_time_breaks.icon = self.config.get("break_symbol")
        self.stats_all_time_project = rumps.MenuItem("○ No active project", callback=self.not_clickable_notification)
        self.stats_all_time_by_project = rumps.MenuItem("By Project")
        # export and clear
        self.export_stats_button = rumps.MenuItem("Export Stats…", callback=self.export_stats)
        self.clear_stats_button = rumps.MenuItem("Clear Stats…", callback=self.clear_stats)


        ## TIMER BUTTONS
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.start_button = rumps.MenuItem("Start", callback=self.start_timer, key="s", icon="icons/start.png", template=True)
        # pause_pomodoro button is created as a rumps.MenuItem, callback is the pause_timer method
        self.pause_button = rumps.MenuItem("Pause", callback=self.pause_timer, key="p", icon="icons/pause.png", template=True)
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.continue_button = rumps.MenuItem("Continue", callback=self.continue_timer, key="s", icon="icons/start.png", template=True)
        # the skip_pomodoro button is created as a rumps.MenuItem, callback is the skip_timer method
        self.skip_button = rumps.MenuItem("Skip", callback=self.skip_timer, icon="icons/skip.png", template=True)
        # the reset_pomodoro button is created as a rumps.MenuItem, callback is the reset_timer method
        self.reset_button = rumps.MenuItem("Reset", callback=self.reset_timer, key="r", icon="icons/reset.png", template=True)

        ## MENU
        self.menus = {"default_menu" :
                [self.project_button,
                None,
                self.start_button,
                self.reset_button,
                self.skip_button,
                None,
                self.session_info,
                self.end_session_button,
                None,
                [self.stats_today_submenu,
                    [self.stats_today_pomodoros,
                    self.stats_today_breaks,
                    self.stats_today_project,
                    [self.stats_today_by_project, []]]],
                [self.stats_week_submenu,
                    [self.stats_week_pomodoros,
                    self.stats_week_breaks,
                    self.stats_week_project,
                    [self.stats_week_by_project, []]]],
                [self.stats_all_time_submenu,
                    [self.stats_all_time_pomodoros,
                    self.stats_all_time_breaks,
                    self.stats_all_time_project,
                    [self.stats_all_time_by_project, []]]],
                None,
                self.export_stats_button,
                self.clear_stats_button,
                None,
                [self.preferences_button, 
                    [[self.pomodoro_length_button, 
                        self.pomodoro_length_options], 
                    [self.break_length_button, 
                        self.break_length_options], 
                    [self.long_length_button, 
                        self.long_length_options],
                    None,
                    self.autostart_pomodoro_button,
                    self.autostart_break_button,
                    self.autostart_session_button,
                    None,
                    self.allow_sounds_button,
                    [self.sound_volume,
                        self.sound_volume_options],
                    [self.sound_preferences_button, 
                        self.sound_options]
                    ]
                ],
                None,
                self.about_button,
                self.quit_button]
            }
        
        ## DEFAULT menu and state
        # create a session from the session_general
        self.load_session()
        # set the menu to the default (first button is Start)
        self.app.menu.update(self.menus.get("default_menu"))
        # set the menu to the right interval types
        self.update_menu()
        # loaded state of timer
        self.load_timer("startup")
        # display the right preferences (sound toggle, sound select, autostart toggles)
        self.startup_display_preferences()
        # build the project selector submenu
        self._rebuild_project_menu()
    
    ## STATES AND MENUS
    def load_timer(self, sender):
        """sets the menu to the correct state, loads next interval, starting it if autostart is True for current interval type

        Args:
            sender (string, MenuItem): information on the sender
        """
        #stop the current timer
        self.timer.stop()
        #reset the current timer
        self.timer.count = 0

        autostart = False
        interval_type = self.get_current_interval_type()
        if sender == "end_session":
            autostart = self.prefs.get("autostart_session")
        else:
            if self.prefs.get("autostart_pomodoro") and interval_type == "pomodoro":
                autostart = True
            elif self.prefs.get("autostart_break") and interval_type in ("break", "long"):
                autostart = True
            elif self.prefs.get("autostart_session") and not interval_type:
                autostart = True

        # check wheter the session is not over aka there is not a bool value in session
        if self.get_current_interval_type() is False:
            #if it is over, trigger a method for ending a session
            self.end_session(sender="loaded_state")

        # change the title to the current interval
        self.app.title = secs_to_time(self.prefs.get("{}_length".format(self.get_current_interval_type())))
        self.app.icon = self.config.get("{}_symbol".format(self.get_current_interval_type())) 

        if autostart and sender != "startup":
            first_button = self.pause_button
        else:
            first_button = self.start_button

        # set the first button to either Start or Pause
        try: 
            self.swap_menu_item(self.start_button, first_button)
        except: 
            pass
        try: 
            self.swap_menu_item(self.pause_button, first_button)
        except:
            pass
        try:
            self.swap_menu_item(self.continue_button, first_button)
        except: 
            pass

        # update the menu buttons
        self.update_menu()
        # update the session info
        self.update_session_info()
        # update todays stats
        self.load_stats(sender=sender)

        if autostart and sender != "startup":
            self.start_timer(sender="")
    
    def swap_menu_item(self, original_item, new_item):
        """swaps a MenuItem with another MenuItem in the menu

        Args:
            original_item (rumps.rumps.MenuItem): the item that will be replaced
            new_item (rumps.rumps.MenuItem): the item that will take the original_item place
        """
        original_item.title = original_item.title.split()[0]
        new_item.title = new_item.title.split()[0]
        self.app.menu.insert_after(original_item.title, new_item)
        self.app.menu.pop(original_item.title)
        self.update_menu()

    def update_menu(self):
        """updates timer buttons (Start, Pause, Continue, Skip, Reset, Stop) with correct interval types (Pomodoro, Break, Long Break)
        """
        current_interval = self.get_current_interval_type().capitalize()
        if current_interval == "Long":
            current_interval = "Long Break"
        self.start_button.title = "Start {}".format(current_interval)
        self.pause_button.title = "Pause {}".format(current_interval)
        self.continue_button.title = "Continue {}".format(current_interval)
        self.skip_button.title = "Skip {}".format(current_interval)
        self.reset_button.title = "Reset {}".format(current_interval)

    ## SESSION
    # returns the current interval TYPE from current_session dict
    def get_current_interval_type(self, full_text=False):
        """returns the currently loaded interval type (pomodoro, break, long) of the current_session

        Args:
            full_text (bool, optional): If true, a string meant for the user will be returned. Defaults to False.

        Returns:
            string: type of loaded
             interval 
        """
        # loop through the session, getting the interval key and the bool value
        for interval, value in self.session_current.items():
            # if the bool is False aka the interval has not been completed
            if isinstance(value, bool):
                # return the first word of interval key (pomodoro/break/long)
                if full_text is True:
                    if interval.split("_")[0] == "long":
                        return "Long Break"
                    else:
                        return interval.split("_")[0].capitalize()
                else:
                    return interval.split("_")[0]
        # when the loop concludes without returning the function, it means there is no interval left in the session - return False
        return False

    def get_current_interval(self):
        """returns currently loaded specific (indexed) interval of current_session

        Returns:
            string: indexed interval (type_i)
        """
        # loop through the session, getting the interval key and the bool value
        for interval, value in self.session_current.items():
            # if the bool is False aka the interval has not been completed
            if isinstance(value, bool):
                # return the first word of interval key (pomodoro/break/long)
                return interval
    
    def update_session_info(self):
        """updates the session_info with correct symbols
        """
        string = ""
        # loop through the items in session
        for interval, value in self.session_current.items():
            # if the item starts with "pomodoro"
            if interval.split("_")[0] == "pomodoro":
                # if the interval is the current interval and there is time in the timer
                if interval == self.get_current_interval() and self.timer.is_alive() is True:
                    # add the half-full clock
                    string += self.config.get("clock_half")
                # if the interval has a value type bool, aka it has not been started yet
                elif type(value) == bool:
                    # add the empty clock
                    string += self.config.get("clock_empty")
                # else the value has alredy been assigned an int aka it has passed already
                else:
                    # add the full clock
                    string += self.config.get("clock_full")
        # set the title of the session info to the string
        self.session_info.title = "Session: {}".format(string)

    def load_session(self):
        """loads a new session from self.session_general
        """
        for c, interval in enumerate(self.session_general):
            self.session_current["{}_{}".format(interval, c)] = False

    def end_session(self, sender):
        """ends the current session, saving the current interval and loading the new session

        Args:
            sender (string, MenuItem): information on the sender
        """
        if isinstance(sender, rumps.MenuItem):
            button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
        # stop the timer
        self.timer.stop()
        # if the sender is not the loaded_state function
        if sender != "loaded_state":
            # save interval
            self.save_interval(self.get_current_interval_type(), self.timer.count - 1)

        self.session_current.clear()
        self.load_session()

        # load the next interval
        if sender != "loaded_state":
            self.load_timer("end_session")
        # load todays stats from data
        self.load_stats(sender="")
    
    ## PROJECTS
    def _update_project_label(self):
        current = self.prefs.get("current_project", "")
        self.project_button.title = "● {}".format(current) if current else "○ No Project"

    def _rebuild_project_menu(self):
        for key in list(self.project_button.keys()):
            self.project_button.pop(key)
        current = self.prefs.get("current_project", "")
        no_proj = rumps.MenuItem("No Project", callback=self.no_project)
        no_proj.state = int(not current)
        items = [no_proj]
        for name in self.prefs.get("projects", []):
            proj_item = rumps.MenuItem(name)
            proj_item.state = int(name == current)
            sel = rumps.MenuItem("Select", callback=self.select_project)
            sel.project_name = name
            ren = rumps.MenuItem("Rename…", callback=self.rename_project)
            ren.project_name = name
            dlt = rumps.MenuItem("Delete", callback=self.delete_project)
            dlt.project_name = name
            proj_item.update([sel, ren, dlt])
            items.append(proj_item)
        items.append(rumps.MenuItem("+ New Project…", callback=self.new_project))
        self.project_button.update(items)
        self._update_project_label()

    def select_project(self, sender):
        self.prefs["current_project"] = sender.project_name
        save_file(self.prefs_path, self.prefs)
        self._rebuild_project_menu()
        self.load_stats(sender="")

    def no_project(self, sender):
        self.prefs["current_project"] = ""
        save_file(self.prefs_path, self.prefs)
        self._rebuild_project_menu()
        self.load_stats(sender="")

    def new_project(self, sender):
        window = rumps.Window("Project name:", "+ New Project", default_text="")
        response = window.run()
        if not response.clicked:
            return
        name = response.text.strip()
        if not name or name in self.prefs.get("projects", []):
            return
        self.prefs.setdefault("projects", []).append(name)
        self.prefs["current_project"] = name
        save_file(self.prefs_path, self.prefs)
        self._rebuild_project_menu()
        self.load_stats(sender="")

    def rename_project(self, sender):
        old_name = sender.project_name
        window = rumps.Window("New name:", "Rename Project", default_text=old_name)
        response = window.run()
        if not response.clicked:
            return
        new_name = response.text.strip()
        if not new_name or new_name == old_name or new_name in self.prefs.get("projects", []):
            return
        projects = self.prefs.get("projects", [])
        projects[projects.index(old_name)] = new_name
        if self.prefs.get("current_project") == old_name:
            self.prefs["current_project"] = new_name
        save_file(self.prefs_path, self.prefs)
        self._rebuild_project_menu()
        self.load_stats(sender="")

    def delete_project(self, sender):
        name = sender.project_name
        projects = self.prefs.get("projects", [])
        if name in projects:
            projects.remove(name)
        if self.prefs.get("current_project") == name:
            self.prefs["current_project"] = ""
        save_file(self.prefs_path, self.prefs)
        self._rebuild_project_menu()
        self.load_stats(sender="")

    ## STATS
    def save_interval(self, save_interval, save_length):
        """saves a just ended interval to the stats file, if it has a length of at least 1

        Args:
            save_interval (string): type of interval
            save_length (int): length of interval in seconds

        Returns:
            bool: True if interval was saved
        """
        if not save_length or save_length <= 0:
            return False
        append_interval(
            self.stats_path,
            save_interval,
            self.interval_start or datetime.now().isoformat(timespec='seconds'),
            save_length,
            self.prefs.get("current_project", ""),
        )
        return True

    def load_stats(self, sender):
        """loads stats from stats file and displays them in the menu (daily and weekly)

        Args:
            sender (string, MenuItem): information on the sender
        """
        stats = read_stats(self.stats_path)
        s = compute_stats(stats, date.today())

        self.stats_today_pomodoros.title = "{}   {}".format(s["today"]["pomodoros"], secs_to_time(s["today"]["pomodoro_time"], hours=True))
        self.stats_today_breaks.title = "{}   {}".format(s["today"]["breaks"], secs_to_time(s["today"]["break_time"], hours=True))
        self.stats_week_pomodoros.title = "{}   {}".format(s["week"]["pomodoros"], secs_to_time(s["week"]["pomodoro_time"], hours=True))
        self.stats_week_breaks.title = "{}   {}".format(s["week"]["breaks"], secs_to_time(s["week"]["break_time"], hours=True))

        self.stats_all_time_pomodoros.title = "{}   {}".format(s["all_time"]["pomodoros"], secs_to_time(s["all_time"]["pomodoro_time"], hours=True))
        self.stats_all_time_breaks.title = "{}   {}".format(s["all_time"]["breaks"], secs_to_time(s["all_time"]["break_time"], hours=True))

        current = self.prefs.get("current_project", "")
        self._update_stats_project_line(self.stats_today_project, s["today"], current)
        self._update_stats_project_line(self.stats_week_project, s["week"], current)
        self._update_stats_project_line(self.stats_all_time_project, s["all_time"], current)
        self._rebuild_by_project_submenu(self.stats_today_by_project, s["today"]["by_project"])
        self._rebuild_by_project_submenu(self.stats_week_by_project, s["week"]["by_project"])
        self._rebuild_by_project_submenu(self.stats_all_time_by_project, s["all_time"]["by_project"])

    def _update_stats_project_line(self, item, period_stats, current_project):
        if current_project:
            pd = period_stats["by_project"].get(current_project, {})
            pomodoros = pd.get("pomodoros", 0)
            ptime = pd.get("pomodoro_time", 0)
            item.title = "● {}: {} 🍅  {}".format(current_project, pomodoros, secs_to_time(ptime, hours=True))
        else:
            item.title = "○ No active project"

    def _rebuild_by_project_submenu(self, submenu_item, by_project_data):
        for key in list(submenu_item.keys()):
            submenu_item.pop(key)
        if not by_project_data:
            submenu_item.update([rumps.MenuItem("No data", callback=self.not_clickable_notification)])
            return
        max_len = max(len(p) for p in by_project_data)
        items = []
        for project, data in by_project_data.items():
            label = "{:<{}}  🍅 {:>2}   {}".format(project, max_len, data["pomodoros"], secs_to_time(data["pomodoro_time"], hours=True))
            items.append(rumps.MenuItem(label, callback=self.not_clickable_notification))
        submenu_item.update(items)

    def export_stats(self, sender):
        stats = read_stats(self.stats_path)
        if not stats:
            rumps.alert("No Stats", "Nothing to export yet.")
            return
        filename = "tomado-stats-{}.csv".format(date.today().isoformat())
        export_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
        with open(export_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "time", "type", "duration_seconds", "duration_minutes", "project"])
            for record in stats:
                try:
                    dt = datetime.fromisoformat(record["start"])
                except (KeyError, ValueError):
                    continue
                duration = record.get("duration", 0)
                writer.writerow([
                    dt.date().isoformat(),
                    dt.strftime("%H:%M:%S"),
                    record.get("type", ""),
                    duration,
                    round(duration / 60, 2),
                    record.get("project", ""),
                ])
        rumps.alert("Exported", "Saved to Desktop/{}".format(filename))

    def clear_stats(self, sender):
        response = rumps.alert(
            title="Clear Stats",
            message="Permanently delete all tracked intervals?",
            ok="Clear",
            cancel="Cancel",
        )
        if response == 1:
            save_file(self.stats_path, [])
            self.load_stats(sender="")

    ## PREFERENCES
    def startup_display_preferences(self):
        """displays correct preferences (from prefs file) on start up
        """
        # AUTOSTART
        self.autostart_pomodoro_button.state = int(bool(self.prefs.get("autostart_pomodoro")))
        self.autostart_break_button.state = int(bool(self.prefs.get("autostart_break")))
        self.autostart_session_button.state = int(bool(self.prefs.get("autostart_session")))
        # INTERVAL LENGHTS
        # loop through a list of the lists of options
        option_lists = [self.pomodoro_length_options, self.break_length_options, self.long_length_options]
        for options in option_lists:
            for option in options:
                # if the first word (number) of the button title is the same as the number in preferences
                if int(option.title.split()[0]) * 60 == self.prefs.get("{}_length".format(option.type)):
                    # make the button active
                    option.state = 1
        # SOUND TOGGLE
        self.allow_sounds_button.state = int(bool(self.prefs.get("allow_sound")))
        # SOUND VOLUME
        for option in self.sound_volume_options:
            if int(option.title.strip("%"))/100 == self.prefs.get("sound_volume"):
                option.state = 1
                break
        # SOUND SELECT
        for option in self.sound_options:
            # if the title of the button is the same as the file in preferences
            if "sounds/" + option.title.lower() + ".mp3" == self.prefs.get("timer_sound"):
                # make the button active
                option.state = 1
                break
    def autostart_toggle(self, sender):
        """toggles the autostart (of Pomodoros or Breaks) and saves it to the preferences file

        Args:
            sender (string, MenuItem): information on the sender
        """
        #change the preferences value to the other bool
        self.prefs["autostart_{}".format(sender.type)] = not self.prefs["autostart_{}".format(sender.type)]
        #change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        save_file(self.prefs_path, self.prefs)

    def change_length(self, sender):
        """changes the length of an interval (Pomodoro, Break, Long Break) and saves it to the preferences file

        Args:
            sender (string, MenuItem): information on the sender
        """
        # change the interval length value in prefs
        self.prefs["{}_length".format(sender.type)] = int(sender.title.split()[0]) * 60
        
        options = {
            "pomodoro": self.pomodoro_length_options,
            "break": self.break_length_options,
            "long": self.long_length_options,
        }[sender.type]
        # loop through the options
        for option in options:
            # make them inactive
            option.state = 0
        # make the state of the sender active
        sender.state = 1

        # if there isnt an active interval
        if self.timer.count == 0:
            #set the menu bar timer text to the new length
            self.app.title = secs_to_time(self.prefs.get("{}_length".format(self.get_current_interval_type())))

        save_file(self.prefs_path, self.prefs)

    ## SOUNDS
    def sounds_toggle(self, sender):
        """toggles (on/off) sounds of the app

        Args:
            sender (string, MenuItem): the sender button
        """
        # change the preferences value to the other bool
        self.prefs["allow_sound"] = not self.prefs["allow_sound"]
        # change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        save_file(self.prefs_path, self.prefs)

    def change_volume(self, sender):
        """changes the sound volume in prefs and updates the menu

        Args:
            sender (string, MenuItem): the sender button
        """
        temp = str(int(self.prefs["sound_volume"] * 100)) + "%"
        self.prefs["sound_volume"] = int(sender.title.strip("%"))/100
        for option in self.sound_volume_options:
            if option.title == temp:
                option.state = 0
                break
        sender.state = 1
        save_file(self.prefs_path, self.prefs)
        self.notification_playback.setVolume_(self.prefs.get("sound_volume"))

    def change_sound(self, sender):
        """changes the sound that notifies the user at the end of the interval in prefs

        Args:
            sender (string, MenuItem): the sender button
        """
        temp = self.prefs["timer_sound"][7:][:-4].capitalize()
        self.prefs["timer_sound"] = "sounds/" + sender.title.lower() + ".mp3"
        for sound in self.sound_options:
            if sound.title == temp:
                sound.state = 0
                break
        sender.state = 1
        save_file(self.prefs_path, self.prefs)
        del self.notification_playback
        self.notification_playback = load_sound(self.prefs.get("timer_sound"))
        self.notification_playback.setVolume_(self.prefs.get("sound_volume"))
    
    ## NOTIFICATIONS
    def interval_notification(self, type):
        """notifies the user when interval ends, depending on the type

        Args:
            type (string): interval type pomodoro/break/long
        """
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["{}_message".format(type)],
                sound=False)
        if self.prefs.get("allow_sound"):
            self.notification_playback.play()

    def not_clickable_notification(self, sender=None):
        """notidies the user when a non clickable MenuItem is pressed
        """
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["not_clickable_message"],
                sound=False)

    ## TIMER
    def tick(self, sender):
        """triggeres every second, moves the timer

        Args:
            sender (string, MenuItem): information on the sender
        """
        # add one to the counter
        sender.count += 1
        # calculate the remaining time from the counter and the end
        time_left = sender.end - sender.count
        # the menu bar title gets changed to the remaining time coverted by a function
        self.app.title = secs_to_time(time_left+1)
        self.app.icon = self.config.get("{}_symbol".format(self.get_current_interval_type()))
        # if there is no remaining time
        if time_left < 0:
            # stop the timer
            self.stop_timer()

    def start_timer(self, sender):
        """starts the interval

        Args:
            sender (string, MenuItem): information on the sender
        """
        # check if the function is being triggered by a button
        if isinstance(sender, rumps.MenuItem):
            button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
            # replace the start button to the pause button
            self.swap_menu_item(self.start_button, self.pause_button)
        # define the timer length from preferences
        self.timer.end = self.prefs.get("{}_length".format(self.get_current_interval_type()))
        # start the timer
        self.timer.start()
        self.update_session_info()

        self.interval_start = datetime.now().isoformat(timespec='seconds')
    
    def stop_timer(self):
        """stops the loaded interval
        """
        # stop the timer
        self.timer.stop()
        self.timer.end = 0
        # notify the user according to the current timer type
        self.interval_notification(self.get_current_interval_type())
        # save interval
        self.save_interval(self.get_current_interval_type(), self.timer.count - 1)
        # set the just passed interval to the time it has elapsed
        self.session_current[self.get_current_interval()] = self.timer.count - 1
        # load the next interval
        self.load_timer("stop_timer")

    def pause_timer(self, sender):
        """pauses the loaded interval

        Args:
            sender (string, MenuItem): information on the sender
        """
        button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
        # stop the timer
        self.timer.stop()
        # swap the pause_button for the continue button
        self.swap_menu_item(self.pause_button, self.continue_button)

    def continue_timer(self, sender):
        """continues the loaded interval

        Args:
            sender (string, MenuItem): information on the sender
        """
        button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
        # starts the timer
        self.timer.start()
        # replaces the continue button with the pause button
        self.swap_menu_item(self.continue_button, self.pause_button)
    
    def reset_timer(self, sender):
        """resets the loaded interval

        Args:
            sender (string, MenuItem): information on the sender
        """
        button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
        # load the next interval
        self.load_timer("reset_timer")

    def skip_timer(self, sender):
        """skips the loaded interval

        Args:
            sender (string, MenuItem): information on the sender
        """
        button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
        # save interval
        self.save_interval(self.get_current_interval_type(), self.timer.count - 1)
        # if the timer has not started yet
        if self.timer.count == 0:
            self.session_current[self.get_current_interval()] = 0
        else:
            # set the just passed interval to the time it has elapsed
            self.session_current[self.get_current_interval()] = self.timer.count - 1
        # load the next interval
        self.load_timer("skip_timer")
    
    def about_info(self, sender):
        """shows info about the app

        Args:
            sender (string, MenuItem): information on the sender
        """
        rumps.alert(
            "About Tomado",
            "made with ❤️, care and patience by\nDaniel Gális — dgalis.sk"
            "\n\n{}\n2026 · AGPL-3.0".format(__version__)
        )
    
    ## APP
    def run(self):
        """runs the app
        """
        self.app.run()
    def quit(self, sender):
        """quits the app, ending the loaded session

        Args:
            sender (_type_): _description_
        """
        button_sound(self.prefs.get("allow_sound"), self.prefs.get("sound_volume"))
        self.end_session(sender="")
        rumps.quit_application(sender=None)

## RUN
if __name__ == "__main__":
    app = Tomado()
    app.run()
################################################################################
# Title:    tomado.py
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

from subprocess import call
import rumps
import json
import time

from utilities import *

# FIXME: when a session is ended and autostart_pomodoros = true, first button is Start and should be Pause

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
            "pomodoro_length_options" : ["15", "20", "25", "30", "40", "45", "60"],
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
            "pomodoro_length": 1500,
            "break_length": 300,
            "long_length": 900,
            "autostart_pomodoro": True,
            "autostart_break": True,
            "allow_sound": True,
            "timer_sound": "sounds/beep.mp3"
        }
        # path to the preferences file
        self.prefs_path = str(self.folder + "/prefs.json")
        # open prefs from file
        self.prefs = open_file(self.prefs_path)
        # if it is empty (file didnt exist), use default prefs
        if not bool(self.prefs):
            self.prefs = self.default_prefs    
        
        ## STATS
        # path to the stats file
        self.stats_path = str(self.folder + '/stats.json')
        # if stats file doesnt exist, create it
        with open(self.stats_path, "a") as f:
            pass

        ## GENERAL BUTTONS
        # non clickable button showing info about current session
        self.session_info = rumps.MenuItem("Session info", callback=self.not_clickable)
        # end session button
        self.end_session_button = rumps.MenuItem("End Session", callback=self.end_session, key="e")
        # about button
        self.about_button = rumps.MenuItem("About {}".format(self.config.get("app_name")), callback=self.about_info)
        
        # preferences button
        self.prefereces_button = rumps.MenuItem("Preferences")
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
        # autostart breakes toggle
        self.autostart_break_button = rumps.MenuItem("Autostart Breakes", callback=self.autostart_toggle)
        self.autostart_break_button.type = "break"
        # sounds toggle
        self.allow_sounds_button = rumps.MenuItem("Allow Sounds", callback=self.sounds_toggle)
        # sound preferences
        self.sound_preferences_button = rumps.MenuItem("Timer Sound")
        self.sound_options = create_submenu(self.config.get("sound_options"), self.change_sound)
        
        # stats submenus
        self.stats_today_submenu = rumps.MenuItem("Daily Stats")
        self.stats_week_submenu = rumps.MenuItem("Weekly Stats")
        # shows pomodoros tracked today / this week
        self.stats_today_pomodoros = rumps.MenuItem("Pomodoros:", callback=self.not_clickable)
        self.stats_today_pomodoros.icon = self.config.get("pomodoro_symbol")
        self.stats_week_pomodoros = rumps.MenuItem("Pomodoros:", callback=self.not_clickable)
        self.stats_week_pomodoros.icon = self.config.get("pomodoro_symbol")
        # shows breakes tracked today / this week
        self.stats_today_breakes = rumps.MenuItem("Breakes:", callback=self.not_clickable)
        self.stats_today_breakes.icon = self.config.get("break_symbol")
        self.stats_week_breakes = rumps.MenuItem("Breakes:", callback=self.not_clickable)
        self.stats_week_breakes.icon = self.config.get("break_symbol")


        ## TIMER BUTTONS
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.start_button = rumps.MenuItem("Start", callback=self.start_timer, key="s", icon="icons/start.png", template=True)
        # pause_pomodoro button is created as a rumps.MenuItem, callback is the pause_timer method
        self.pause_button = rumps.MenuItem("Pause", callback=self.pause_timer, key="s", icon="icons/pause.png", template=True)
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.continue_button = rumps.MenuItem("Continue", callback=self.continue_timer, key="s", icon="icons/start.png", template=True)
        # the skip_pomodoro button is created as a rumps.MenuItem, callback is the skip_timer method
        self.skip_button = rumps.MenuItem("Skip", callback=self.skip_timer, key="r", icon="icons/skip.png", template=True)
        # the reset_pomodoro button is created as a rumps.MenuItem, callback is the reset_timer method
        self.reset_button = rumps.MenuItem("Reset", callback=self.reset_timer, key="r", icon="icons/reset.png", template=True)

        ## MENU
        self.menus = {"default_menu" : 
                [self.start_button, 
                self.reset_button,
                self.skip_button, 
                None, 
                self.session_info,
                self.end_session_button,
                None,
                [self.stats_today_submenu, 
                    [self.stats_today_pomodoros,
                    self.stats_today_breakes]],
                [self.stats_week_submenu, 
                    [self.stats_week_pomodoros,
                    self.stats_week_breakes]],
                None,
                [self.prefereces_button, 
                    [[self.pomodoro_length_button, 
                        self.pomodoro_length_options], 
                    [self.break_length_button, 
                        self.break_length_options], 
                    [self.long_length_button, 
                        self.long_length_options],
                    None,
                    self.autostart_pomodoro_button,
                    self.autostart_break_button,
                    None,
                    self.allow_sounds_button,
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
        self.create_session()
        # set the menu to the default (first button is Start)
        self.app.menu.update(self.menus.get("default_menu"))
        # set the menu to the right interval types
        self.update_menu()
        # loaded state of timer
        self.loaded_state("startup")
        # display the right preferences (sound toggle, sound select, autostart toggles)
        self.startup_display_preferences()
    
    ## STATES AND MENUS
    # sets the app to the default menu and resets timer
    def loaded_state(self, sender):

        #stop the current timer
        self.timer.stop()
        #reset the current timer
        self.timer.count = 0

        autostart = False
        if self.prefs.get("autostart_pomodoro") == True and self.get_current_interval_type() == "pomodoro":
            autostart = True
        if self.prefs.get("autostart_break") == True and self.get_current_interval_type() == "break":
            autostart = True
        if self.prefs.get("autostart_break") == True and self.get_current_interval_type() == "long":
            autostart = True

        # variable representing whether a new session has been started
        new_session = False
        # check wheter the session is not over aka there is not a bool value in session
        if self.get_current_interval_type() == False:
            #if it is over, trigger a method for ending a session
            self.end_session(sender="loaded_state")
            #save the info about a new session starting to a variable
            new_session = True

        # change the title to the current interval
        self.app.title = secs_to_time(self.prefs.get("{}_length".format(self.get_current_interval_type())))
        self.app.icon = self.config.get("{}_symbol".format(self.get_current_interval_type())) 

        if autostart and not new_session and sender != "startup":
            first_button = self.pause_button
        else:
            first_button = self.start_button

        # set the first button to either Start or Pause
        try :self.swap_menu_item(self.start_button, first_button)
        except: pass
        try: self.swap_menu_item(self.pause_button, first_button)
        except: pass
        try: self.swap_menu_item(self.continue_button, first_button)
        except: pass

        # update the menu buttons
        self.update_menu()
        # update the session info
        self.update_session_info()
        # update todays stats
        self.load_stats(sender=sender)

        if autostart and not new_session and sender != "startup":
            self.start_timer(sender="")
    
    # replaces a MenuItem with another MenuItem
    def swap_menu_item(self, original_item, new_item):
        original_item.title = original_item.title.split()[0]
        new_item.title = new_item.title.split()[0]
        self.app.menu.insert_after(original_item.title, new_item)
        self.app.menu.pop(original_item.title)
        self.update_menu()

    # updates timer control button titles with correct interval types
    def update_menu(self):
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
        # loop through the session, getting the interval key and the bool value
        for interval, value in self.session_current.items():
            # if the bool is False aka the interval has not been completed
            if type(value) == bool:
                # return the first word of interval key (pomodoro/break/long)
                if full_text == True:
                    if interval.split("_")[0] == "long":
                        return "Long Break"
                    else:
                        return interval.split("_")[0].capitalize()
                else:
                    return interval.split("_")[0]
        # when the loop concludes without returning the function, it means there is no interval left in the session - return False
        return False

    # returns current SPECIFIC interval from current_session dict
    def get_current_interval(self):
        # loop through the session, getting the interval key and the bool value
        for interval, value in self.session_current.items():
            # if the bool is False aka the interval has not been completed
            if type(value) == bool:
                # return the first word of interval key (pomodoro/break/long)
                return interval
    
    # updates the session info
    def update_session_info(self):
        string = ""
        # loop through the items in session
        for interval, value in self.session_current.items():
            # if the item starts with "pomodoro"
            if interval.split("_")[0] == "pomodoro":
                # if the interval is the current interval and there is time in the timer
                if interval == self.get_current_interval() and self.timer.is_alive() == True:
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

    # creates a new session from self.session_general
    def create_session(self):
        for c, interval in enumerate(self.session_general):
            self.session_current["{}_{}".format(interval, c)] = False

    # ends and saves current session
    def end_session(self, sender):
        if type(sender) == rumps.rumps.MenuItem:
            button_sound(self.prefs.get("allow_sound"))
        # stop the timer
        self.timer.stop()
        # save interval
        self.save_interval(self.get_current_interval_type(), self.timer.count - 1)

        # open the data dictionary from json
        with open(self.stats_path) as f:
            try: stats = json.load(f)
            except: stats = {}

        # adds end time to current session
        current_week = time.strftime("%Y_%W", time.localtime(time.time()))
        current_date = time.strftime("%m.%d%.", time.localtime(time.time()))
        current_time = time.strftime("%H:%M%:%S", time.localtime(time.time()))

        for week, sessions in stats.items():
            if week == current_week:
                for session, intervals in sessions.items():
                    if "-" not in session:
                        sessions_update = {
                            "{}-{}_{}".format(session, current_date, current_time) : intervals
                        }
                        sessions.update(sessions_update)
                        break
                sessions.pop(session)
        
        save_file(self.stats_path, stats)

        self.session_current.clear()
        self.create_session()

        # load the next interval
        self.loaded_state("end_session")
        # load todays stats from data
        self.load_stats(sender="")
    
    ## STATS
    # saves a just ended interval to stats file, if it has a length of atleast 1
    def save_interval(self, save_interval, save_length):
        if save_length <= 0 or not save_length or save_length == None:
            return False

        stats = open_file(self.stats_path)
        
        current_week = time.strftime("%Y_%W", time.localtime(time.time()))
        current_date = time.strftime("%m.%d%.", time.localtime(time.time()))
        current_time = time.strftime("%H:%M%:%S", time.localtime(time.time()))

        for week, sessions in stats.items():
            if week == current_week:
                for session, intervals in sessions.items():
                    if "-" not in session: # session has not ended yet
                        intervals_update = {
                            "{}_{}_{}".format(save_interval, current_date, current_time) : save_length
                        }
                        intervals.update(intervals_update)
                        save_file(self.stats_path, stats)
                        return True # saved interval into current session
                sessions_update = {
                    "{}_{}".format(current_date, current_time) : {
                        "{}_{}_{}".format(save_interval, current_date, current_time) : save_length
                        }
                }
                sessions.update(sessions_update)
                save_file(self.stats_path, stats)
                return True # created new session and save interval
        # if stats is empty or there isnt current_week yet
        stats_update = {
            "{}".format(current_week) : {
                "{}_{}".format(current_date, current_time) : {
                    "{}_{}_{}".format(save_interval, current_date, current_time) : save_length
                }
            }
        }
        stats.update(stats_update)
        save_file(self.stats_path, stats)
        return True # created new week, new session and saved interval

    # loads stats from stats file and displays them in the menu
    def load_stats(self, sender):
        # daily stat vars
        today_pomodoros = 0
        today_pomodoros_time = 0
        today_breakes = 0
        today_breakes_time = 0
        # weekly stat vars
        week_pomodoros = 0
        week_pomodoros_time = 0
        week_breakes = 0
        week_breakes_time = 0
        
        stats = open_file(self.stats_path)

        current_week = time.strftime("%Y_%W", time.localtime(time.time()))
        current_date = time.strftime("%m.%d%.", time.localtime(time.time()))

        for week, sessions in stats.items():
            if week == current_week:
                for session, intervals in sessions.items():
                    # get weekly stats
                    for interval, length in intervals.items():
                        if interval.split("_")[0] == "pomodoro":
                            week_pomodoros_time += length
                            week_pomodoros += 1
                        else:
                            week_breakes_time += length
                            week_breakes += 1
                    # get daily stats
                    # if start_time of unfinished, start_time of finished, or end_time of finished sessions is today
                    if session.split("_")[0] == current_date or session.split("-")[1].split("_")[0] == current_date or session.split("-")[1].split("_")[0] == current_date:
                        for interval, length in intervals.items():
                            if interval.split("_")[1] == current_date:
                                if interval.split("_")[0] == "pomodoro":
                                    today_pomodoros_time += length
                                    today_pomodoros += 1
                                else:
                                    today_breakes_time += length
                                    today_breakes += 1
        # update the submenus
        self.stats_today_pomodoros.title = "{} Pomodoros = {}".format(today_pomodoros, secs_to_time(today_pomodoros_time, hours=True))
        self.stats_today_breakes.title = "{} Breakes = {}".format(today_breakes, secs_to_time(today_breakes_time, hours=True))
        self.stats_week_pomodoros.title = "{} Pomodoros = {}".format(week_pomodoros, secs_to_time(week_pomodoros_time, hours=True))
        self.stats_week_breakes.title = "{} Breakes = {}".format(week_breakes, secs_to_time(week_breakes_time, hours=True))

    ## PREFERENCES
    # method to display correct preferences on start up
    def startup_display_preferences(self):
        # AUTOSTART
        if self.prefs.get("autostart_pomodoro"):
            self.autostart_pomodoro_button.state = 1
        else:
            self.autostart_pomodoro_button.state = 0
        if self.prefs.get("autostart_break"):
            self.autostart_break_button.state = 1
        else:
            self.autostart_break_button.state = 0
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
        if self.prefs.get("allow_sound"):
            self.allow_sounds_button.state = 1
        else:
            self.allow_sounds_button.state = 0
        # SOUND SELECT
        for option in self.sound_options:
            # if the title of the button is the same as the file in preferences
            if "sounds/" + option.title.lower() + ".mp3" == self.prefs.get("timer_sound"):
                # make the button active
                option.state = 1
    
    # toggles autostart
    def autostart_toggle(self, sender):
        #change the preferences value to the other bool
        self.prefs["autostart_{}".format(sender.type)] = not self.prefs["autostart_{}".format(sender.type)]
        #change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        save_file(self.prefs_path, self.prefs)

    # changes the length of an interval
    def change_length(self, sender):
        # change the interval length value in prefs
        self.prefs["{}_length".format(sender.type)] = int(sender.title.split()[0]) * 60
        
        # get the type of interval and select the matching list of option buttons
        if sender.type == "pomodoro":
            options = self.pomodoro_length_options
        if sender.type == "break":
            options = self.break_length_options
        if sender.type == "long":
            options = self.long_length_options
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
    # change the timer sound
    def change_sound(self, sender):
        self.prefs["timer_sound"] = "sounds/" + sender.title.lower() + ".mp3"
        sender.state = 1
        for sound in self.sound_options:
            if sound.title != sender.title:
                sound.state = 0
        save_file(self.prefs_path, self.prefs)

    # toggle sounds
    def sounds_toggle(self, sender):
        # change the preferences value to the other bool
        self.prefs["allow_sound"] = not self.prefs["allow_sound"]
        # change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        save_file(self.prefs_path, self.prefs)
    
    ## NOTIFICATIONS
    # interval notification
    def notification(self, type):
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["{}_message".format(type)],
                sound=False)
        if self.prefs.get("allow_sound"):
            playsound(self.prefs.get("timer_sound"))

    # not clickable notification
    def not_clickable_notification(self):
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["not_clickable_message"],
                sound=False)

    ## TIMER
    # triggered every second
    def tick(self, sender):
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

    # starts the timer (also button triggered)
    def start_timer(self, sender):
        # check if the function is being triggered by a button
        if type(sender) == rumps.rumps.MenuItem:
            button_sound(self.prefs.get("allow_sound"))
            # replace the start button to the pause button
            self.swap_menu_item(self.start_button, self.pause_button)
        # define the timer length from preferences
        self.timer.end = self.prefs.get("{}_length".format(self.get_current_interval_type()))
        # start the timer
        self.timer.start()
        self.update_session_info()
    
    # stops the timer
    def stop_timer(self):
        # stop the timer
        self.timer.stop()
        self.timer.end = 0
        # notify the user according to the current timer type
        self.notification(self.get_current_interval_type())
        # save interval
        self.save_interval(self.get_current_interval_type(), self.timer.count - 1)
        # set the just passed interval to the time it has elapsed
        self.session_current[self.get_current_interval()] = self.timer.count - 1
        # load the next interval
        self.loaded_state("stop_timer")

    # pauses the interval
    def pause_timer(self, sender):
        button_sound(self.prefs.get("allow_sound"))
        # stop the timer
        self.timer.stop()
        # swap the pause_button for the continue button
        self.swap_menu_item(self.pause_button, self.continue_button)

    # continues the interval
    def continue_timer(self, sender):
        button_sound(self.prefs.get("allow_sound"))
        # starts the timer
        self.timer.start()
        # replaces the continue button with the pause button
        self.swap_menu_item(self.continue_button, self.pause_button)
    
    # resets the interval
    def reset_timer(self, sender):
        button_sound(self.prefs.get("allow_sound"))
        # load the next interval
        self.loaded_state("reset_timer")

    # skips the interval
    def skip_timer(self, sender):
        button_sound(self.prefs.get("allow_sound"))
        # save interval
        self.save_interval(self.get_current_interval_type(), self.timer.count - 1)
        # if the timer has not started yet
        if self.timer.count == 0:
            self.session_current[self.get_current_interval()] = 0
        else:
            # set the just passed interval to the time it has elapsed
            self.session_current[self.get_current_interval()] = self.timer.count - 1
        # load the next interval
        self.loaded_state("skip_timer")
    
    # shows info about the app
    def about_info(self, sender):
        rumps.alert("About Tomado", "made with ❤️, care and patience by Daniel Gális \ndanielgalis.com \n\npart of self.governance(software)\n\n2022\nGPL-3.0 License")

    # not clickable
    def not_clickable(self, sender):
        self.not_clickable_notification()
    
    ## APP
    # runs this app
    def run(self):
        self.app.run()
    # quits this app
    def quit(self, sender):
        self.end_session(sender="")
        rumps.quit_application(sender=None)

## RUN
if __name__ == "__main__":
    app = Tomado()
    app.run()
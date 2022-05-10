## HEADER
# FIXME: rework stats system

from subprocess import call
import rumps
import json
import time

from utilities import *


class Tomado(object):
    ## UTILITIES
    def create_submenu(self, button_list, callback, type=""):
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
            button = rumps.MenuItem("{} Minutes".format(n), callback=callback)
            button.type = type
            submenu.append(button)
        return submenu

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
        # if it exists, load prefs from the json in prefs_path
        try: 
            with open(self.prefs_path, "r") as f:
                self.prefs = json.load(f)
        # if there is no file, load the default prefs 
        except:
            self.prefs = self.default_prefs    
        
        ## STATS
        # path to the stats file
        self.stats_path = str(self.folder + '/stats.json')
        # if it exists, load stats from the json in stats_path
        with open(self.stats_path, "a") as data:
            pass
        # create stats variables
        self.pomodoros_today = 0
        self.pomodoro_time_today = 0
        self.breakes_today = 0
        self.breakes_time_today = 0

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
        self.pomodoro_length_options = self.create_submenu(self.config.get("pomodoro_length_options"), self.change_length, "pomodoro")
        # break length preference
        self.break_length_button = rumps.MenuItem("Short Break Length")
        self.break_length_options = self.create_submenu(self.config.get("break_length_options"), self.change_length, "break")
        # long break length preference
        self.long_length_button = rumps.MenuItem("Long Break Length")
        self.long_length_options = self.create_submenu(self.config.get("long_length_options"), self.change_length, "long")
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
        self.sound_options = self.create_submenu(self.config.get("sound_options"), self.change_sound)
        
        # stats today submenu
        self.today_stats_submenu = rumps.MenuItem("Today's Stats")
        # shows pomodoros tracked today
        self.stats_today_pomodoros = rumps.MenuItem("Pomodoros:", callback=self.not_clickable)
        self.stats_today_pomodoros.icon = self.config.get("pomodoro_symbol")
        # shows breakes tracked today
        self.stats_today_breakes = rumps.MenuItem("Breakes:", callback=self.not_clickable)
        self.stats_today_breakes.icon = self.config.get("break_symbol")

        # create a session from the session_general
        self.create_session()

        ## TIMER BUTTONS
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.start_button = rumps.MenuItem("Start {}".format(self.get_current_interval_type(full_text=True)), callback=self.start_timer, key="s", icon="icons/start.png", template=True)
        # pause_pomodoro button is created as a rumps.MenuItem, callback is the pause_timer method
        self.pause_button = rumps.MenuItem("Pause {}".format(self.get_current_interval_type(full_text=True)), callback=self.pause_timer, key="s", icon="icons/pause.png", template=True)
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.continue_button = rumps.MenuItem("Continue {}".format(self.get_current_interval_type(full_text=True)), callback=self.continue_timer, key="s", icon="icons/start.png", template=True)
        # the skip_pomodoro button is created as a rumps.MenuItem, callback is the skip_timer method
        self.skip_button = rumps.MenuItem("Skip {}".format(self.get_current_interval_type(full_text=True)), callback=self.skip_timer, key="r", icon="icons/skip.png", template=True)
        # the reset_pomodoro button is created as a rumps.MenuItem, callback is the reset_timer method
        self.reset_button = rumps.MenuItem("Reset {}".format(self.get_current_interval_type(full_text=True)), callback=self.reset_timer, key="r", icon="icons/reset.png", template=True)

        ## MENUS
        self.menus = {"default_menu" : 
                [self.start_button, 
                self.reset_button,
                self.skip_button, 
                None, 
                self.session_info,
                self.end_session_button,
                None,
                [self.today_stats_submenu, 
                    [self.stats_today_pomodoros,
                    self.stats_today_breakes]],
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
        # set the menu to the default
        self.app.menu.update(self.menus.get("default_menu"))
        # load todays stats from data
        self.load_today_stats(sender="")
        # loaded state of timer
        self.loaded_state()
        # display the right preferences (sound toggle, sound select, autostart toggles)
        self.startup_display_preferences()

        #FIXME TESTING
        self.save_interval("pomdoro", 10)
    
    ## STATES AND MENUS
    # sets the app to the default menu and resets timer
    def loaded_state(self):

        #stop the current timer
        self.timer.stop()
        #reset the current timer
        self.timer.count = 0

        # variable representing whether a new session has been started
        new_session = False
        # check wheter the session is not over aka there is not a bool value in session
        if self.get_current_interval_type() == False:
            #if it is over, trigger a method for ending a session
            self.end_session(sender="loaded")
            #save the info about a new session starting to a variable
            new_session = True

        # change the title to the current interval
        self.app.title = secs_to_time(self.prefs.get("{}_length".format(self.get_current_interval_type())))
        self.app.icon = self.config.get("{}_symbol".format(self.get_current_interval_type())) 

        # update the menu buttons
        self.update_menu()
        # update the session info
        self.update_session_info()
        # update todays stats
        self.update_today_stats(sender="")

        # return variable representing info about whether a new session has been started
        return new_session
    
    # replaces a MenuItem with another MenuItem
    def swap_menu_item(self, original_item, new_item):
        self.app.menu.insert_after(original_item.title, new_item)
        self.app.menu.pop(original_item.title)
        self.update_menu()

    # updates timer control button titles with correct interval types
    def update_menu(self):
        self.start_button.title = "Start {}".format(self.get_current_interval_type(full_text=True))
        self.pause_button.title = "Pause {}".format(self.get_current_interval_type(full_text=True))
        self.continue_button.title = "Continue {}".format(self.get_current_interval_type(full_text=True))
        self.skip_button.title = "Skip {}".format(self.get_current_interval_type(full_text=True))
        self.reset_button.title = "Reset {}".format(self.get_current_interval_type(full_text=True))

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
        # stop the timer
        self.timer.stop()
        # if the timer hasnt been started
        if self.timer.count == 0 and self.get_current_interval() != None:
            self.session_current[self.get_current_interval()] = 0
        elif self.get_current_interval() != None:
            # set the just passed interval to the time it has elapsed
            self.session_current[self.get_current_interval()] = self.timer.count - 1
            #TODO: save interval

        # loop through the session
        for interval, value in self.session_current.items():
            # if an interval still hasnt been started
            if type(value) == bool:
                #set its value to 0
                self.session_current[interval] = 0
                #TODO dont save 0 length intervals

        # open the data dictionary from json
        with open(self.stats_path) as f:
            try: data = json.load(f)
            except: data = {}

        #TODO today -> this week
        # if a key for today has already been created
        if time.strftime("%Y_%m_%d",time.localtime(time.time())) in data.keys():
            # insert the current session as value with key of date and time
            data[time.strftime("%Y_%m_%d",time.localtime(time.time()))][time.strftime("%Y_%m_%d_%H:%M:%S",time.localtime(time.time()))] = self.session_current.copy()
        #TODO today -> this week
        else:
            # create a key for today
            data[time.strftime("%Y_%m_%d",time.localtime(time.time()))] = ({time.strftime("%Y_%m_%d_%H:%M:%S",time.localtime(time.time())):self.session_current.copy()})
        #TODO add end time to session
        
        # write the new data dictionary to json
        with open(self.stats_path, "w") as f:
            json.dump(data, f, indent=2)

        # load todays stats from data
        self.load_today_stats(sender="")

    
    ## STATS

    #TODO saves interval to current (not ended) session
    def save_interval(self, save_interval, save_length):
        if length == 0:
            return False

        # open up stats json into data
        with open(self.stats_path) as f:
            try: data = json.load(f)
            except: data = {}
        
        current_week = time.strftime("%Y_%W", time.localtime(time.time()))
        current_date = time.strftime("%m.%d%.", time.localtime(time.time()))
        current_time = time.strftime("%H:%M%:S%", time.localtime(time.time()))

        for week, sessions in data:
            if week == current_week:
                for session, intervals in sessions:
                    if "-" not in session: # session has not ended yet
                        intervals["{}_{}".format(save_interval, current_time)] = save_length
                    else: # there is not current session
                        sessions["{}_{}".format(current_date, current_time)] = {"{}_{}".format(save_interval, current_time) : save_length}
                        new_session = True
            else:
            create current_week
            create new_session
            new_session = True
            save the interval to new_session
        
        # save the updated stats to the json
        with open(self.stats_path, "w") as f:
            json.dump(data, f, indent=2)
        
        return new_session #if a new session has been created

    # loads todays stats from stats file
    def load_today_stats(self, sender):
        # reset the stats to zero
        self.pomodoros_today = 0
        self.pomodoro_time_today = 0
        self.breakes_today = 0
        self.breakes_time_today = 0
        with open(self.stats_path) as f:
            # try reading and unsearilizing the file
            try:
                data = json.load(f)
            # if it is empty, return this function
            except json.decoder.JSONDecodeError: return
        # try reading today data from the saved_sessions
        try:
            # from the data dict, get todays dict of sessions using todays date in the Y_M_D (2022_1_13) format as the key
            today = data[time.strftime("%Y_%m_%d",time.localtime(time.time()))]
            # loop through todays sessions without their epoch time keys
            for session in today.values():
                # in each session, loop thourgh the intervals and length they elapsed
                for interval, length in session.items():
                    # if its a pomodoro interval
                    if interval.split("_")[0] == "pomodoro" and length > 0:
                        # add one to the pomodoro counter
                        self.pomodoros_today += 1
                        # add its length to the pomodoro time counter
                        self.pomodoro_time_today += length
                    # else it is a break or long break and if it hasnt been skipped completety
                    elif length > 0:
                        # add one to the break counter
                        self.breakes_today += 1
                        # add its length to the break time counter
                        self.breakes_time_today += length    
        # except todays stats havent been created
        except KeyError: pass
        # clear the old session
        self.session_current.clear()
        # create a new session
        self.create_session()
        if sender != "loaded":
            # load the next interval into the timer
            self.loaded_state()

    # updates today's stats
    def update_today_stats(self, sender):
        # add stats from the current session
        for interval, length in self.session_current.items():
        # if its a pomodoro interval and it has already elapsed some time
            if interval.split("_")[0] == "pomodoro" and type(length) != bool:
                # add one to the pomodoro counter
                self.pomodoros_today += 1
                # add its length to the pomodoro time counter
                self.pomodoro_time_today += length
            # else it is a break or long break and it has already elapsed some time
            elif type(length) != bool:
                # add one to the break counter
                self.breakes_today += 1
                # add its length to the break time counter 
                self.breakes_time_today += length
        # pass the stats into the appropriate buttons
        self.stats_today_pomodoros.title = "{} Pomodoros = {}".format(self.pomodoros_today, secs_to_time(self.pomodoro_time_today, hours=True))
        self.stats_today_breakes.title = "{} Breakes = {}".format(self.breakes_today, secs_to_time(self.breakes_time_today, hours=True))

    ## PREFERENCES
    # save preferences to a file after change
    def save_preferences(self):
        with open(self.prefs_path, "w") as f:
            json.dump(self.prefs, f)

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
        self.save_preferences()

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
        self.save_preferences()

    ## SOUNDS
    # change the timer sound
    def change_sound(self, sender):
        self.prefs["timer_sound"] = "sounds/" + sender.title.lower() + ".mp3"
        sender.state = 1
        for sound in self.sound_options:
            if sound.title != sender.title:
                sound.state = 0
        self.save_preferences()

    # toggle sounds
    def sounds_toggle(self, sender):
        # change the preferences value to the other bool
        self.prefs["allow_sound"] = not self.prefs["allow_sound"]
        # change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        self.save_preferences()
    
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
        # define the timer length from preferences
        self.timer.end = self.prefs.get("{}_length".format(self.get_current_interval_type()))
        # start the timer
        self.timer.start()
        # replace the start button to the pause button
        self.swap_menu_item(self.start_button, self.pause_button)
        # update the session info
        self.update_session_info()
    
    # stops the timer
    def stop_timer(self):
        # stop the timer
        self.timer.stop()
        self.timer.end = 0
        # notify the user according to the current timer type
        self.notification(self.get_current_interval_type())

        # set the just passed interval to the time it has elapsed
        self.session_current[self.get_current_interval()] = self.timer.count - 1

        #TODO: save interval into stats file, into a session without end time

        # load the next interval, get info about whether a new session has been started
        new_session = self.loaded_state()
        
        # autostart if a new session hasnt been started
        if not new_session:
            if self.prefs.get("autostart_pomodoro") == True and self.get_current_interval_type() == "pomodoro":
                self.start_timer(sender="")
            if self.prefs.get("autostart_break") == True and self.get_current_interval_type() == "break":
                self.start_timer(sender="")
            if self.prefs.get("autostart_break") == True and self.get_current_interval_type() == "long":
                self.start_timer(sender="")


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
        self.loaded_state()
        # start the timer
        self.start_timer(sender="")

    # skips the interval
    def skip_timer(self, sender):
        button_sound(self.prefs.get("allow_sound"))
        # if the timer has not started yet
        if self.timer.count == 0:
            self.session_current[self.get_current_interval()] = 0
        else:
            # set the just passed interval to the time it has elapsed
            self.session_current[self.get_current_interval()] = self.timer.count - 1
        try: print("\ntest:", self.saved_sessions[time.strftime("%Y_%m_%d",time.localtime(time.time()))])
        except: pass
        # load the next interval and get info whether a new session has been started
        new_session = self.loaded_state()
        # autostart if a new session hasnt been started
        if not new_session:
            self.start_timer(sender="")
    
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
        self.end_session(sender=None)
        rumps.quit_application(sender=None)

## RUN
if __name__ == "__main__":
    app = Tomado()
    app.run()
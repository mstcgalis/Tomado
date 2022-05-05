from subprocess import call
import rumps
import json
import time
from playsound import playsound


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
            "long_message": "Session is finished. Good joob! 🌻",
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

        #TODO: this is terrible, refractor control buttons 
        ## POMODORO BUTTONS
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.start_pomodoro_button = rumps.MenuItem("Start Pomodoro", callback=self.start_timer, key="s", icon="icons/start.png", template=True)
        # pause_pomodoro button is created as a rumps.MenuItem, callback is the pause_timer method
        self.pause_pomodoro_button = rumps.MenuItem("Pause Pomodoro", callback=self.pause_timer, key="s", icon="icons/pause.png", template=True)
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.continue_pomodoro_button = rumps.MenuItem("Continue Pomodoro", callback=self.continue_timer, key="s", icon="icons/start.png", template=True)
        # the skip_pomodoro button is created as a rumps.MenuItem, callback will be reset_timer method
        self.skip_pomodoro_button = rumps.MenuItem("Skip Pomodoro", callback=self.skip_timer, key="r", icon="icons/skip.png", template=True)
        # the reset_pomodoro button is created as a rumps.MenuItem, callback will be reset_timer method
        self.reset_pomodoro_button = rumps.MenuItem("Reset Pomodoro", callback=self.reset_timer, key="r", icon="icons/reset.png", template=True)

        ## BREAK BUTTONS
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.start_break_button = rumps.MenuItem("Start Break", callback=self.start_timer, key="s", icon="icons/start.png", template=True)
        # pause_pomodoro button is created as a rumps.MenuItem, callback is the pause_timer method
        self.pause_break_button = rumps.MenuItem("Pause Break", callback=self.pause_timer, key="s", icon="icons/pause.png", template=True)
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.continue_break_button = rumps.MenuItem("Continue Break", callback=self.continue_timer, key="s", icon="icons/start.png", template=True)
        # the skip_break button is created as a rumps.MenuItem, callback will be reset_timer method
        self.skip_break_button = rumps.MenuItem("Skip Break", callback=self.skip_timer, key="r", icon="icons/skip.png", template=True)
        # the reset_break button is created as a rumps.MenuItem, callback will be reset_timer method
        self.reset_break_button = rumps.MenuItem("Reset Break", callback=self.reset_timer, key="r", icon="icons/reset.png", template=True)

        ## LONG BUTTONS
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.start_long_button = rumps.MenuItem("Start Long Break", callback=self.start_timer, key="s", icon="icons/start.png", template=True)
        # pause_pomodoro button is created as a rumps.MenuItem, callback is the pause_timer method
        self.pause_long_button = rumps.MenuItem("Pause Long Break", callback=self.pause_timer, key="s", icon="icons/pause.png", template=True)
        # start_pomodoro button is created as a rumps.MenuItem, callback is the start_timer method
        self.continue_long_button = rumps.MenuItem("Continue Long Break", callback=self.continue_timer, key="s", icon="icons/start.png", template=True)
        # the skip_break button is created as a rumps.MenuItem, callback will be reset_timer method
        self.skip_long_button = rumps.MenuItem("Skip Long Break", callback=self.skip_timer, key="r", icon="icons/skip.png", template=True)

        ## MENUS
        self.menus = {"default_menu" : 
                [self.start_pomodoro_button, 
                self.reset_pomodoro_button,
                self.skip_pomodoro_button, 
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
        # create a session from the session_general
        self.create_session()
        # set the menu to the default
        self.app.menu.update(self.menus.get("default_menu"))
        # load todays stats from data
        self.load_today_stats(sender="")
        # loaded state of timer
        self.loaded_state()

        # display the right preferences (sound toggle, sound select, autostart toggles)
        self.startup_display_preferences()
    
    ## STATES AND MENUS
    #method for setting the app to the default menu and resetting timer
    def loaded_state(self):
        #create a variable representing whether a new session has been started
        new_session = False
        #stop the current timer
        self.timer.stop()
        #reset the current timer
        self.timer.count = 0
        #check wheter the session is not over aka there is not a bool value in session
        if self.current_interval_type() == False:
            #if it is over, trigger a method for ending a session
            self.end_session(sender="loaded")
            #save the info about a new session starting to a variable
            new_session = True
            #upate stats from json
        #change the title to the current interval
        self.app.title = self.secs_to_time(self.prefs.get("{}_length".format(self.current_interval_type())))
        self.app.icon = self.config.get("{}_symbol".format(self.current_interval_type())) 
        #update the mene buttons
        self.update_menu()
        #update the session info
        self.update_session_info()
        #update todays stats
        self.update_today_stats(sender="")
        #return the variable representing info about whether a new session has been started
        return new_session
    
    #method for replacing a MenuItem with another MenuItem
    def replace_menu_item(self, original_item, new_item):
        self.app.menu.insert_after(original_item.title, new_item)
        self.app.menu.pop(original_item.title)

    #method for replacing the whole menu, the new one is from an iterable
    def update_menu(self):
        self.app.menu.pop(self.app.menu.keys()[0])
        self.app.menu.pop(self.app.menu.keys()[0])
        self.app.menu.pop(self.app.menu.keys()[0])
        if self.current_interval_type() == "pomodoro":
            self.app.menu.insert_before(self.app.menu.keys()[0], self.start_pomodoro_button)
            self.app.menu.insert_before(self.app.menu.keys()[1], self.reset_pomodoro_button)
            self.app.menu.insert_before(self.app.menu.keys()[2], self.skip_pomodoro_button)
        if self.current_interval_type() == "break":
            self.app.menu.insert_before(self.app.menu.keys()[0], self.start_break_button)
            self.app.menu.insert_before(self.app.menu.keys()[1], self.reset_break_button)
            self.app.menu.insert_before(self.app.menu.keys()[2], self.skip_break_button)
        if self.current_interval_type() == "long":
            self.app.menu.insert_before(self.app.menu.keys()[0], self.start_long_button)
            self.app.menu.insert_before(self.app.menu.keys()[1], self.reset_break_button)
            self.app.menu.insert_before(self.app.menu.keys()[2], self.skip_long_button)
    
    #method that takes an integer of seconds and returns a minutes:seconds string, or a hours:minutes:seconds string
    def secs_to_time(self, seconds, format = "minutes"):
        if format == "hours":
            hours, secs = divmod(seconds, 3600)
            mins, secs = divmod(secs, 60)
            return '{}h {:02d}m'.format(hours, mins)
        else:
            mins, secs = divmod(seconds, 60)
            return '{:02d}:{:02d}'.format(mins, secs)

    ##SESSION
    ##method for getting the current interval TYPE from session dict
    def current_interval_type(self):
        #loop through the session, getting the interval key and the bool value
        for interval, value in self.session_current.items():
            #if the bool is False aka the interval has not been completed
            if type(value) == bool:
                #return the first word of interval key (pomodoro/break/long)
                return interval.split("_")[0]
        #when the loop concludes without returning the function, it means there is no interval left in the session
        #return False
        return False

    #method for getting the current SPECIFIC interval from session dict
    def current_interval(self):
        #loop through the session, getting the interval key and the bool value
        for interval, value in self.session_current.items():
            #if the bool is False aka the interval has not been completed
            if type(value) == bool:
                #return the first word of interval key (pomodoro/break/long)
                return interval
    
    #method for updating the session info
    def update_session_info(self):
        string = ""
        #loop through the items in session
        for interval, value in self.session_current.items():
            #if the item starts with "pomodoro"
            if interval.split("_")[0] == "pomodoro":
                #if the interval is the current interval and there is time in the timer
                if interval == self.current_interval() and self.timer.is_alive() == True:
                    #add the half-full clock
                    string += self.config.get("clock_half")
                #if the interval has a value type bool, aka it has not been started yet
                elif type(value) == bool:
                    #add the empty clock
                    string += self.config.get("clock_empty")
                #else the value has alredy been assigned an int aka it has passed already
                else:
                    #add the full clock
                    string += self.config.get("clock_full")
        #set the title of the session info to the string
        self.session_info.title = "Session: {}".format(string)

    # creates a new session from self.session_general
    def create_session(self):
        for c, interval in enumerate(self.session_general):
            self.session_current["{}_{}".format(interval, c)] = False

    # method for ending and saving a session
    def end_session(self, sender):
        #stop the timer
        self.timer.stop()
        #if the timer hasnt been started
        if self.timer.count == 0 and self.current_interval() != None:
            self.session_current[self.current_interval()] = 0
        elif self.current_interval() != None:
            #set the just passed interval to the time it has elapsed
            self.session_current[self.current_interval()] = self.timer.count - 1
        #loop through the session
        for interval, value in self.session_current.items():
            #if an interval still hasnt been started
            if type(value) == bool:
                #set its value to 0
                self.session_current[interval] = 0
        #open the data disctionary from json
        with open(self.stats_path) as f:
            try: data = json.load(f)
            except: data = {}
        #if a key for today has already been created
        if time.strftime("%Y_%m_%d",time.localtime(time.time())) in data.keys():
            #insert the current session as value with key of date and time
            data[time.strftime("%Y_%m_%d",time.localtime(time.time()))][time.strftime("%Y_%m_%d_%H:%M:%S",time.localtime(time.time()))] = self.session_current.copy()
        else:
            #create a key for today
            data[time.strftime("%Y_%m_%d",time.localtime(time.time()))] = ({time.strftime("%Y_%m_%d_%H:%M:%S",time.localtime(time.time())):self.session_current.copy()})
        #write the new data dictionary to json
        with open(self.stats_path, "w") as f:
            json.dump(data, f, indent=2)

        #load todays stats from data
        self.load_today_stats(sender="")

    
    ## STATS
    # method for loading todays stats from stats file
    def load_today_stats(self, sender):
        # reset the stats to zero
        self.pomodoros_today = 0
        self.pomodoro_time_today = 0
        self.breakes_today = 0
        self.breakes_time_today = 0
        with open(self.stats_path) as f:
            #try reading and unsearilizing the file
            try:
                data = json.load(f)
            #if it is empty, return this function
            except json.decoder.JSONDecodeError: return
        try:
        #try reading today data from the saved_sessions
            #from the data dict, get todays dict of sessions using todays date in the Y_M_D (2022_1_13) format as the key
            today = data[time.strftime("%Y_%m_%d",time.localtime(time.time()))]
            #loop through todays sessions without their epoch time keys
            for session in today.values():
                #in each session, loop thourgh the intervals and length they elapsed
                for interval, length in session.items():
                    #if its a pomodoro interval
                    if interval.split("_")[0] == "pomodoro" and length > 0:
                        #add one to the pomodoro counter
                        self.pomodoros_today += 1
                        #add its length to the pomodoro time counter
                        self.pomodoro_time_today += length
                    #else it is a break or long break and if it hasnt been skipped completety
                    elif length > 0:
                        #add one to the break counter
                        self.breakes_today += 1
                        #add its length to the break time counter
                        self.breakes_time_today += length    
        #except todays stats havent been created
        except KeyError: pass

        #clear the old session
        self.session_current.clear()
        #create a new session
        self.create_session()
        if sender != "loaded":
            #load the next interval into the timer
            self.loaded_state()

    def update_today_stats(self, sender):
        #add stats from the current session
        for interval, length in self.session_current.items():
        #if its a pomodoro interval and it has already elapsed some time
            if interval.split("_")[0] == "pomodoro" and type(length) != bool:
                #add one to the pomodoro counter
                self.pomodoros_today += 1
                #add its length to the pomodoro time counter
                self.pomodoro_time_today += length
            #else it is a break or long break and it has already elapsed some time
            elif type(length) != bool:
                #add one to the break counter
                self.breakes_today += 1
                #add its length to the break time counter 
                self.breakes_time_today += length
        #pass the stats into the approapriate buttons
        self.stats_today_pomodoros.title = "{} Pomodoros = {}".format(self.pomodoros_today, self.secs_to_time(self.pomodoro_time_today, format="hours"))
        self.stats_today_breakes.title = "{} Breakes = {}".format(self.breakes_today, self.secs_to_time(self.breakes_time_today, format="hours"))

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
                print(option)
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
    
    #autostart toggle method, activated by the buttons
    def autostart_toggle(self, sender):
        #change the preferences value to the other bool
        self.prefs["autostart_{}".format(sender.type)] = not self.prefs["autostart_{}".format(sender.type)]
        #change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        self.save_preferences()

    # change the length of an interval
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
        #make the state of the sender active
        sender.state = 1
        #loop through the options
        for option in options:
            #if the option is not the sender, make it inactive
            if option.title != sender.title:
                option.state = 0
        #if there isnt an active interval
        if self.timer.count == 0:
            #set the menu bar timer to the new length
            self.app.title = self.secs_to_time(self.prefs.get("{}_length".format(self.current_interval_type())))
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

    #toggle sounds
    def sounds_toggle(self, sender):
        #change the preferences value to the other bool
        self.prefs["allow_sound"] = not self.prefs["allow_sound"]
        #change the state to the other one
        if sender.state == 0:
            sender.state = 1
        else:
            sender.state = 0
        self.save_preferences()
    
    ## NOTIFICATIONS
    # pomodoro notification
    def pomodoro_notification(self):
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["pomodoro_message"],
                sound=False)
        if self.prefs.get("allow_sound"):
            playsound(self.prefs.get("timer_sound"))
    
    # break notification
    def break_notification(self):
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["break_message"],
                sound=False)
        if self.prefs.get("allow_sound"):
            playsound(self.prefs.get("timer_sound"))

    # long break notification
    def long_notification(self):
        rumps.notification(
                title=self.config["app_name"],
                subtitle="",
                message=self.config["long_message"],
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
    # method passed in as a callback into rumps.Timer, will happen every second
    def tick(self, sender):
        #add one to the counter
        sender.count += 1
        #calculate the remaining time from the counter and the end
        time_left = sender.end - sender.count
        #the menu bar title gets changed to the remaining time coverted by a function
        self.app.title = self.secs_to_time(time_left+1)
        self.app.icon = self.config.get("{}_symbol".format(self.current_interval_type()))
        #if there is no remaining time
        if time_left < 0:
            #stop the timer
            self.stop_timer()

    # method for starting the timer
    def start_timer(self, sender):
        #check if the function is being triggered by a button
        try: 
            if sender.title.split()[0] == "Start" and self.prefs.get("allow_sound"):
            #if yes, play a sound
                playsound("sounds/button.mp3", False)
        except: pass
        #define the timer length from preferences
        self.timer.end = self.prefs.get("{}_length".format(self.current_interval_type()))
        #start the timer
        self.timer.start()
        #replace the start button to the pause button
        if self.current_interval_type() == "pomodoro":
            self.replace_menu_item(self.start_pomodoro_button, self.pause_pomodoro_button)
        if self.current_interval_type() == "break":
            self.replace_menu_item(self.start_break_button, self.pause_break_button)
        if self.current_interval_type() == "long":
            self.replace_menu_item(self.start_long_button, self.pause_long_button)
        #update the session info
        self.update_session_info()
    
    #method for stoping the timer
    def stop_timer(self):
        #stop the timer
        self.timer.stop()
        self.timer.end = 0
        #notify the user according to the current timer type
        if self.current_interval_type() == "pomodoro":
            self.pomodoro_notification()
        if self.current_interval_type() == "break":
            self.break_notification()
        if self.current_interval_type() == "long":
            self.long_notification()
        #set the just passed interval to the time it has elapsed
        self.session_current[self.current_interval()] = self.timer.count - 1
        #load the next interval, get info about whether a new session has been started
        new_session = self.loaded_state()
        #autostart if a new session hasnt been started
        if not new_session:
            if self.prefs.get("autostart_pomodoro") == True and self.current_interval_type() == "pomodoro":
                self.start_timer(sender="")
            if self.prefs.get("autostart_break") == True and self.current_interval_type() == "break":
                self.start_timer(sender="")
            if self.prefs.get("autostart_break") == True and self.current_interval_type() == "long":
                self.start_timer(sender="")


    #method for pausing the timer
    def pause_timer(self, sender):
        #stop the timer
        self.timer.stop()
        #swap the pause_button for the continue button
        if sender.title == "Pause Pomodoro":
            self.replace_menu_item(self.pause_pomodoro_button, self.continue_pomodoro_button)
        if sender.title == "Pause Break":
            self.replace_menu_item(self.pause_break_button, self.continue_break_button)
        if sender.title == "Pause Long Break":
            self.replace_menu_item(self.pause_long_button, self.continue_long_button)

    #method for continuing the timer
    def continue_timer(self, sender):
        if sender.title.split()[0] == "Continue" and self.prefs.get("allow_sound"):
            #play a sound
            playsound("sounds/button.mp3", False)
        #start the timer
        self.timer.start()
        #replace the continue button woth the pause button
        if sender.title == "Continue Pomodoro":
            self.replace_menu_item(self.continue_pomodoro_button, self.pause_pomodoro_button)
        if sender.title == "Continue Break":
            self.replace_menu_item(self.continue_break_button, self.pause_break_button)
        if sender.title == "Continue Long Break":
            self.replace_menu_item(self.continue_long_button, self.pause_long_button)

    #method for reseting the timer
    def reset_timer(self, sender):
        if self.prefs.get("allow_sound"):
            #play a sound
            playsound("sounds/button.mp3")
        #load the next interval
        self.loaded_state()
        #start the timer
        self.start_timer(sender="")

    #method for skiping the timer
    def skip_timer(self, sender):
        if self.prefs.get("allow_sound"):
            #play a sound
            playsound("sounds/button.mp3")
        #if the timer has not started yet
        if self.timer.count == 0:
            self.session_current[self.current_interval()] = 0
        else:
            #set the just passed interval to the time it has elapsed
            self.session_current[self.current_interval()] = self.timer.count - 1
        try: print("\ntest:", self.saved_sessions[time.strftime("%Y_%m_%d",time.localtime(time.time()))])
        except: pass
        #load the next interval and get info whether a new session has been started
        new_session = self.loaded_state()
        #autostart if a new session hasnt been started
        if not new_session:
            if self.prefs.get("autostart_pomodoro") == True and self.current_interval_type() == "pomodoro":
                self.start_timer(sender="")
            if self.prefs.get("autostart_break") == True and self.current_interval_type() == "break":
                self.start_timer(sender="")
            if self.prefs.get("autostart_break") == True and self.current_interval_type() == "long":
                self.start_timer(sender="")
    
    #debug method for testing
    def about_info(self, sender):
        rumps.alert("About Tomado", "made with ❤️, care and patience by Daniel Gális \ndanielgalis.com \n\npart of self.governance(software)\n\n2022\nGPL-3.0 License")

    #not clickable
    def not_clickable(self, sender):
        self.not_clickable_notification()
    
    ##APP
    #method to run this app
    def run(self):
        self.app.run()
    
    def quit(self, sender):
        self.end_session(sender=None)
        rumps.quit_application(sender=None)

if __name__ == "__main__":
    app = Tomado()
    app.run()
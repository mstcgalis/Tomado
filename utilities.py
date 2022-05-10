from playsound import playsound

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
    if allow_sound:
        playsound("sounds/button.mp3")
    else:
        pass
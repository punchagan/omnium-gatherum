#!/usr/bin/env python
import subprocess
import sys

def search_windows(window):
    """Search for windows titled window"""
    search = subprocess.Popen("xdotool search --class %s" %(window), 
                              stdout=subprocess.PIPE, shell="FALSE")
    search_output = search.stdout.readlines()
    search.stdout.close()

    search_output = [each.strip() for each in search_output]
    return search_output

def get_current_ws():
    ws = subprocess.Popen("xdotool get_desktop", stdout=subprocess.PIPE,
                          shell='False')

    return ws.stdout.readline().strip()

def get_window_workspace(window):
    win_ws = subprocess.Popen("xdotool get_desktop_for_window %s"
                              %(window),stdout=subprocess.PIPE,
                              shell = "False")

    return win_ws.stdout.readline().strip()

def window_in_current_ws(output, ws):
    windows = filter(lambda w: get_window_workspace(w) == ws, output)
    if windows:
        return windows[0]
    else:
        return None

def raise_window_or_start_program(window, program):
    """ Search for window with string window in title (in current WorkSpace).
    Else, start program."""
    
    w = window_in_current_ws(search_windows(window), get_current_ws())
                             
    if w:
        subprocess.Popen("xdotool windowactivate %s" %(w), shell = "False")
    else:
        subprocess.Popen(program, shell="FALSE")

        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage %s window-name" %(sys.argv[0])
        exit(1)

    program = sys.argv[1]

    # Having different variables helps, in case of some programs. 
    window = program

    raise_window_or_start_program(window, program)

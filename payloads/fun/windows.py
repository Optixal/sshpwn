#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def prep(program):
    return "DISPLAY=:0 && export DISPLAY && nohup " + program + " &"

def send(shell, programs):
    for program in programs:
        shell.sendline(prep(program))
        output = str(shell.recvrepeat(0.2), "UTF-8")

def execute(session, configs, params):
    
    launch = ["gedit", "wireshark", "maltego"]
    launch.append("firefox -new-window https://www.google.com.sg/#q=my+little+pony")
    
    try:
        shell = session.shell("/bin/bash")
        send(shell, launch)
        shell.close()
        return 0
    except:
        return 2

#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def prep(program):
    return "DISPLAY=\":0\" && export DISPLAY && nohup " + program + " &"

def send(shell, programs):
    for program in programs:
        print(cs.status, "Launching", program)
        shell.sendline(prep(program))
        sleep(1)

def execute(session, configs, params):
    
    launch = ["gedit", "wireshark", "maltego"]
    launch.append("firefox -new-window https://www.google.com.sg/#q=my+little+pony")
    
    shell = session.process("/bin/bash")
    print(cs.status, "Launching programs...")
    send(shell, launch)

    shell.close()
    return 0


#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

waitforcapture = 1

def execute(session, configs, params):
    if not params:
        print(cs.status, "Usage: command [command (no nohup and &)]")
        return 1
    
    shell = session.process("/bin/sh", env={'PS1':''})
    shell.sendline(params)
    sleep(1)
    shell.close()
    return 0

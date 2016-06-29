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
    
    shell = session.process("/bin/bash")
    shell.sendline(params)
    print(cs.status, "Starting... will take 5 seconds...")
    sleep(5)
    print(cs.status, "Command executed! Closing shell...")
    shell.close()
    return 0

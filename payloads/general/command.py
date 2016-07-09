#!/usr/bin/python3

from pwn import *

def execute(session, configs, params):
    if not params:
        print(cs.status, "Usage: command [command]")
        return 1
    
    try:
        shell = session.shell("/bin/bash")
        shell.sendline(params)
        output = str(shell.recvrepeat(0.2), "UTF-8")
        shell.close()
        return 0
    except:
        return 2

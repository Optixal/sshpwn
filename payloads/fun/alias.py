#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):
    
    try:
        shell = session.shell("/bin/bash")

        bashrc_location = "/home/" + session.user + "/.bashrc" if session.user != "root" else "/root/.bashrc"
        shell.sendline("echo \"alias cd=ls\" >> " + bashrc_location)
        output = str(shell.recvrepeat(0.2), "UTF-8") 
        
        shell.close() 
        return 0
    except:
        return 2

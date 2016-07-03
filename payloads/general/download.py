#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):

    def download(remote_file):
        # TODO: Prepend username before saveas file if ~ is used
        save_as = remote_file.split("/")[-1]
        save_as = save_as.replace(".", "", 1) if save_as[0] == "." else save_as
        save_as = download_dir + save_as
        try:
            session.download_file(remote_file, save_as)
        except PermissionError:
            pass

    download_dir = configs["DownloadDirectory"] + session.host + "/"
    os.system("mkdir -p " + download_dir)

    downloads = params.split(" ")
    remote_home_dir = "/home/" + session.user + "/" if session.user != "root" else "/root/" 
    downloads = list(fileitem.replace("~/", remote_home_dir) for fileitem in downloads)

    for fileitem in downloads:
        try:
            download(fileitem) 
        except:
            # TODO: Count amount of successful downloads, if 0, return 2
            return 2
    return 0

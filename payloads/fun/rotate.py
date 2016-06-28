#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):
    session.upload_file("/home/opt/rotate.sh", "/tmp/rotate.sh")
    shell = session.process("/bin/bash")
    shell.sendline("chmod 754 /tmp/rotate.sh")
    shell.sendline("nohup /tmp/rotate.sh &")
    sleep(1)
    shell.close()
    return 0

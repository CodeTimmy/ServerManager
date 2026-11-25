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
import os

# TODO: Move to settings
DoubbleNL_Console = "auto"
DoubbleNL_Log = "True"
MaxLogSize = int("100000")

print("Server Manager  Copyright (C) 2026  CodeTimmy")
print("This program comes with ABSOLUTELY NO WARRANTY.")
print("This is free software, and you are welcome to")
print("redistribute it under the GPL-3.0 conditions.")
print("-----------------------------------------------")
print("More information:")
print("https://github.com/CodeTimmy/ServerManager/blob/main/LICENSE")
print("-----------------------------------------------")
print("Feel free to report bugs and suggest features at")
print("https://github.com/CodeTimmy/ServerManager/issues")
print("")
print("")
print("")

session = PromptSession()

basedir = Path(__file__).resolve().parent

exiting = False

last_log_source = "None"

def parse_time_digit(digit):
    if int(digit) in range(10):
        return(f"0{str(digit)}")
    else:
        return(str(digit))

def time_now():
    localtime = time.localtime()
    time_f = f"{parse_time_digit(localtime[2])}.{parse_time_digit(localtime[1])}.{localtime[0]}-{parse_time_digit(localtime[3])}:{parse_time_digit(localtime[4])}:{parse_time_digit(localtime[5])}" # TODO: implement on Windows
    return time_f

def printInfo(msg): # TODO: implement on Windows
    global last_log_source
    if (DoubbleNL_Console.lower() == "true") or ((DoubbleNL_Console.lower() == "auto") and (last_log_source != "INFO")):
        print("\n" + Fore.WHITE + "[INFO] " + str(msg))
    else:
        print(Fore.WHITE + "[INFO] " + str(msg))
    addLog(f"[{time_now()} | INFO] {str(msg)}\n")
    last_log_source = "INFO"

def StdOut(folder):
    global last_log_source
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
            if (DoubbleNL_Console.lower() == "true") or ((DoubbleNL_Console.lower() == "auto") and (last_log_source != folder)):
                print("\n" + Fore.GREEN + style + "[" + folder.upper() + "] " + color + line + Style.RESET_ALL, end="")
            else:
                print(Fore.GREEN + style + "[" + folder.upper() + "] " + color + line + Style.RESET_ALL, end="")
            addLog(f"[{time_now()} | {folder.upper()}] {line}") # TODO: implement on Windows
            last_log_source = folder
        else:
            printInfo(Fore.RED + Style.BRIGHT + folder + " is dead!" + Style.RESET_ALL)
            time.sleep(1)

def pstart(folder):
    if exiting:
        printInfo("Cannot start, while exiting!")
    else:
        file = basedir / folder / "start.sh"
        printInfo("Starting " + folder.upper())
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

def addLog(text: str): # TODO: implement on Windows
    global last_log_source
    os.makedirs('.LOGS', exist_ok=True)
    with open('.LOGS/latest.log', 'a', encoding='utf-8') as f:
        if DoubbleNL_Log.lower() == "true":
            f.write("\n" + text)
        else:
            f.write(text)
    with open('.LOGS/latest.log', 'r+', encoding='utf-8') as f:
        content = f.read()
        if len(content) > MaxLogSize:
            localtime = time.localtime()
            time_formated = f"{parse_time_digit(localtime[2])}-{parse_time_digit(localtime[1])}-{localtime[0]} {parse_time_digit(localtime[3])}-{parse_time_digit(localtime[4])}-{parse_time_digit(localtime[5])}"
            with open(f".LOGS/{time_formated}.log", 'w', encoding='utf-8') as f2:
                f2.write(content)
            f.seek(0)
            f.write(f"For older logs see: '.LOGS/{time_formated}.log'\n")
            f.truncate()
            if (DoubbleNL_Console.lower() == "true") or ((DoubbleNL_Console.lower() == "auto") and (last_log_source != "INFO")):
                print("\n" + Fore.WHITE + "[INFO] " + "Split Logfile!")
            else:
                print(Fore.WHITE + "[INFO] " + "Split Logfile!")
            last_log_source = "INFO"

addLog(f"[{time_now()} | INFO] ---------------S-T-A-R-T-E-D---------------\n")

procs = {}
folders = []
forbidden_folders = [
    "config", "logs", "local", "cache", "info", "input",
    ".config", ".logs", ".local", ".cache", ".info", ".input"
]
for folder in basedir.iterdir():
    if folder.is_dir():
        printInfo("- " + folder.name)
        if folder.name.lower() in forbidden_folders:
            printInfo("Skipped! (forbidden Name)")
            continue
        if not folder.name == folder.name.lower():
            printInfo("Skipped! (ERROR: ALL folder Names MUST be lowercase!)")
            continue
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
        if (DoubbleNL_Console.lower() == "true"):
            print("\n" + Fore.BLUE + "[INPUT] " + usrinput)
        else:
            print(Fore.BLUE + "[INPUT] " + usrinput)
        addLog(f"[{time_now()} | INPUT] {usrinput}\n")
        last_log_source = "INFO"
        if usrinput.startswith(".") or usrinput.startswith("/"):
            usrinput = usrinput.removeprefix(".").removeprefix("/").lower()
            if usrinput == "help":
                printInfo("Not implemented!")
                continue
            if usrinput == "list":
                printInfo("Not implemented!")
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
            printInfo("Unknown Command: " + usrinput + ", use /help for more info!")
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
            printInfo("Unknown Program/Server: " + usrinput + ", use /help or /list for more info!")

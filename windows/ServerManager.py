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

session = PromptSession()

basedir = Path(__file__).resolve().parent

exiting = False

def StdOut(folder):
    print("Started " + folder + " StdOut")
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

        print(Fore.GREEN + style + "[" + folder + "] " + color + line + Style.RESET_ALL, end="")
        if not line:
            print(Fore.RED + Style.BRIGHT + folder + " is dead!" + Style.RESET_ALL)
            time.sleep(1)

def start(folder):
    if exiting:
        print("Cannot start, while exiting!")
    else:
        print("Starting " + folder)
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
        print("- ", folder.name)
        if folder.name.startswith("."):
            print("Skipped!")
            continue
        file = folder / "start.bat"
        if file.is_file():
            folders.append(folder.name)
            print("Found!")
            start(folder.name)
            threading.Thread(target=StdOut, args=(folder.name,), daemon=True).start()

def restart_check():
    while True:
        for folder in folders:
            p = procs[folder]
            if not p.poll() is None:
                print(Fore.RED + Style.BRIGHT + folder + " exited with code " + str(p.returncode) + Style.RESET_ALL)
                start(folder)
                time.sleep(1)

#def stop_exit():
#    exiting = True
#    while True:
#        for folder in folders:
#            p = procs[folder]
#                if

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
            if usrinput == "kill":
                print("Not implemented!")
                continue
            #if usrinput == "exit":
            #    print("Stopping all Servers and exiting...")
            #    stop_exit()
            #    continue
            if usrinput == "start":
                print("Not implemented!")
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

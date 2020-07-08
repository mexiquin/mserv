#!/usr/bin/env python3

from .network_func import NetworkDownload
import os
import requests
import socket
from bs4 import BeautifulSoup
import argh
import subprocess
from colorama import Fore, Back, Style, init

init(autoreset=True)
serverDir = {}
url = "https://www.minecraft.net/en-us/download/server/"
dlr = NetworkDownload(url, None)

def identify_servers(path=os.getcwd()):
    # Identify any potential servers in current directory
    for subdir, _, filenames in walklevel(os.getcwd()):
        if "server.jar" in filenames:
            if os.path.basename(os.path.normpath(subdir)) in serverDir:
                serverDir[os.path.basename(os.path.normpath(subdir))].append(subdir)
            else:
                serverDir[os.path.basename(os.path.normpath(subdir))] = subdir

# os.walk, but allows for level distinction
def walklevel(some_dir, level=1):
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def update(serverName):
    """Goes to the official Mojang website and downloads the server.jar file again. This works whether or not the
    executable is new """
    # identify where the server.jar file is located
    os.remove(f"{os.path.join(serverDir[serverName], 'server.jar')}")
    dlr.download_to_dir(serverDir[serverName])




def eula_true(serverName):
    """Points to the eula.txt generated from the server executable, generates text to auto-accept the eula
    """
    eula_dir = os.path.join(serverDir[serverName], 'eula.txt')
    # with is like your try .. finally block in this case
    with open(eula_dir, 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    # now change the 2nd line, note that you have to add a newline
    if data[-1] != 'eula=true':
        accept_eula = input("Would you like to accept the Mojang EULA? (Y/n)")
        if accept_eula.lower == "y" or accept_eula == "":
            data[-1] = 'eula=true'
        else:
            print("EULA not accepted. You can do this later within the 'eula.txt' file")

        # and write everything back
        with open(eula_dir, 'w') as file:
            file.writelines(data)


def setup():
    """Runs functions that generate the server files before running
    """
    serverName = input(Fore.YELLOW + Style.BRIGHT + "Input new server name: ")
    os.mkdir(os.path.join(os.getcwd(), serverName))
    dlr.download_to_dir(os.path.join(os.getcwd(), serverName))
    identify_servers()
    run(first_launch=True, serverName=serverName)
    eula_true(serverName)
    print(Fore.GREEN + Style.BRIGHT + '\nEULA Accepted and server is ready to go!!')


def run(max_ram: "Maximum amount of ram alloted" = "-Xmx1024M", min_ram: "Minimum amount of ram alloted" = "-Xms1024M",
        gui: "if True, will show the Mojang UI, else will remain CLI-based" = False,
        first_launch: "Backend, used to denote if this is part of the Setup" = False, serverName='Server'):
    """Executes the server binary with optional parameters
    """
    # If multiple folders exist, let user select
    #TODO

    gui = "nogui" if gui is False else ""
    if first_launch:
        subprocess.run(
            ["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join((serverDir[serverName]), 'server.jar')}", f"{gui}"],
            cwd=serverDir[serverName], stdout=subprocess.DEVNULL)

        return

    # List all identified server folders and let user select them
    identify_servers()
    selectDir = ''
    if len(serverDir) > 1:
        print(f"{Fore.YELLOW}{Style.BRIGHT}Choose server to run (enter number): ")
        for number, item in enumerate(serverDir):
            print(f"{number} - {item}  ", end=' ',)
        selectDir = list(serverDir)[int(input())]
        #TODO
    else:
        selectDir=list(serverDir)[0]
    # Networking IP information
    print(Fore.GREEN + Style.BRIGHT + f"\nStarting {selectDir}\n")
    print(Fore.YELLOW + Style.BRIGHT + 'Gathering Network Information...\n')
    hostname = socket.gethostname()
    IP_Ad = requests.get('http://ip.42.pl/raw').text
    print(
        Fore.CYAN + Style.BRIGHT + f"Hostname: {hostname}\nIP Address: {IP_Ad}\nPort:25565")

    print("Starting Server...")
    subprocess.run(["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join(serverDir[selectDir], 'server.jar')}", f"{gui}"],
                   cwd=serverDir[selectDir])


# TODO
def GUI():
    """Executes the user interface for mserv, best for people who don't know how to use the command line
    """
    pass

def version():
    """Displays the current version of the program
    """
    with open('setup.py', 'r') as setup_file:
        data = setup_file.readlines()
    for line in data:
        if 'version' in line:
            print(Fore.MAGENTA + Style.BRIGHT+ f'mserv v{line[13:-3]}')


def main():
    parser = argh.ArghParser()
    parser.add_commands([setup, run, update, version])
    parser.dispatch()

if __name__ == "__main__":
    main()
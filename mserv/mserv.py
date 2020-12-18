#!/usr/bin/env python3

import os
import requests
import socket
import Libs.Networking as Networking
import click
import subprocess
from colorama import Fore, Style, init
import toml

init(autoreset=True)
serverDir = {}
url = "https://www.minecraft.net/en-us/download/server/"
downloader = Networking.Networking(url)
version_num = toml.load(os.path.join(os.pardir, 'pyproject.toml'))['tool']['poetry']['version']


@click.group()
@click.version_option(version=version_num)
def mserv_cli():
    pass


def identify_servers():
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


@click.command()
def update(server_name):
    """Download a fresh server.jar file from Mojang.

    Scrapes the Mojang server download website for a new server.jar file.
    This works whether or not the executable is new """

    # identify where the server.jar file is located
    os.remove(f"{os.path.join(serverDir[server_name], 'server.jar')}")
    downloader.download_to_dir(downloader.file_webscraper(), serverDir[server_name])


def eula_true(server_name):
    """Points to the eula.txt generated from the server executable, generates text to auto-accept the eula
    """
    eula_dir = os.path.join(serverDir[server_name], 'eula.txt')
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


@click.command()
def setup():
    """
    Create a new server.
    Runs functions that generate the server files before running.
    """
    new_server_name = input(Fore.YELLOW + Style.BRIGHT + "Input new server name: ")
    new_server_dir = os.path.join(os.getcwd(), new_server_name)
    os.mkdir(new_server_dir)
    downloader.download_to_dir(new_dir=new_server_dir, scrape=True)
    identify_servers()
    print(Fore.CYAN + Style.BRIGHT + '\nRunning first-time server setup...\n')
    __run(first_launch=True, server_name=new_server_name)
    eula_true(new_server_name)
    print(Fore.GREEN + Style.BRIGHT + '\nEULA Accepted and server is ready to go!!')


# Original run function, can operate independent of the argument parser
def __run(max_ram="-Xmx1024M", min_ram="-Xms1024M", gui=False, server_name="Server", first_launch=False):
    """Executes the server binary with optional parameters
    """

    ui = "nogui" if gui is False else ""

    if first_launch:
        subprocess.run(
            ["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join((serverDir[server_name]), 'server.jar')}",
             f"{ui}"],
            cwd=serverDir[server_name], stdout=subprocess.DEVNULL)

        return

    # List all identified server folders and let user select them
    identify_servers()
    if len(serverDir) > 1:
        print(f"{Fore.YELLOW}{Style.BRIGHT}Choose server to run (enter number): ")
        for number, item in enumerate(serverDir):
            print(f"{number} - {item}  ", end=' ', )
        selectDir = list(serverDir)[int(input())]
    else:
        selectDir = list(serverDir)[0]
    # Networking IP information
    print(Fore.GREEN + Style.BRIGHT + f"\nStarting {selectDir}\n")
    print(Fore.YELLOW + Style.BRIGHT + 'Gathering Network Information...\n')
    hostname = socket.gethostname()
    IP_Ad = requests.get('http://ip.42.pl/raw').text
    print(Fore.CYAN + Style.BRIGHT + f"Hostname: {hostname}\nPublic IP Address: {IP_Ad}\nPort:25565")
    print("Starting Server...")
    subprocess.run(
        ["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join(serverDir[selectDir], 'server.jar')}", f"{ui}"],
        cwd=serverDir[selectDir])


# Alias of the __run function that will be handled by the 'click' argument parser
@click.command()
@click.option('--max_ram', default="-Xmx1024M", help="Maximum amount of ram alloted")
@click.option('--min_ram', help="Minimum amount of ram alloted", default="-Xms1024M")
@click.option("--gui", default=False, help="'True', will show Mojang's UI, 'False', will remain CLI-based")
@click.option("--server_name", help="force execution of other server directory", default='Server')
def run(max_ram: str, min_ram: str, gui: bool, server_name: str, first_launch=False):
    __run(max_ram, min_ram, gui, server_name, first_launch)


# TODO implement GUI using pyqt
@mserv_cli.command()
def GUI():
    """Executes the user interface for mserv
    """
    pass


# Adding commands to the mserv_cli function for argument parsing
mserv_cli.add_command(setup)
mserv_cli.add_command(update)
mserv_cli.add_command(run)
mserv_cli.add_command(GUI)

if __name__ == "__main__":
    mserv_cli()

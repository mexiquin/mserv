#!/usr/bin/env python3

import os
import socket
import subprocess
import sys
import time

import click
import requests
from bs4 import BeautifulSoup
from rich.box import SIMPLE
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt, Confirm
from rich.table import Table
from importlib.metadata import version

version_num = version('mserv')

console = Console()


class Networking:
    """
    Handles downloader and web scraping functionalities
    """

    def __init__(self, source_url, local_dir=os.getcwd()):
        self.url = source_url
        self.local_dir = local_dir

    def extract_filename(self, new_url=None):
        """
        Extracts the filename from the provided url
        :param new_url: Specify any non-default url to examine
        :return: a string containing the filename at the end of the url
        """
        if new_url is not None:
            if new_url.find('/'):
                return new_url.rsplit('/', 1)[1]

        elif self.url.find('/'):
            return self.url.rsplit('/', 1)[1]

    def file_webscraper(self, search_file_name=None):
        """
        Searches a specified webpage searching for a hyperlink to a specified file

        :param search_file_name: Keyword search for a hyperlink on a webpage
        :return: The url of the identified hyperlink
        """
        requester = requests.get(self.url)
        soupy = BeautifulSoup(requester.text, features="html.parser")
        for link in soupy.findAll('a'):
            if link.get("href") is not None:
                if search_file_name in link.get("href"):
                    return link.get('href')

    def download_to_dir(self, new_dir=None, new_filename=None, scrape=False):
        """
        Downloads a file from a url and saves it in the specified output directory

        :param new_dir: Specify a non-default directory to download to
        :param new_filename: Specify a non-default filename for the downloaded file
        :param scrape: Determine whether or not to scrape the webpage for a file keyword,
        or simply download whatever is at the provided url
        """
        chunksize = 1024
        requester = requests.get(self.url if scrape is False else self.file_webscraper(search_file_name='server.jar'),
                                 stream=True)
        file_name = self.extract_filename(self.file_webscraper(search_file_name='server.jar'))
        directory = os.path.join(new_dir if new_dir is not None else self.local_dir,
                                 new_filename if new_filename is not None else file_name)
        # print(directory)
        # Exception handling for the HTTPS request
        try:
            requester.raise_for_status()
        except Exception as urlOof:
            console.print("[bold red]Error in accessing URL: %s[/bold red]", urlOof)
            input("Press ENTER to continue...")
        # console.print("Downloading %s" % file_name, style='bold yellow')
        # Some exception handling for file writing stuff
        with open(directory, "wb") as file:
            total_length = int(requester.headers.get('content-length'))
            for chunk in track(requester.iter_content(chunk_size=chunksize), total=(total_length / 1024) + 1,
                               description='[red]Downloading...'):
                if chunk:
                    file.write(chunk)
                    file.flush()


# Beginning of mserv CLI interface

# a dictionary of server subfolders. keeps track if multiple servers present in same directory.
# eg. MainServerDir/server1 MainServerDir/server2 etc.
serverDir = {}
url = "https://www.minecraft.net/en-us/download/server/"  # url of the minecraft server download page

downloader = Networking(url)


@click.group()
@click.version_option(version=version_num)
def mserv_cli():
    pass


def identify_servers():
    # Identify any potential servers (top-level subdirectories) in current directory
    for subdir, _, filenames in walklevel(os.getcwd()):
        if "server.jar" in filenames:  # Only parse through folders containing the server.jar exe
            if os.path.basename(os.path.normpath(subdir)) in serverDir:
                serverDir[os.path.basename(os.path.normpath(subdir))].append(subdir)
            else:
                serverDir[os.path.basename(os.path.normpath(subdir))] = subdir


def prog_exists(name):
    """
    Check whether `name` is on PATH and marked as executable.

    :param name: Name of the program in question
    :return: True if program is installed. Else, returns False
    """
    from shutil import which

    return which(name) is not None


def walklevel(some_dir, level=1):
    """
    os.walk, but allows for level distinction

    :param some_dir: Top level directory to walk through
    :param level: Depth of walk. Defaults to 1 level below
    """
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


@click.command()
def update():
    """Download a fresh server.jar file from Mojang.

    Scrapes the Mojang server download website for a new server.jar file.
    This works whether or not the executable is new """

    # identify where the server.jar file is located
    identify_servers()
    if len(serverDir) > 1:
        select_dir = Prompt.ask("[bold yellow]Choose server to update[/bold yellow]", choices=serverDir)
    else:
        select_dir = list(serverDir)[0]

    os.remove(f"{os.path.join(serverDir[select_dir], 'server.jar')}")  # remove the old server.jar exe
    downloader.download_to_dir(new_dir=serverDir[select_dir], scrape=True)  # webscrape to grab a new one


def eula_true(server_name):
    """Points to the eula.txt generated from the server executable, generates text to auto-accept the eula
    """
    eula_dir = os.path.join(serverDir[server_name], 'eula.txt')
    # with acts like a try/finally block in this case
    with open(eula_dir, 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    # now change the last line (containing the eula acceptance).
    if data[-1] != 'eula=true':
        accept_eula = Confirm.ask("[bold yellow]Would you like to accept the Mojang EULA?[/bold yellow]", default=True)
        if accept_eula is True:
            data[-1] = 'eula=true'
            console.print('\nEULA Accepted and server is ready to go!!', style='bold green')
        else:
            console.print("EULA not accepted. You can do this later within the 'eula.txt' file", style="bold red")

        # and write everything back
        with open(eula_dir, 'w') as file:
            file.writelines(data)


def __setup(debug_dir=None, debug_name=None, debug=False):
    new_server_name = Prompt.ask("[bold yellow]Input new server name[/bold yellow]") if not debug else debug_name
    new_server_dir = os.path.join(os.getcwd(), new_server_name) if not debug else os.path.join(debug_dir,
                                                                                               new_server_name)
    os.mkdir(new_server_dir)

    downloader.download_to_dir(new_dir=new_server_dir, scrape=True)
    with console.status("[bold green]Generating Server Files"):
        identify_servers()
        __run(first_launch=True, server_name=new_server_name)
    if not debug:
        eula_true(new_server_name)


@click.command()
def setup():
    """
    Create a new server.
    Runs functions that generate the server files before running.
    """

    __setup()


# Original run function, can operate independent of the argument parser
def __run(max_ram="-Xmx1024M", min_ram="-Xms1024M", gui=False, server_name="Server", first_launch=False):
    """Executes the server binary with optional parameters
    """

    # first, check if java is installed. If not, give error and close program.
    if not prog_exists('java'):
        console.print("\n\n[red bold]Java not detected![/red bold/\n\n")
        sys.exit(1)

    ui = "nogui" if gui is False else ""

    if first_launch:
        subprocess.run(
            ["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join((serverDir[server_name]), 'server.jar')}",
             f"{ui}"], cwd=serverDir[server_name], stdout=subprocess.DEVNULL)

        return

    # List all identified server folders and let user select them
    identify_servers()
    if len(serverDir) > 1:
        select_dir = Prompt.ask("[bold yellow]Choose server to run[/bold yellow]", choices=serverDir)
    else:
        select_dir = list(serverDir)[0]
    print(chr(27) + "[2J")

    # Network identifier information
    console.print(f"\nStarting {select_dir}\n", style='bold green')

    hostname = socket.gethostname()
    ip_addr = requests.get('http://ip.42.pl/raw').text

    network_table = Table(title='Network Information', show_header=False, show_lines=True, box=SIMPLE,
                          title_style='bold yellow')
    network_table.add_column(style='bold cyan', justify='right')
    network_table.add_column(style='bold green')

    network_table.add_row('Hostname:', hostname)
    network_table.add_row('Public IP Address:', ip_addr)
    network_table.add_row('Port:', '25565')

    console.print(network_table)

    # console.print("Starting Server...", style='bold')
    try:
        subprocess.run(
            ["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join(serverDir[select_dir], 'server.jar')}",
             f"{ui}"],
            cwd=serverDir[select_dir])
    except KeyboardInterrupt:
        with console.status(status="[bold red]Server shutting down...[/bold red]", speed=0.5, ):
            time.sleep(2)
            sys.exit(0)


# Alias of the __run function that will be handled by the 'click' argument parser
@click.command()
@click.option('--max_ram', default="-Xmx1024M", help="Maximum amount of ram allotted")
@click.option('--min_ram', help="Minimum amount of ram allotted", default="-Xms1024M")
@click.option("--gui", default=False, help="'True', will show Mojang's UI, 'False', will remain CLI-based")
@click.option("--server_name", help="force execution of other server directory", default='Server')
def run(max_ram: str, min_ram: str, gui: bool, server_name: str, first_launch=False):
    __run(max_ram, min_ram, gui, server_name, first_launch)


# Adding commands to the mserv_cli function for argument parsing
mserv_cli.add_command(setup)
mserv_cli.add_command(update)
mserv_cli.add_command(run)

if __name__ == "__main__":
    mserv_cli()

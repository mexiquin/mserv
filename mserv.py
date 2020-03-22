import os
import requests
import socket
from bs4 import BeautifulSoup
import argh
import subprocess
from clint.textui import progress
from colorama import Fore, Back, Style, init
init(autoreset=True)
serverDir = os.path.join(os.getcwd(), 'Server')
url = "https://www.minecraft.net/en-us/download/server/"


def file_webscraper(url=url, search_file='server.jar'):
    """Searches a specified webpage searching for a hyperlink to a specified file
    
    Keyword Arguments:
        url {str} -- Url of the webpage to scrape (default: {https://www.minecraft.net/en-us/download/server/})
        search_file {str} -- The file to search for (default: {'server.jar'})
    
    Returns:
        [str] -- The url of the file we want to access
    """
    requester = requests.get(url)
    soupy = BeautifulSoup(requester.text, features="html.parser")
    for link in soupy.findAll('a'):
        if link.get("href") is not None:
            if search_file in link.get("href"):
                return link.get('href')


# use this to execute functions you want to try
def test():
    """For debugging only
    """
    pass


def fileNameFromURL(url):
    # Extracts the filename from a given url
    if url.find('/'):
        return url.rsplit('/', 1)[1]


def update():
    """Goes to the official Mojang website and downloads the server.jar file again. This works whether or not the
    executable is new """
    # identify where the server.jar file is located
    os.remove(f"{os.path.join(serverDir, 'server.jar')}")
    download_to_dir(file_webscraper(), serverDir)


def download_to_dir(url, outDir=os.getcwd()):
    """Downloads a file from a url and saves it in the specified output directory
    
    Arguments:
        url {str} -- The url of the file to be downloaded
    
    Keyword Arguments:
        outDir {str} -- Directory to save the file to (default: {os.getcwd()})
    """
    requestor = requests.get(url)
    fileName = fileNameFromURL(url)
    directory = os.path.join(outDir, fileName)
    # Exception handling for the HTTPS request
    try:
        requestor.raise_for_status()
    except Exception as urlOof:
        print(Fore.RED + "Error in accessing URL: %s", urlOof)
        input("Press ENTER to continue...")

    print(Fore.YELLOW + Style.BRIGHT + "Downloading %s" % fileName)
    # Some exception handling for file writing stuff
    with open(directory, "wb") as file:
        total_length = int(requestor.headers.get('content-length'))
        for chunk in progress.bar(requestor.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
            if chunk:
                file.write(chunk)
                file.flush()


def eula_true():
    """Points to the eula.txt generated from the server executable, generates text to auto-accept the eula
    """
    eula_dir = os.path.join(serverDir, 'eula.txt')
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
    print(Fore.YELLOW + Style.BRIGHT + 'Downloading server files...')

    if not os.path.isdir(serverDir):
        print("Server folder doesn't exist. Generating...")
        os.mkdir(serverDir)
    download_to_dir(file_webscraper(), serverDir)
    run(first_launch=True)
    eula_true()
    print(Fore.GREEN + Style.BRIGHT + '\nEULA Accepted and server is ready to go!!')


def run(max_ram: "Maximum amount of ram alloted" = "-Xmx1024M", min_ram: "Minimum amount of ram alloted" = "-Xms1024M",
        gui: "if True, will show the Mojang UI, else will remain CLI-based" = False,
        first_launch: "Backend, used to denote if this is part of the Setup" = False):
    """Executes the server binary with optional parameters
    """
    gui = "nogui" if gui is False else ""
    if first_launch:
        subprocess.run(
            ["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join(serverDir, 'server.jar')}", f"{gui}"],
            cwd=serverDir)
        return

        # Networking IP information
    print(Fore.YELLOW + Style.BRIGHT + 'Gathering Network Information...\n')
    hostname = socket.gethostname()
    IP_Ad = requests.get('http://ip.42.pl/raw').text
    print(
        Fore.CYAN + Style.BRIGHT + f"Hostname: {hostname}\nIP Address: {IP_Ad}\nPort:25565")

    print("Starting Server...")
    subprocess.run(["java", f"{max_ram}", f"{min_ram}", "-jar", f"{os.path.join(serverDir, 'server.jar')}", f"{gui}"],
                   cwd=serverDir)


# TODO
def GUI():
    """Executes the user interface for mserv, best for people who don't know how to use the command line
    """
    pass


if __name__ == "__main__":
    parser = argh.ArghParser()
    parser.add_commands([setup, run, update, test])
    parser.dispatch()

import requests
from bs4 import BeautifulSoup
import os
from clint.textui import progress
from colorama import Fore, Back, Style, init

class NetworkDownload:
    def __init__(self, url, destination=os.getcwd()):
        self.dest = destination
        self.source = url
        self.requester = requests.get(self.source)
        init(autoreset=True)

    def file_webscraper(self, search_file='server.jar'):
        """Searches a specified webpage searching for a hyperlink to a specified file

        Keyword Arguments:
            source {str} -- source of the webpage to scrape (default: {https://www.minecraft.net/en-us/download/server/})
            search_file {str} -- The file to search for (default: {'server.jar'})

        Returns:
            [str] -- The source of the file we want to access
        """
        soupy = BeautifulSoup(self.requester.text, features="html.parser")
        for link in soupy.findAll('a'):
            if link.get("href") is not None:
                if search_file in link.get("href"):
                    return link.get('href')

    def _fileNameFromURL(self):
        # Extracts the filename from a given url
        if self.source.find('/'):
            return self.source.rsplit('/', 1)[1]

    def download_to_dir(self, newDir=None):
        """Downloads a file from a url and saves it in the specified output directory

        Arguments:
            url {str} -- The url of the file to be downloaded

        Keyword Arguments:
            outDir {str} -- Directory to save the file to (default: {os.getcwd()})
        """
        requestor = requests.get(self.source, stream=True)
        fileName = self._fileNameFromURL()
        directory = os.path.join(self.dest, fileName) if newDir == None else os.path.join(newDir, fileName)
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


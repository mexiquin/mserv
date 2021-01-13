import os

import requests
from bs4 import BeautifulSoup
from rich import style
from rich.progress import track
from rich.console import Console

console = Console()

class Networking:
    def __init__(self, url, local_dir=os.getcwd()):
        self.url = url
        self.local_dir = local_dir

    def extract_filename(self, new_url=None):
        # Extracts the filename from the provided url
        if new_url is not None:
            if new_url.find('/'):
                return new_url.rsplit('/', 1)[1]

        elif self.url.find('/'):
            return self.url.rsplit('/', 1)[1]

    def file_webscraper(self, search_file_name=None):
        """Searches a specified webpage searching for a hyperlink to a specified file

        Keyword Arguments:
            url {str} -- Url of the webpage to scrape
            search_file {str} -- The file to search for (default: {'server.jar'})

        """
        requester = requests.get(self.url)
        soupy = BeautifulSoup(requester.text, features="html.parser")
        for link in soupy.findAll('a'):
            if link.get("href") is not None:
                if search_file_name in link.get("href"):
                    return link.get('href')

    # TODO Find a replacement for 'clint' for download progress bars
    def download_to_dir(self, new_dir=None, new_filename=None, scrape=False):
        """Downloads a file from a url and saves it in the specified output directory

        Arguments:
            url {str} -- The url of the file to be downloaded

        Keyword Arguments:
            outDir {str} -- Directory to save the file to (default: {os.getcwd()})
        """
        chunksize = 1024
        requester = requests.get(self.url if scrape is False else self.file_webscraper(search_file_name='server.jar'),
                                 stream=True)
        file_name = self.extract_filename(self.file_webscraper(search_file_name='server.jar'))
        directory = os.path.join(new_dir if new_dir is not None else self.local_dir,
                                 new_filename if new_filename is not None else file_name)
        #print(directory)
        # Exception handling for the HTTPS request
        try:
            requester.raise_for_status()
        except Exception as urlOof:
            console.print("[bold red]Error in accessing URL: %s[/bold red]", urlOof)
            input("Press ENTER to continue...")
        #console.print("Downloading %s" % file_name, style='bold yellow')
        # Some exception handling for file writing stuff
        with open(directory, "wb") as file:
            total_length = int(requester.headers.get('content-length'))
            for chunk in track(requester.iter_content(chunk_size=chunksize), total=(total_length / 1024) + 1, description='Downloading...'):
                if chunk:
                    file.write(chunk)
                    file.flush()

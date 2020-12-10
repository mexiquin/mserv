import os

import requests
from bs4 import BeautifulSoup
from colorama import Fore, Back, Style


class Networking:
    def __init__(self, url, local_dir):
        self.url = url
        self.local_dir = local_dir

    def extract_filename(self):
        # Extracts the filename from the provided url
        if self.url.find('/'):
            return self.url.rsplit('/', 1)[1]

    def file_webscraper(self, search_file_name='server.jar'):
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
    def download_to_dir(self):
        """Downloads a file from a url and saves it in the specified output directory

        Arguments:
            url {str} -- The url of the file to be downloaded

        Keyword Arguments:
            outDir {str} -- Directory to save the file to (default: {os.getcwd()})
        """
        requester = requests.get(self.url, stream=True)
        file_name = self.fileNameFromURL(self.url)
        directory = os.path.join(self.local_dir, file_name)
        # Exception handling for the HTTPS request
        try:
            requester.raise_for_status()
        except Exception as urlOof:
            print(Fore.RED + "Error in accessing URL: %s", urlOof)
            input("Press ENTER to continue...")

        print(Fore.YELLOW + Style.BRIGHT + "Downloading %s" % file_name)
        # Some exception handling for file writing stuff
        with open(directory, "wb") as file:
            total_length = int(requester.headers.get('content-length'))
            for chunk in progress.bar(requester.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                if chunk:
                    file.write(chunk)
                    file.flush()

#!/usr/bin/python3
import os
import argparse
import requests
import platform
import socket
import sys

serverDir = os.path.join(os.getcwd(), 'Server')
url = "https://launcher.mojang.com/v1/objects/3dc3d84a581f14691199cf6831b71ed1296a9fdf/server.jar"

def fileNameFromURL(url):
    if url.find('/'):
        return url.rsplit('/', 1)[1]

def update(new_url):
    # identify where the server.jar file is located
    os.remove(f"{os.path.join(serverDir, 'server.jar')}")
    download_to_dir(new_url, serverDir)


def download_to_dir(url, outDir):
    requestor = requests.get(url, allow_redirects=True)
    fileName = fileNameFromURL(requestor.url)
    directory = '%s/%s' % (outDir, fileName)

    # Exception handling for the HTTPS request
    try:
        requestor.raise_for_status()
    except Exception as urlOof:
        print("Error in accessing URL: %s", urlOof)
        input("Press ENTER to continue...")

    print("Downloading %s" % fileName)

    # Some exception handling for file writing stuff
    try:
        file = open(directory, "wb")
        file.write(requestor.content)
        file.close()
    except IOError as e:
        print("Error writing file %s" % e)
        time.sleep(7)

    else:
        print("Download of %s Complete" % fileName)


def eula_true():
    eula_dir = os.path.join(serverDir, 'eula.txt')
    # with is like your try .. finally block in this case
    with open(eula_dir, 'r') as file:
        # read a list of lines into data
        data = file.readlines()

    # now change the 2nd line, note that you have to add a newline
    if data[-1] != 'eula=true':
        print("\n\nAuto-Accepting the EULA\n\n")
        data[-1] = 'eula=true'

        # and write everything back
        with open(eula_dir, 'w') as file:
            file.writelines(data)


def file_check():

    print('Downloading server files...')
    requester = requests.get(url, allow_redirects=True)

    if not os.path.isdir(serverDir):
        os.mkdir(serverDir)
        print('Writing files...')
        with open(os.path.join(serverDir, fileNameFromURL(url)), 'wb') as file:
            file.write(requester.content)
        print('\nFiles written to disk!!\n\n')
        main()
        eula_true()
        print('\n\nEULA Accepted and server is ready to go!!\n\nTo start server, run the same command without the "-g/--generate" flag\n\n')


def main():

    # Networking IP information
    print('Gathering Network Information...\n')
    hostname = socket.gethostname()
    IP_Ad = socket.gethostbyname(hostname)
    print(
        f"Hostname: {hostname}\nIP Address: {IP_Ad}\n\nStarting Server...\n\n")

    os.chdir(serverDir)
    os.system(f"java -Xmx1024M -Xms1024M -jar {os.path.join(serverDir, 'server.jar')} nogui")
    os.chdir('../')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--generate', help='Generate new server files (and auto-accept EULA)',
                        action='store_true')
    parser.add_argument('-r', '--run', help='Run the server', action='store_true')

    parser.add_argument('-u', '--update', help='Specify the new download url and update the server.jar file with the updated version', action='store_true')

    vals = parser.parse_args()

    if vals.generate:
        file_check()
    if vals.run:
        main()
    if vals.update:
        new_url = input('Enter the url of the new server.jar file: ')
        update(new_url)
    elif len(sys.argv) < 1:
        print('\n')
        parser.print_help()
        print('\n')

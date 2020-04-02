import subprocess
#import argh
import os

def build(input_file: str, one_file=True):
    """This script builds the specified python file into an executable binary"""

    subprocess.run(["pip", "install", "pyinstaller"])
    # find requirements.txt
    if os.path.isfile(os.path.join(os.getcwd(), 'requirements.txt')):
        subprocess.run(["pip", 
                        "install",
                        "-r",
                        "requirements.txt"])

    # build project using pyinstaller
    subprocess.run(["pyinstaller",
                    "--clean", 
                    "-F" if one_file else "-D", 
                    "--distpath", "./bin", 
                    input_file])


if __name__ == "__main__":
    build("mserv.py")
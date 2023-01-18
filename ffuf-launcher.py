#!/usr/bin/env python3

import inquirer
import subprocess
import argparse
import sys
import os
from distutils.spawn import find_executable
from colorama import init, Fore, Style

#########################
# Init
#########################
init()

BANNER = """
███████╗███████╗██╗   ██╗███████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║   ██║██╔════╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗
█████╗  █████╗  ██║   ██║█████╗      ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝
██╔══╝  ██╔══╝  ██║   ██║██╔══╝      ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗
██║     ██║     ╚██████╔╝██║         ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║
╚═╝     ╚═╝      ╚═════╝ ╚═╝         ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  

                                        By Eagleslam (@JDouliez)

"""

print(BANNER)

parser = argparse.ArgumentParser(
                    prog = 'Ffuf Launcher',
                    description = 'This tool lets you dynamically choose your wordlist and your extension list to fuzz. Because each website is different.')

parser.add_argument('URL', help='The url to fuzz. Must contains the FUZZ word')
parser.add_argument('ARGS', nargs='?', help='Any additional ffuf arguments. (Optional)')
args = parser.parse_known_args()

#########################
# Checks
#########################
if find_executable("fzf") is None:
    print(f"{Fore.RED}[!] fzf tool is not installed (https://github.com/junegunn/fzf).\nPlease run \"sudo apt install fzf\"{Style.RESET_ALL}")
    sys.exit(1)

if find_executable("ffuf") is None:
    print(f"{Fore.RED}[!] ffuf tool is not installed (https://github.com/ffuf/ffuf).\n Please run \"go install github.com/ffuf/ffuf@latest\"{Style.RESET_ALL}")
    sys.exit(1)

#########################
# Configuration
#########################

## Adapt these choices with your personal wordlists
WORDLISTS_CHOICES = {
    "directory-list-2.3-big.txt": "/usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt",
    "Bo0oM-fuzz.txt": "/usr/share/Bo0oM-fuzz.txt",
}

## Adapt these paths with your personal filesystem
WORDLISTS_FOLDER_PATHS = [".", "/usr/share/seclists", "/usr/share/wordlists"]

EXTENSIONS_CHOICES = [".html", ".js", ".php", ".log", ".zip", ".sql", ".txt", ".pdf", ".xml", ".conf", ".cfg", ".json", ".asp", ".aspx", ".jsp", ".py", ".rb", ".doc", ".docx", ".xls", ".xslx", ".tar", ".tar.gz", ".tgz"]
CUSTOM_LIST = "Custom list"

#########################
# Selecting one wordlist
#########################
wordlists_question = [inquirer.List('choice',message="Which wordlist do you want to fuzz with?", choices=[*WORDLISTS_CHOICES, CUSTOM_LIST])]
wordlist_answer = inquirer.prompt(wordlists_question)["choice"]

if wordlist_answer == CUSTOM_LIST:
    output = subprocess.check_output("find " + " ".join(WORDLISTS_FOLDER_PATHS) + " -type f -name '*.txt' 2>/dev/null | fzf", shell=True)
    wordlist = output.decode('utf-8').splitlines()[0]
else: 
    wordlist = WORDLISTS_CHOICES[wordlist_answer]

#########################
# Selecting extensions
#########################
extensions_question = [inquirer.Checkbox('choice', message="What extensions do you want to fuzz?", choices=EXTENSIONS_CHOICES)]
extension_as_list = inquirer.prompt(extensions_question)["choice"]

extensions = ",".join(extension_as_list)
args = " ".join(sys.argv[1:])

#########################
# Running ffuf
#########################
cmd = f"ffuf -c -r -w {wordlist} -o scan-ffuf.txt -e {extensions} -t 64 -mc all -fc 404 -u {args}"
os.system(cmd)
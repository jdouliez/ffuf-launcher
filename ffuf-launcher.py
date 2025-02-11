#!/usr/bin/env python3

import re
from bs4 import BeautifulSoup
import inquirer
import subprocess
import argparse
import sys
import os
from distutils.spawn import find_executable
from colorama import init, Fore, Back, Style
import requests

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

                                        By Ali@s (@JDouliez)

"""

print(BANNER)

parser = argparse.ArgumentParser(
                    prog = 'Ffuf Launcher',
                    description = 'This tool lets you dynamically choose your wordlist and your extension list to fuzz. Because each website is different.')

parser.add_argument('URL', help='The url to fuzz.')
parser.add_argument('ARGS', nargs='?', help='Any additional ffuf arguments. (Optional)')
args = parser.parse_known_args()

#########################
# Checks
#########################

def is_number(var):
    pattern = re.compile(r'^-?\d+(\.\d+)?$')
    return bool(pattern.match(str(var)))

if find_executable("fzf") is None:
    print(f"{Fore.RED}[!] fzf tool is not installed (https://github.com/junegunn/fzf).\nPlease run \"sudo apt install fzf\"{Style.RESET_ALL}")
    sys.exit(1)

if find_executable("ffuf") is None:
    print(f"{Fore.RED}[!] ffuf tool is not installed (https://github.com/ffuf/ffuf).\n Please run \"go install github.com/ffuf/ffuf/v2@latest\"{Style.RESET_ALL}")
    sys.exit(1)

scans_path = "./scans"
if not os.path.isdir(scans_path):
    os.makedirs(scans_path)

#########################
# Configuration
#########################

## Adapt these choices with your personal wordlists
WORDLISTS_CHOICES = {
    "directory-list-2.3-small.txt": "/usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-small.txt",
    "directory-list-2.3-medium.txt": "/usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt",
    "directory-list-2.3-big.txt": "/usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt",
    "Bo0oM-fuzz.txt": "/usr/share/Bo0oM-fuzz.txt",
    "onelistforallmicro.txt": "/usr/share/onelistforallmicro.txt",
    "jhaddix_content_discovery_all.txt": "/usr/share/jhaddix_content_discovery_all.txt",
    "BugBountyWordlist (custom)": "/usr/share/BugBountyWordlist.txt"
}

## Adapt these paths with your personal filesystem
WORDLISTS_FOLDER_PATHS = [".", "/usr/share/SecLists/Discovery/Web-Content/", "/usr/share/wordlists"]

EXTENSIONS_CHOICES = [".html", ".js", ".php", ".jsp", ".log", ".zip", ".sql", ".txt", ".pdf", ".xml", ".conf", ".cfg", ".json", ".asp", ".aspx", ".jsp", ".py", ".rb", ".doc", ".docx", ".xls", ".xslx", ".tar", ".tar.gz", ".tgz"]
CUSTOM_LIST = "Custom/Local list"
ASSETNOTES_WORDLISTS_CHOICES = {}

#########################
# Selecting one wordlist
#########################

# Let's use the Assetnote Wordlists (https://wordlists.assetnote.io/)
for file in requests.get("https://wordlists-cdn.assetnote.io/data/automated.json").json()['data']:
    filename = ' / '.join(file['Filename'].replace("httparchive_", "")[:-15].split("_"))
    name = f"Specific (automated): {filename} ({file['File Size']})"
    link = BeautifulSoup(file['Download'], 'html.parser').a['href']
    ASSETNOTES_WORDLISTS_CHOICES[name] = link

for file in requests.get("https://wordlists-cdn.assetnote.io/data/manual.json").json()['data']:
    filename = file['Filename'].replace("httparchive_", "")
    name = f"Specific (manual): {filename} ({file['File Size']})"
    link = BeautifulSoup(file['Download'], 'html.parser').a['href']
    ASSETNOTES_WORDLISTS_CHOICES[name] = link


wordlists_question = [inquirer.List('choice',message="Which wordlist do you want to fuzz with?", choices=['---------------- CLASSIC ----------------', *WORDLISTS_CHOICES, '---------------- CUSTOM ---------------- ', CUSTOM_LIST, '---------------- ASSETNOTES ----------------', *ASSETNOTES_WORDLISTS_CHOICES])]
wordlist_answer = inquirer.prompt(wordlists_question)["choice"]

if wordlist_answer.startswith('----------------'):
    exit(1)
elif wordlist_answer == CUSTOM_LIST:
    output = subprocess.check_output("find " + " ".join(WORDLISTS_FOLDER_PATHS) + " -type f -name '*.txt' 2>/dev/null | fzf", shell=True)
    wordlist = output.decode('utf-8').splitlines()[0]
elif "Specific" in wordlist_answer:
    filename = ASSETNOTES_WORDLISTS_CHOICES[wordlist_answer].split("/")[-1]
    file_path = os.path.join(WORDLISTS_FOLDER_PATHS[-1], filename)

    if not os.path.exists(WORDLISTS_FOLDER_PATHS[-1]):
        try:
            subprocess.run(['sudo', 'mkdir', '-p', WORDLISTS_FOLDER_PATHS[-1]], check=True)
            subprocess.run(['sudo', 'chown', f'{os.getlogin()}:{os.getlogin()}', WORDLISTS_FOLDER_PATHS[-1]], check=True)
            print(f"{Fore.YELLOW}Directory {WORDLISTS_FOLDER_PATHS[-1]} created with sudo{Fore.RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error occurred while creating directory with sudo: {e}{Fore.RESET}")

    if not os.path.exists(file_path):
        print(f"{Fore.YELLOW}Downloading new wordlist...{Fore.RESET}")
        os.system(f"wget -q {ASSETNOTES_WORDLISTS_CHOICES[wordlist_answer]} -O {file_path}")

    wordlist = file_path
else:
    wordlist = WORDLISTS_CHOICES[wordlist_answer]

if not os.path.exists(wordlist):
    print(f"{Fore.RED}[!] The selected wordlist is not accessible. Check the configuration section in the file.{Style.RESET_ALL}")
    sys.exit(1)

#########################
# Selecting extensions
#########################
if "Specific" not in wordlist_answer:
    extensions_question = [inquirer.Checkbox('choice', message="What extensions do you want to fuzz?", choices=EXTENSIONS_CHOICES)]
    extension_as_list = inquirer.prompt(extensions_question)["choice"]
    if len(extension_as_list) == 0:
        print(f"{Fore.YELLOW}[!] You have not selected any extension{Style.RESET_ALL}")
else:
    extension_as_list = []

extensions = ",".join(extension_as_list)

args_array = []
for arg in sys.argv[1:]:
    if arg.startswith("-") or arg.startswith("http") or is_number(arg):
        args_array.append(arg)
    else:
        args_array.append(f"'{arg}'")  

args = " ".join(args_array)

#########################
# Running ffuf
#########################
extension_cmd = f"-e {extensions}" if len(extensions) > 0 else ""

url = args.split(" ")[0]
if "FUZZ" not in url:
    if not url.endswith("/"):
        url += "/"
    url += "FUZZ"

other_args =  args.split(" ", 1)[1] if len(args.split(" ")) > 1 else "" 
ua_arg = " -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'" if "User-Agent" not in other_args else ""

url_for_file = args.split(" ")[0].replace("http://", "").replace("https://", "").replace("/FUZZ", "").replace("/", "_")
cmd = f"ffuf -c -ic -r -w {wordlist} -o scans/scan-ffuf-{url_for_file}.txt {extension_cmd} -t 64 -mc all -u {url} {other_args}{ua_arg}"
print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Running command \"{Fore.WHITE}{Back.BLACK}{cmd}{Style.RESET_ALL}\"")
os.system(cmd)

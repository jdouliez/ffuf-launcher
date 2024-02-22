#!/usr/bin/env python3

import inquirer
import subprocess
import argparse
import sys
import os
from distutils.spawn import find_executable
from colorama import init, Fore, Back, Style

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
CUSTOM_LIST = "Custom list"

#########################
# Selecting one wordlist
#########################
wordlists_question = [inquirer.List('choice',message="Which wordlist do you want to fuzz with?", choices=[*WORDLISTS_CHOICES, CUSTOM_LIST])]
wordlist_answer = inquirer.prompt(wordlists_question)["choice"]
2
if wordlist_answer == CUSTOM_LIST:
    output = subprocess.check_output("find " + " ".join(WORDLISTS_FOLDER_PATHS) + " -type f -name '*.txt' 2>/dev/null | fzf", shell=True)
    wordlist = output.decode('utf-8').splitlines()[0]
else:
    wordlist = WORDLISTS_CHOICES[wordlist_answer]

if not os.path.exists(wordlist):
    print(f"{Fore.RED}[!] The selected wordlist is not accessible. Check the configuration section in the file.{Style.RESET_ALL}")
    sys.exit(1)

#########################
# Selecting extensions
#########################
extensions_question = [inquirer.Checkbox('choice', message="What extensions do you want to fuzz?", choices=EXTENSIONS_CHOICES)]
extension_as_list = inquirer.prompt(extensions_question)["choice"]
if len(extension_as_list) == 0:
    print(f"{Fore.YELLOW}[!] You have not selected any extension{Style.RESET_ALL}")

extensions = ",".join(extension_as_list)
args = " ".join(sys.argv[1:])

#########################
# Running ffuf
#########################
if len(extensions) > 0:
    extension_cmd = f"-e {extensions}"
else:
    extension_cmd = ""

url = args.split(" ")[0]
if "FUZZ" not in url:
    if not url.endswith("/"):
        url += "/"
    url += "FUZZ"

other_args =  args.split(" ", 1)[1] if len(args.split(" ")) > 1 else "" 
ua_arg = "-H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'" if "User-Agent" not in other_args else ""

url_for_file = args.split(" ")[0].replace("http://", "").replace("https://", "").replace("/FUZZ", "").replace("/", "_")
cmd = f"ffuf -c -ic -r -w {wordlist} -o scans/scan-ffuf-{url_for_file}.txt {extension_cmd} -t 64 -mc all -fc 404 -u {url} {other_args} {ua_arg}"
print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Running command \"{Fore.WHITE}{Back.BLACK}{cmd}{Style.RESET_ALL}\"")
os.system(cmd)

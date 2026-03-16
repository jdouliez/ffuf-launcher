#!/usr/bin/env python3

import json
import re
import shlex
import shutil
from collections import Counter
import inquirer
import subprocess
import argparse
import sys
import os
from colorama import init, Fore, Back, Style
import requests
import warnings
warnings.filterwarnings("ignore")

REQUEST_TIMEOUT = 10

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
                    prog='Ffuf Launcher',
                    description='This tool lets you dynamically choose your wordlist and your extension list to fuzz. Because each website is different.')

parser.add_argument('URL', help='The url to fuzz.')
parser.add_argument('ARGS', nargs='?', help='Any additional ffuf arguments. (Optional)')
args = parser.parse_known_args()

#########################
# Checks
#########################

def is_number(var):
    pattern = re.compile(r'^-?\d+(\.\d+)?$')
    return bool(pattern.match(str(var)))

if shutil.which("fzf") is None:
    print(f"{Fore.RED}[!] fzf tool is not installed (https://github.com/junegunn/fzf).\nPlease run \"sudo apt install fzf\"{Style.RESET_ALL}")
    sys.exit(1)

if shutil.which("ffuf") is None:
    print(f"{Fore.RED}[!] ffuf tool is not installed (https://github.com/ffuf/ffuf).\n Please run \"go install github.com/ffuf/ffuf/v2@latest\"{Style.RESET_ALL}")
    sys.exit(1)

scans_path = "./scans"
if not os.path.isdir(scans_path):
    os.makedirs(scans_path)

# Parse URL early (needed for memory lookup)
user_args = []
base_url = None
for arg in sys.argv[1:]:
    if arg.startswith("http://") or arg.startswith("https://"):
        base_url = arg
    else:
        user_args.append(arg)

if not base_url:
    print(f"{Fore.RED}[!] No URL provided. Usage: ffuf-launcher.py <URL> [ffuf_args...]{Style.RESET_ALL}")
    sys.exit(1)

#########################
# Memory: remember last wordlist & extensions per URL
#########################
MEMORY_DIR = os.path.expanduser("~/.config/ffuf-launcher")
MEMORY_FILE = os.path.join(MEMORY_DIR, "scan_memory.json")


def _memory_key(url):
    """Normalize URL for memory lookup (strip FUZZ, scheme, trailing slash)."""
    u = url.replace("/FUZZ", "").rstrip("/")
    if not u.endswith("/"):
        u += "/"
    return u


def load_memory():
    try:
        if os.path.isfile(MEMORY_FILE):
            with open(MEMORY_FILE) as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_memory(key, wordlist_choice, extensions_list):
    try:
        os.makedirs(MEMORY_DIR, exist_ok=True)
        data = load_memory()
        data[key] = {"wordlist": wordlist_choice, "extensions": extensions_list}
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


memory_key = _memory_key(base_url)
memory = load_memory().get(memory_key, {})

#########################
# Configuration
#########################

## Adapt these choices with your personal wordlists
WORDLISTS_CHOICES = {
    "onelistforallmicro.txt": "/usr/share/onelistforallmicro.txt",
    "Bo0oM-fuzz.txt": "/usr/share/Bo0oM-fuzz.txt",
    "jhaddix_content_discovery_all.txt": "/usr/share/jhaddix_content_discovery_all.txt",
    "raft-small-words.txt": "/usr/share/SecLists/Discovery/Web-Content/raft-small-words.txt",
    "raft-medium-words.txt": "/usr/share/SecLists/Discovery/Web-Content/raft-medium-words.txt",
    "raft-large-words.txt": "/usr/share/SecLists/Discovery/Web-Content/raft-large-words.txt",
}


## Adapt these paths with your personal filesystem
WORDLISTS_FOLDER_PATHS = [".", "/usr/share/SecLists/Discovery/Web-Content/", "/usr/share/wordlists"]

EXTENSIONS_CHOICES = [".html", ".js", ".php", ".jsp", ".log", ".zip", ".sql", ".txt", ".pdf", ".xml", ".conf", ".cfg", ".json", ".asp", ".aspx", ".py", ".rb", ".doc", ".docx", ".xls", ".xslx", ".tar", ".tar.gz", ".tgz"]
CUSTOM_LIST = "Custom/Local list"
ASSETNOTES_WORDLISTS_CHOICES = {}

#########################
# Selecting one wordlist
#########################

# Filter not existing wordlist on the filesystem
WORDLISTS_CHOICES = {
    key: value for key, value in WORDLISTS_CHOICES.items()
    if os.path.isfile(value)
}

# Let's use the Assetnote Wordlists (https://wordlists.assetnote.io/)
ASSETNOTES_CDN_BASE = "https://wordlists-cdn.assetnote.io/data"
try:
    for file in requests.get(f"{ASSETNOTES_CDN_BASE}/automated.json", timeout=REQUEST_TIMEOUT).json().get("data", []):
        filename = " / ".join(file["Filename"].replace("httparchive_", "")[:-15].split("_"))
        name = f"Specific (automated): {filename} ({file['File Size']})"
        link = f"{ASSETNOTES_CDN_BASE}/automated/{file['Filename']}"
        ASSETNOTES_WORDLISTS_CHOICES[name] = link

    for file in requests.get(f"{ASSETNOTES_CDN_BASE}/manual.json", timeout=REQUEST_TIMEOUT).json().get("data", []):
        filename = file["Filename"].replace("httparchive_", "")
        name = f"Specific (manual): {filename} ({file['File Size']})"
        link = f"{ASSETNOTES_CDN_BASE}/manual/{file['Filename']}"
        ASSETNOTES_WORDLISTS_CHOICES[name] = link
except (requests.RequestException, KeyError):
    print(f"{Fore.YELLOW}[!] Assetnotes catalog unavailable (offline or network error){Style.RESET_ALL}")

# Build choices: hide ASSETNOTES section when empty (e.g. offline)
wordlist_choices = ["---------------- CLASSIC ----------------", *WORDLISTS_CHOICES, "---------------- CUSTOM ---------------- ", CUSTOM_LIST]
if ASSETNOTES_WORDLISTS_CHOICES:
    wordlist_choices.extend(["---------------- ASSETNOTES ----------------", *ASSETNOTES_WORDLISTS_CHOICES])

default_wordlist = memory.get("wordlist") if memory.get("wordlist") in wordlist_choices else None
list_kwargs = {"message": "Which wordlist do you want to fuzz with?", "choices": wordlist_choices}
if default_wordlist is not None:
    list_kwargs["default"] = default_wordlist
wordlists_question = [inquirer.List("choice", **list_kwargs)]
answers = inquirer.prompt(wordlists_question)
if answers is None:
    sys.exit(0)  # User cancelled (Ctrl+C or similar)
wordlist_answer = answers["choice"]

if wordlist_answer.startswith("----------------"):
    sys.exit(1)
elif wordlist_answer == CUSTOM_LIST:
    find_args = ["find"] + [os.path.abspath(p) for p in WORDLISTS_FOLDER_PATHS] + ["-type", "f", "-name", "*.txt"]
    try:
        find_proc = subprocess.Popen(find_args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        # Only capture stdout (selection); stderr must go to terminal for fzf's interactive UI
        fzf_proc = subprocess.run(["fzf"], stdin=find_proc.stdout, stdout=subprocess.PIPE, text=True, check=True)
        find_proc.wait()
        wordlist = fzf_proc.stdout.strip()
    except subprocess.CalledProcessError:
        print(f"{Fore.RED}[!] Selection cancelled or no wordlist chosen.{Style.RESET_ALL}")
        sys.exit(1)
    if not wordlist or not os.path.isfile(wordlist):
        print(f"{Fore.RED}[!] Invalid selection. Please choose a valid wordlist file.{Style.RESET_ALL}")
        sys.exit(1)
elif "Specific" in wordlist_answer:
    download_url = ASSETNOTES_WORDLISTS_CHOICES[wordlist_answer]
    filename = download_url.split("/")[-1]
    file_path = os.path.join(WORDLISTS_FOLDER_PATHS[-1], filename)

    if not os.path.exists(WORDLISTS_FOLDER_PATHS[-1]):
        try:
            subprocess.run(["sudo", "mkdir", "-p", WORDLISTS_FOLDER_PATHS[-1]], check=True)
            subprocess.run(["sudo", "chown", f"{os.getlogin()}:{os.getlogin()}", WORDLISTS_FOLDER_PATHS[-1]], check=True)
            print(f"{Fore.YELLOW}Directory {WORDLISTS_FOLDER_PATHS[-1]} created with sudo{Fore.RESET}")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}Error occurred while creating directory with sudo: {e}{Fore.RESET}")

    if not os.path.exists(file_path):
        print(f"{Fore.YELLOW}Downloading new wordlist...{Fore.RESET}")
        try:
            subprocess.run(["wget", "-q", download_url, "-O", file_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Failed to download wordlist: {e}{Fore.RESET}")
            sys.exit(1)

    wordlist = file_path
else:
    wordlist = WORDLISTS_CHOICES[wordlist_answer]

if not os.path.exists(wordlist):
    print(f"{Fore.RED}[!] The selected wordlist is not accessible. Check the configuration section in the file.{Style.RESET_ALL}")
    sys.exit(1)

#########################
# Selecting extensions
#########################
if "Specific" not in wordlist_answer and "onelistforallmicro.txt" not in wordlist_answer and "Bo0oM-fuzz.txt" not in wordlist_answer and "jhaddix_content_discovery_all.txt" not in wordlist_answer:
    default_extensions = [e for e in memory.get("extensions", []) if e in EXTENSIONS_CHOICES]
    checkbox_kwargs = {"message": "What extensions do you want to fuzz?", "choices": EXTENSIONS_CHOICES}
    if default_extensions:
        checkbox_kwargs["default"] = default_extensions
    extensions_question = [inquirer.Checkbox("choice", **checkbox_kwargs)]
    ext_answers = inquirer.prompt(extensions_question)
    if ext_answers is None:
        sys.exit(0)  # User cancelled
    extension_as_list = ext_answers["choice"]
    if len(extension_as_list) == 0:
        print(f"{Fore.YELLOW}[!] You have not selected any extension{Style.RESET_ALL}")
else:
    extension_as_list = []

extensions = ",".join(extension_as_list)

# Save selection to memory for next scan of same URL
save_memory(memory_key, wordlist_answer, extension_as_list)

############################
# Dynamic probe: detect "not found" response size
############################
# Probe multiple non-existent paths to find the response size(s) of error/not-found pages.
# Uses response SIZE (bytes), not status code or line count. Does NOT block 404 by default.
# Filters results by excluding responses matching the detected baseline size(s).

# Varied paths to cover different "not found" responses (no ext, .php, .html, dir, etc.)
PROBE_REQUESTS = [
    "/idontguessitcouldexist.idk",
    "/sdjhfskdfhskfruskuhfksudhfksdjhf.ldsjf",
    "/checking-security",
    "/zxcvbnmqwerty98765.xyz",
    "/__nonexistent_probe_path__",
    "/nopage",
    "/fakepath.php",
    "/nonexistent.html",
    "/fake_subdir/",
]

PROBE_MIN_OCCURRENCES = 2  # Filter any size seen at least this many times

simple_url = base_url.replace("/FUZZ", "").rstrip("/")
dynamic_filter_sizes = []  # List of sizes to filter (ffuf -fs accepts comma-separated)

# Skip probe if user already specified -fs or -fl
user_has_size_filter = "-fs" in user_args or "-fl" in user_args

if not user_has_size_filter:
    try:
        sizes = []
        for path in PROBE_REQUESTS:
            resp = requests.get(f"{simple_url}{path}", verify=False, timeout=REQUEST_TIMEOUT)
            sizes.append(len(resp.content))

        # Filter ALL sizes that appear repeatedly (multiple "not found" page templates)
        size_counts = Counter(sizes)
        dynamic_filter_sizes = [
            size for size, count in size_counts.items()
            if count >= PROBE_MIN_OCCURRENCES
        ]
        dynamic_filter_sizes.sort()
        if dynamic_filter_sizes:
            sizes_str = ",".join(str(s) for s in dynamic_filter_sizes)
            print(f"{Fore.GREEN}[+] Dynamic probe: filtering response sizes {sizes_str} bytes (from {len(PROBE_REQUESTS)} probes){Style.RESET_ALL}")
    except requests.RequestException:
        pass  # Skip dynamic filter on network error

#########################
# Running ffuf
#########################
url = base_url
if "FUZZ" not in url:
    if not url.endswith("/"):
        url += "/"
    url += "FUZZ"

# Sanitize output filename: keep alphanumeric, dash, dot, underscore
url_for_file = base_url.replace("http://", "").replace("https://", "").replace("/FUZZ", "").rstrip("/")
url_for_file = re.sub(r"[^\w\-.]", "_", url_for_file).strip("_") or "output"

output_file = os.path.join("scans", f"scan-ffuf-{url_for_file}.txt")

# Build ffuf command with subprocess (no shell injection)
ffuf_args = ["ffuf", "-c", "-ic", "-w", wordlist, "-o", output_file, "-t", "64", "-mc", "all"]
if extensions:
    ffuf_args.extend(["-e", extensions])
if dynamic_filter_sizes:
    ffuf_args.extend(["-fs", ",".join(str(s) for s in dynamic_filter_sizes)])
ffuf_args.extend(["-u", url])
ffuf_args.extend(user_args)
if not any("User-Agent" in a for a in user_args):
    ffuf_args.extend(["-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"])

cmd_str = " ".join(shlex.quote(a) for a in ffuf_args)
print(f"[{Fore.YELLOW}*{Style.RESET_ALL}] Running command \"{Fore.WHITE}{Back.BLACK}{cmd_str}{Style.RESET_ALL}\"")

try:
    result = subprocess.run(ffuf_args)
    sys.exit(result.returncode)
except KeyboardInterrupt:
    print(f"\n{Fore.YELLOW}[!] Interrupted by user (Ctrl-C){Style.RESET_ALL}")
    sys.exit(130)

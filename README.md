# Ffuf Launcher

```

███████╗███████╗██╗   ██╗███████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║   ██║██╔════╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗
█████╗  █████╗  ██║   ██║█████╗      ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝
██╔══╝  ██╔══╝  ██║   ██║██╔══╝      ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗
██║     ██║     ╚██████╔╝██║         ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║
╚═╝     ╚═╝      ╚═════╝ ╚═╝         ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  

                                        By Eagleslam (@JDouliez)
```
## Description

This tool is a simple ffuf launcher which lets you select dynamically which wordlist and which extentions you want to fuzz.

## Installation

Just install the python3 requirements...
```bash
$> pip3 install -r requirements.txt
```

... and make sur you have to right dependencies
```bash
# https://github.com/junegunn/fzf
$> sudo apt install fzf

# https://github.com/ffuf/ffuf
$> go install github.com/ffuf/ffuf@lates

# Add an alias for the fun
$> alias ffufscan="$(pwd)/ffuf-launcher.py"
```
## Use

```bash
$> python ffuf-launcher.py http://google.fr/FUZZ -h

███████╗███████╗██╗   ██╗███████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║   ██║██╔════╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗
█████╗  █████╗  ██║   ██║█████╗      ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝
██╔══╝  ██╔══╝  ██║   ██║██╔══╝      ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗
██║     ██║     ╚██████╔╝██║         ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║
╚═╝     ╚═╝      ╚═════╝ ╚═╝         ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  

                                        By Eagleslam (@JDouliez)


usage: Ffuf Launcher [-h] URL [ARGS]

This tool lets you dynamically choose your wordlist and your extension list to fuzz. Because each website is different.

positional arguments:
  URL         The url to fuzz. Must contains the FUZZ word
  ARGS        Any additional ffuf args. (Optional)

optional arguments:
  -h, --help  show this help message and exit
```

## Examples

```bash
$> python ffuf-launcher.py http://example.com/FUZZ -fc 404,502 -fs 1337

███████╗███████╗██╗   ██╗███████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║   ██║██╔════╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗
█████╗  █████╗  ██║   ██║█████╗      ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝
██╔══╝  ██╔══╝  ██║   ██║██╔══╝      ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗
██║     ██║     ╚██████╔╝██║         ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║
╚═╝     ╚═╝      ╚═════╝ ╚═╝         ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  

                                        By Eagleslam (@JDouliez)


[?] Which wordlist do you want to fuzz with?: directory-list-2.3-big.txt
 > directory-list-2.3-big.txt
   Bo0oM-fuzz.txt
   Custom list

[?] What extensions do you want to fuzz?: 
   [X] .html
   [X] .js
   [X] .php
   [X] .log
   [X] .zip
   [ ] .sql
   [ ] .txt
 > [X] .pdf
   [ ] .xml
   [ ] .conf
   [ ] .cfg
   [ ] .json
   [ ] .asp
   [ ] .aspx


        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.3.1-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://example.com/FUZZ
 :: Wordlist         : FUZZ: /usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-big.txt
 :: Extensions       : .html .js .php .log .zip .pdf 
 :: Output file      : scan-ffuf.txt
 :: File format      : json
 :: Follow redirects : true
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 64
 :: Matcher          : Response status: all
 :: Filter           : Response status: 404,502
 :: Filter           : Response size: 1337
________________________________________________

index.html              [Status: 200, Size: 1256, Words: 298, Lines: 47]   
```
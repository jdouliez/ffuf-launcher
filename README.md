# Ffuf Launcher

```

███████╗███████╗██╗   ██╗███████╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔════╝██╔════╝██║   ██║██╔════╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗
█████╗  █████╗  ██║   ██║█████╗      ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝
██╔══╝  ██╔══╝  ██║   ██║██╔══╝      ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗
██║     ██║     ╚██████╔╝██║         ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║
╚═╝     ╚═╝      ╚═════╝ ╚═╝         ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  

                                        By Ali@s (@JDouliez)
```
## Description

This tool is a simple ffuf wrapper which lets you select dynamically which wordlist and which extentions you want to fuzz with.

## Installation

Just install the python3 requirements...
```bash
$> pip3 install -r requirements.txt
```

... and make sure you have to right dependencies
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

                                        By Ali@s (@JDouliez)


usage: Ffuf Launcher [-h] URL [ARGS]

This tool lets you dynamically choose your wordlist and your extension list to fuzz. Because each website is different.

positional arguments:
  URL         The url to fuzz.
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

                                        By Ali@s (@JDouliez)


[?] Which wordlist do you want to fuzz with?: directory-list-2.3-medium.txt
   directory-list-2.3-small.txt
 > directory-list-2.3-medium.txt
   directory-list-2.3-big.txt
   Bo0oM-fuzz.txt
   onelistforallmicro.txt
   jhaddix_content_discovery_all.txt
   Custom list

[?] What extensions do you want to fuzz?: 
   [X] .php
   [ ] .log
   [ ] .zip
   [X] .sql
   [ ] .txt
   [ ] .pdf
 > [X] .xml
   [ ] .conf
   [ ] .cfg
   [ ] .json
   [ ] .asp
   [ ] .aspx
   [ ] .jsp

[*] Running command "ffuf -c -r -w /usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt -o scan-ffuf-example.com.txt -e .html,.js,.php,.sql,.xml -t 64 -mc all -fc 404 -u http://example.com/FUZZ -fc 404,502 -fs 1337"

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
 :: Wordlist         : FUZZ: /usr/share/SecLists/Discovery/Web-Content/directory-list-2.3-medium.txt
 :: Extensions       : .html .js .php .sql .xml 
 :: Output file      : scan-ffuf-example.com.txt
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

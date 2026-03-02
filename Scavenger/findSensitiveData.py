import datetime
import os
import sys
from os import listdir
from os.path import isfile, join
import classes.utility
from colorama import Fore, Style
import shutil

if len(sys.argv) < 2:
    print("Usage: python findSensitiveData.py <raw_paste_folder>")
    sys.exit(1)

raw_paste_folder = sys.argv[1]
if not os.path.isdir(raw_paste_folder):
    print(Fore.RED + f"Folder not found: {raw_paste_folder}" + Style.RESET_ALL)
    sys.exit(1)

rawfiles = [f for f in listdir(raw_paste_folder) if isfile(join(raw_paste_folder, f))]
count = 0
gCount = 0
tools = classes.utility.ScavUtility()
searchTerms = tools.loadSearchTerms()

print(Fore.YELLOW + str(datetime.datetime.now()) + ": [+] Fetched files from " + raw_paste_folder + Style.RESET_ALL)

for file in rawfiles:
    fpath = os.path.join(raw_paste_folder, file)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        curFileContent = f.readlines()

    foundPassword = 0
    foundSensitiveData = 0
    sensitiveValue = ""

    for line in curFileContent:
        line = line.strip()
        if "@" in line and ":" in line:
            parts = line.split(":")
            if len(parts) == 2:
                parts[0] = parts[0].strip()
                parts[1] = parts[1].strip()
                if "@" in parts[0]:
                    if tools.check(parts[0]) == 1:
                        password = parts[1].split(" ")[0]
                        password = password.split("|")[0]
                        if password == "" or len(password) < 4 or len(password) > 40:
                            continue
                        else:
                            foundPassword = 1
                    else:
                        continue
                else:
                    continue
            else:
                continue

        for searchItem in searchTerms:
            if searchItem in line:
                foundSensitiveData = 1
                sensitiveValue = searchItem

    if foundPassword == 1:
        print(Fore.GREEN + str(datetime.datetime.now()) + ": [+] Found credentials. Saving to data/files_with_passwords/" + Style.RESET_ALL)
        os.makedirs(os.path.join('data', 'files_with_passwords'), exist_ok=True)
        shutil.copy(fpath, os.path.join('data', 'files_with_passwords', file))
        with open(os.path.join('logs', 'findSensitiveData_credentials.log'), 'a', encoding='utf-8', errors='ignore') as lf:
            lf.write(fpath + "\n")
    elif foundSensitiveData == 1:
        print(Fore.GREEN + str(datetime.datetime.now()) + ": [+] Found other sensitive data. Saving to data/otherSensitivePastes/" + Style.RESET_ALL)
        os.makedirs(os.path.join('data', 'otherSensitivePastes'), exist_ok=True)
        shutil.copy(fpath, os.path.join('data', 'otherSensitivePastes', file))
        with open(os.path.join('logs', 'findSensitiveData_othersensitivedata.log'), 'a', encoding='utf-8', errors='ignore') as lf:
            lf.write(fpath + " - matched keyword: " + sensitiveValue + "\n")

    if count == 1000:
        count = 0
        print(Fore.YELLOW + str(datetime.datetime.now()) + "[+] Proccessed " + str(gCount) + " pastes." + Style.RESET_ALL)
    count += 1
    gCount += 1

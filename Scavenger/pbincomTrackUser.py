import os
import datetime
from bs4 import BeautifulSoup, SoupStrainer
import requests
import time
import classes.utility
from colorama import Fore, Style
import shutil

tools = classes.utility.ScavUtility()
session = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0"}
searchTerms = tools.loadSearchTerms()

iterator = 1
while True:
    print(str(datetime.datetime.now()) + ": [#] Archiving pastes...")
    print()
    tools.archivepastes(os.path.join('data', 'raw_pastes'))

    print(str(datetime.datetime.now()) + ": [#] " + str(iterator) + ". iterator")
    # read all relevant users
    users_path = os.path.join('configs', 'users.txt')
    with open(users_path, 'r', encoding='utf-8', errors='ignore') as f:
        relevantUsers = f.readlines()

    # go through users and store paste IDs
    for user in relevantUsers:
        try:
            user = user.strip()
            if not user:
                continue
            print(str(datetime.datetime.now()) + ": [#] Getting pastes for user " + Fore.GREEN + user + Style.RESET_ALL)
            response = session.get("https://pastebin.com/u/" + user, headers=headers)
            response = response.text

            skipcount = 0
            existsCounter = 0
            for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
                if not hasattr(link, 'has_attr'):
                    continue
                if "HTML" not in str(link) and "html" not in str(link):
                    if link.has_attr('href'):
                        href = link['href']
                        if len(href) == 9 and href.startswith('/') and href not in ['/messages', '/settings', '/scraping'] and '/u/' not in href:
                            if skipcount <= 7:
                                skipcount += 1
                                continue

                            link_id = href.lstrip('/')
                            # check if paste already scraped
                            already_logged = False
                            log_path = os.path.join('logs', 'alreadytrackedpastes.log')
                            if os.path.exists(log_path):
                                with open(log_path, 'r', encoding='utf-8', errors='ignore') as lg:
                                    for line in lg:
                                        if link_id in line:
                                            already_logged = True
                                            break
                            if already_logged:
                                existsCounter += 1
                                continue

                            # get paste and store it
                            print(Fore.YELLOW + str(datetime.datetime.now()) + ": [*] Crawling " + href + Style.RESET_ALL)
                            curPaste = session.get("https://pastebin.com/raw/" + link_id, headers=headers)
                            curPaste = curPaste.text
                            raw_path = os.path.join('data', 'raw_pastes', link_id)
                            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
                            with open(raw_path, 'w', encoding='utf-8', errors='ignore') as f:
                                f.write(str(curPaste))

                            with open(log_path, 'a', encoding='utf-8', errors='ignore') as lg:
                                lg.write(link_id + "\n")

                            # get the juicy stuff
                            foundPassword = 0
                            foundSensitiveData = 0
                            sensitiveValue = ""

                            with open(raw_path, 'r', encoding='utf-8', errors='ignore') as f:
                                fiContent = f.readlines()

                            for line in fiContent:
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
                                shutil.copy(raw_path, os.path.join('data', 'files_with_passwords', link_id))
                            elif foundSensitiveData == 1:
                                destname = sensitiveValue + "_" + link_id
                                print(Fore.GREEN + str(datetime.datetime.now()) + ": [+] Found other sensitive data. Saving to data/otherSensitivePastes/" + Style.RESET_ALL)
                                shutil.copy(raw_path, os.path.join('data', 'otherSensitivePastes', destname))

                            print(str(datetime.datetime.now()) + ": [#] Waiting 20s till next paste scrape...")
                            time.sleep(20)
            print(Fore.RED + str(datetime.datetime.now()) + ": [-] Skipped " + str(existsCounter) + " pastes (reason: already crawled)" + Style.RESET_ALL)
            print(str(datetime.datetime.now()) + ": [#] Waiting 10 minutes till next user check... ")
            print()
            time.sleep(600)
        except Exception as e:
            print(Fore.RED + str(e) + Style.RESET_ALL)

    iterator += 1
    print(str(datetime.datetime.now()) + ": [#] Waiting 3 hours till next iteration...")
    print()
    time.sleep(10800)

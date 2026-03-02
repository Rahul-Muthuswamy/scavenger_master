import random
import time
import datetime
import os
import requests
from bs4 import BeautifulSoup, SoupStrainer
import classes.utility
from colorama import Fore, Style
import shutil

iterator = 1
tools = classes.utility.ScavUtility()
session = requests.session()
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0"}
searchTerms = tools.loadSearchTerms()


def getjuicystuff(tmpresponse):
    existscounter = 0
    for link in BeautifulSoup(tmpresponse, 'html.parser', parse_only=SoupStrainer('a')):
        # BeautifulSoup sometimes yields strings; ensure we have a tag
        if not hasattr(link, 'has_attr'):
            continue
        if "HTML" not in str(link):
            if link.has_attr('href'):
                href = link['href']
                if len(href) == 9 and href.startswith('/') and href not in ['/messages', '/settings', '/scraping']:
                    link_id = href.lstrip('/')
                    raw_path = os.path.join('data', 'raw_pastes', link_id)
                    if os.path.exists(raw_path):
                        existscounter += 1
                        continue
                    print(Fore.YELLOW + str(datetime.datetime.now()) + ": [*] Crawling " + href + Style.RESET_ALL)
                    binresponse = session.get("https://pastebin.com/raw/" + link_id, headers=headers, timeout=5)
                    binresponse = binresponse.text
                    try:
                        foundpassword = 0
                        foundsensitivedata = 0
                        sensitivevalue = ""

                        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
                        with open(raw_path, "wb") as file_:
                            file_.write(binresponse.encode('utf-8').strip())

                        with open(raw_path, "r", encoding='utf-8', errors='ignore') as f:
                            ficontent = f.readlines()

                        for line in ficontent:
                            line = line.strip()
                            if "@" in line and ":" in line:
                                parts = line.split(":" )
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
                                                foundpassword = 1
                                        else:
                                            continue
                                    else:
                                        continue
                                else:
                                    continue

                            for searchItem in searchTerms:
                                if searchItem in line:
                                    foundsensitivedata = 1
                                    sensitivevalue = searchItem

                        if foundpassword == 1:
                            print(Fore.GREEN + str(datetime.datetime.now()) + ": [+] Found credentials. Saving to data/files_with_passwords/" + Style.RESET_ALL)
                            shutil.copy(raw_path, os.path.join('data', 'files_with_passwords', link_id))
                        elif foundsensitivedata == 1:
                            destname = sensitivevalue + "_" + link_id
                            print(Fore.GREEN + str(datetime.datetime.now()) + ": [+] Found other sensitive data (" + sensitivevalue + "). Saving to data/otherSensitivePastes/" + Style.RESET_ALL)
                            shutil.copy(raw_path, os.path.join('data', 'otherSensitivePastes', destname))

                        time.sleep(random.randint(5, 10))
                    except Exception as eErr:
                        print(str(datetime.datetime.now()) + ": [-] " + Fore.RED + str(eErr) + Style.RESET_ALL)
                        continue
    print(Fore.RED + str(datetime.datetime.now()) + ": [-] Skipped " + str(existscounter) + " pastes (reason: already crawled)" + Style.RESET_ALL)


print(str(datetime.datetime.now()) + ": [#] Using slow website scraping to gather pastes")
print()
while True:
    print(str(datetime.datetime.now()) + ": [#] Archiving pastes...")
    tools.archivepastes(os.path.join('data', 'raw_pastes'))
    print(str(datetime.datetime.now()) + ": [#] " + str(iterator) + ". iterator:")
    iterator += 1
    try:
        response = session.get("https://pastebin.com/archive", headers=headers, timeout=5)
        response = response.text
        time.sleep(5)
        getjuicystuff(response)
        print(str(datetime.datetime.now()) + ": [#] Waiting 300 seconds...")
        print()
        time.sleep(300)
    except Exception as e:
        print(Fore.RED + str(datetime.datetime.now()) + ": CRITICAL ERROR" + Style.RESET_ALL)
        print(Fore.RED + str(datetime.datetime.now()) + ": [-] " + str(e) + Style.RESET_ALL)
        time.sleep(300)
        continue

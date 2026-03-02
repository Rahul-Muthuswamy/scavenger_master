#!/usr/bin/python

import time
import re
import os
import zipfile
import shutil


class ScavUtility:
    def __init__(self):
        pass

    def check(self, email):
        regex = '^(?=.{1,64}@)[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)*@[^-][A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*(\.[A-Za-z]{2,})$'
        if (re.search(regex, email)):
            return 1
        else:
            return 0

    def loadSearchTerms(self):
        searchterms = set()
        path = os.path.join('configs', 'searchterms.txt')
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            tmpcontent = f.readlines()

        for tmpline in tmpcontent:
            tmpline = tmpline.strip()
            if tmpline:
                searchterms.add(tmpline)
        return searchterms

    def archivepastes(self, directory):
        if not os.path.isdir(directory):
            return
        pastecount = len([name for name in os.listdir(directory) if os.path.isfile(os.path.join(directory, name))])
        if pastecount > 48000:
            timestamp = str(int(time.time()))
            archivefilename = f"pastebin_{timestamp}.zip"
            archive_path = os.path.join('archive', archivefilename)
            os.makedirs('archive', exist_ok=True)
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(directory):
                    for file in files:
                        fullpath = os.path.join(root, file)
                        arcname = os.path.relpath(fullpath, start=directory)
                        zf.write(fullpath, arcname=arcname)

            # remove files in directory
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                try:
                    if os.path.isfile(filepath) or os.path.islink(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                except Exception:
                    pass

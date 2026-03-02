# Run instructions (Windows)

Prereqs:
- Python 3.8+ installed
- Recommended: run inside WSL or Git Bash for best compatibility. Windows native is supported after these compatibility changes.

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

Create required folders:
```bash
mkdir -p data/raw_pastes data/files_with_passwords data/otherSensitivePastes logs archive
```

Run modules:
- Start archive scraper in background:
```powershell
python scavenger.py -0
```
- Start user tracker in background:
```powershell
python scavenger.py -1
```
- Scan specific folder for sensitive data:
```powershell
python scavenger.py -2
# then provide the folder path when prompted
```

Direct module run (no background):
```powershell
python pbincomArchiveScrape.py
python pbincomTrackUser.py
python findSensitiveData.py data/raw_pastes
```

Notes:
- Scripts now use Python-native file operations and should run on Windows and Unix.
- Long-running scraping of Pastebin may be subject to rate limits and terms of service. Use responsibly.

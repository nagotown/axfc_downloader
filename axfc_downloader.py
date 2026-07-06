import sys
import requests as req
from pathlib import Path
from bs4 import BeautifulSoup as bs
import logging as log

pydir = Path(__file__).parent

log.basicConfig(level=log.INFO,
                filename=Path.joinpath(pydir, "axfcdl.log"),
                encoding="utf-8",
                filemode="a",
                format="{asctime} {levelname}: {message}", 
                style="{", 
                datefmt="%Y-%m-%d %H:%M")

print("==== Axfc Downloader ====")

# base page (ex. https://www.axfc.net/u/3939393&key=PASSWORD)
s = req.Session()
baseurl = input("Enter Acfx download link: ")
idcount = [c.isdigit() for c in baseurl].count(True)

if "axfc.net/u" not in baseurl or idcount < 2:
    log.error(f"User entered invalid Axfc link: {baseurl}")
    print("Not a valid Axfc link. Aborting.")
    input("Press Enter to exit...")
    sys.exit()
else:
    log.info(f"User entered valid Axfc link: {baseurl}")

response = s.get(baseurl)

soup = bs(response.text, "html.parser")

# get filename for file to download. used later
find_names = soup.find("div", class_="comme")
filename = find_names.find_all("p")[1].string

# get password (keyword internally), sid, dqn. needed to actually be able to download
password = None
sid = None
dqn = None

for v in soup.find_all("input"):
    inputs = str(v)
    keyword = "name=\"keyword\""
    sidv = "name=\"sid\""
    dqnv = "name=\"dqn\""
    if keyword in inputs:
        keywordstatus = True
        password = v.get("value")
        if password:
            log.info(f"Password in URL: {password}")
        elif not password:
            log.info("No password in url, asking user for password input...")
            password = input("This file requires a password to download.\nEnter password: ")
            log.info(f"User entered password: {password}")
            baseurl = baseurl + "&key=" + password
            if password == "":
                log.error("User did not enter password")
                print("You can't download this file without a password. Aborting.")
                input("Press Enter to exit...")
                sys.exit()
        else: continue
    elif sidv in inputs:
        sid = v.get("value")
        log.info(f"sid value: {sid}")
    elif dqnv in inputs:
        dqn = v.get("value")
        log.info(f"dqn value: {dqn}")
    else: continue

# button -> dl2.pl (https://axfc.net/u/dl2.pl)
dl2 = "https://www.axfc.net/u/dl2.pl"
dl2_response = s.post(dl2, data={"keyword": password, "sid": sid, "dqn": dqn})
dl2_soup = bs(dl2_response.text, "html.parser")

# get dr value
dr = None

for l in dl2_soup.find_all("a"):
    inputssl2 = str(l)
    drv = "href=\"./link.pl"
    if drv in inputssl2:
        dr = l.get("href")
        log.info(f"dr value: {dr.split("=")[1]}")

if dr == None:
    log.error("User entered incorrect password")
    print("Password is incorrect. Aborting.")
    input("Press Enter to exit...")
    sys.exit()

# dl2.pl -> link.pl (ex. https://www.axfc.net/u/link.pl?dr=YCnAh2hklnT1DsLrOGuh9TrAkgmi9P63)
# ^ skipped as it's not needed

# link.pl -> actual download (ex. https://aquarius.axfc.net/d/YCnAh2hklnT1DsLrOGuh9TrAkgmi9P63)
subdomains = []
subdomainpath = pydir / "subdomains.txt"

if subdomainpath.is_file():
    log.info("subdomains.txt exists")
    with open(subdomainpath, "r") as f:
        for line in f:
            if not line.strip() or line.strip().startswith("#"):
                continue
            else: 
                subdomains.append(line.strip())
else:
    log.info("subdomains.txt does not exist. Setting defaults.")
    subdomains = [
        # zodiac
        "aries",
        "taurus",
        "gemini",
        "cancer",
        "leo",
        "virgo",
        "libra",
        "scorpio",
        "sagittarius",
        "capricornus",
        "capricomus",
        "aquarius",
        "pisces",
        # primates
        "ape",
        "chimpanzee",
        "gorilla",
        "monkey",
        # sea creatures
        "capelin",
        "crab",
        "mackerel",
        "scallop",
        "shark",
        # rocks (gemstones)
        "amber",
        "aquamarine",
        "diamond",
        "emerald",
        "garnet",
        "opal",
        "pearl",
        "peridot",
        "ruby",
        "saffron",
        "sapphire",
        # rocks (seasoning)
        "salt",
        "pepper"
        # planets
        "mercury",
        "venus",
        "earth",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        # mythological but not a planet
        "fenrir"
        ]

# the downloading part
dlfolder = Path(pydir, "download")
dlfolder.mkdir(exist_ok=True)
dlfile = Path(dlfolder, str(filename))

print("Checking subdomains...")

for sub in subdomains:
    downloadlink = "https://" + sub + ".axfc.net/d/" + str(dr.split("=")[1])
    try:
        if dlfile.exists() == False:
            dl = s.get(downloadlink)
            dl.raise_for_status()
            with open(dlfile, mode="wb") as f:
                log.info(f"Downloading {filename}")
                print(f"Downloading {filename}...")
                f.write(dl.content)
            print(f"OK: {downloadlink}")
        else: print(f"{filename} already exists.")
    except:
        log.error(f"Download from {sub} failed")
        print(f"ERROR: {downloadlink}")
    if dlfile.exists():
        log.info(f"{filename} downloaded")
        print(f"{filename} downloaded successfully.")
        break
if dlfile.exists() == False:
    log.error(f"{filename} was not downloaded")
    print(f"{filename} could not be downloaded.")

# Axfc Downloader

Axfc is very prone to not selecting the right subdomain to download from, if the file still exists on the server.

This tool tries to download from each of Axfc's subdomains and stops when successful.

Based on [AxfcTrySystem](https://github.com/stsaria/AxfcTrySystem), which does not work properly as of current due to not passing `keyword`, `sid`, `dqn`, and `dr` values required to actually download files.

## Requirements

Tested on Python `3.14.6`.  
Dependencies may work with other versions, but have not been tested.

`pip install requests==2.34.2 beautifulsoup4==4.15.0` 
or  
`pip install -r requirements.txt`


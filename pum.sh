#!/bin/bash

#export json from plex
python3 plex_api_share.py --backup

# import json to pum
python3 import_plex_users.py

#generate web page
python3 pum_web.py
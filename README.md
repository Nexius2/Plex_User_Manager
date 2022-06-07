# Plex_User_Manager

starting a tool to manage plex users because we can't make the difference between all of them now plex has decided to rename them. 
Also adding access expiration to stop user access when date passed.
I'd be glad to have some help with python and docker.

left to do:
- add pum_userID column and make it primary
- add new users based on userID and servername
- add configuration tab 
- in conf tab add mail conf to send mail before , when, and after account has expired
- in conf tab add cron option to sync plex db
- refresh main frame after each cron sync
- build docker container to run plex sync every cron schedule, display pum_web.py and ask for plex url and token (config.ini)

bugs:
- can't update user when one of the date is missing
- when updating user, main_fram does'nt update correctly
- in some cases forbiden entry box are white
- dockerfile asking for geographic area


Usage:
 - add plex url and token in .config/plexapi/config.ini
 - run pum.sh (or python3 plex_api_share.py --backup then python3 import_plex_users.py) with cron job every day
 - run python3 pum_web.py

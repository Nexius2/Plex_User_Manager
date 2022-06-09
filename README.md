# Plex_User_Manager

starting a tool to manage plex users because we can't make the difference between all of them now plex has decided to rename them. 
Also adding access expiration to stop user access when date passed.
I'd be glad to have some help with python and docker.

left to do:
- add pum_userID column and make it primary
- add new users based on userID and servername ( for multiple servers)
- in conf tab add mail conf to send mail before , when, and after account has expired
- in conf tab add cron option to sync plex db
- refresh main frame after each cron sync
- build docker container to run plex sync every cron schedule, display pum_web.py and ask for plex url and token (config.ini)

bugs:
- checkbox not aligned in conf tab
- when selecting help & info selection touring appears (focus)

Usage:
 - add plex url and token in .config/plexapi/config.ini
 - run pum.sh (or python3 plex_api_share.py --backup then python3 import_plex_users.py) with cron job every day
 - run python3 pum_web.py
 
![screen](https://user-images.githubusercontent.com/9554635/172479259-af074417-b187-4483-8e98-91dde70861ba.png)

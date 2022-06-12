# Plex User Manager

starting a tool to manage plex users because we can't make the difference between all of them now plex has decided to rename them. 
Also adding access expiration to stop user access when date passed.
I'd be glad to have some help with python and docker.

left to do:
- display server number in plex info
- in conf tab 
  * add mail conf to send mail before
  * add cron option to sync plex
  * warn users near expiation (with delay)
  * warn user of expiration
  * remove access when expired
  * delete user when expired (with delay)
  * hide guest
  * add plex token and IP
- build docker container to run plex sync every cron schedule, display pum_web.py and ask for plex url and token (config.ini)
- add help text

bugs:
- checkbox not aligned in conf tab
- when selecting help & info selection touring appears (focus)
- updating message not visible when syncing
- filters not displaying

Usage:
 - add plex url and token in .config/plexapi/config.ini
 - run python3 sync.py with cron job every day
 - run python3 pum_web.py
 
![screen](https://user-images.githubusercontent.com/9554635/172479259-af074417-b187-4483-8e98-91dde70861ba.png)

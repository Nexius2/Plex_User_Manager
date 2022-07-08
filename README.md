# Plex User Manager

Tool to manage plex users because we can't make the difference between all of them now plex has decided to rename them. 
Also adding access expiration to stop user access when date passed.
I'd be glad to have some help with python and docker(GitHub).

left to do:
- in conf tab buttons are done functions not yet working
  * add mail conf to send mail before
  * warn users near expiation (with delay / mail)
  * warn user of expiration (mail)
  * delete user when expired (with delay)
- build docker container to run plex sync every cron schedule, display pum_web.py and ask for plex url and token (config.ini)
- add help text
- add CHANGES to info tab

bugs:
- minor gui diplay glitch

Usage:
 - run python3 pum.py
 
![screen](https://user-images.githubusercontent.com/9554635/172479259-af074417-b187-4483-8e98-91dde70861ba.png)

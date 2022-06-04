# Plex_User_Manager

starting a tool to manage my plex users because I can't make the difference between all of them now plex has decided to rename them

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



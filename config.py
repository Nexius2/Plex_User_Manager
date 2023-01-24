from configparser import ConfigParser


# global config_path
config_path = ".config/"
api_path = "api/"

# Read config.ini file
config_object = ConfigParser()
config_object.read(config_path + "pum.ini")

userinfo = config_object["CONF"]
warn_user_near_expiration = userinfo["warn_user_near_expiration"]
warn_user_near_expiration_delay = userinfo["warn_user_near_expiration_delay"]
warn_user_account_expiration = userinfo["warn_user_account_expiration"]
remove_user_access = userinfo["remove_user_access"]
delete_user = userinfo["delete_user"]
delete_user_delay_str = userinfo["delete_user_delay"]
plex_db_sync_str = userinfo["plex_db_sync"]
hide_guest_str = userinfo["hide_guest"]
hide_no_lib_users_str = userinfo["hide_no_lib_users"]
# cron_conf_str = userinfo["cron_conf"]
nbr_backup_to_keep_str = userinfo["nbr_backup_to_keep"]
sync_plex_delai = userinfo["sync_plex_delai"]
config_object = ConfigParser()
config_object.read(config_path + "pum.ini")
userinfo = config_object["DATABASE"]
db_host = userinfo["host"]
db_user = userinfo["user"]
db_passwd = userinfo["passwd"]
db_db = userinfo["db"]


from configparser import ConfigParser
import mysql.connector
import sys

# Read config.ini file
config_object = ConfigParser()
config_object.read("../.config/pum.ini")
# Get the conf info
userinfo = config_object["DATABASE"]
db_host = userinfo["host"]
db_user = userinfo["user"]
db_passwd = userinfo["passwd"]
db_db = userinfo["db"]
# Get the conf info
userinfo = config_object["CONF"]
warn_user_near_expiration = userinfo["warn_user_near_expiration"]
warn_user_near_expiration_delay = userinfo["warn_user_near_expiration_delay"]
warn_user_account_expiration = userinfo["warn_user_account_expiration"]
remove_user_access = userinfo["remove_user_access"]
delete_user = userinfo["delete_user"]
delete_user_delay = userinfo["delete_user_delay"]
plex_db_sync = userinfo["plex_db_sync"]
hide_guest = userinfo["hide_guest"]

# connect to MySQL
mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_db,
        auth_plugin='mysql_native_password')

# Create a cursor and initialize it
cursor = mydb.cursor()

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS pum")

# Create table
cursor.execute("CREATE TABLE IF NOT EXISTS plexusers(first_name VARCHAR(255), \
     last_name VARCHAR(255), \
     username VARCHAR(255) NOT NULL, \
     email VARCHAR(255) NOT NULL, \
     serverName VARCHAR(255) NOT NULL, \
     account_expire_date DATE, \
     sections VARCHAR(255), \
     allowSync VARCHAR(10), \
     camera VARCHAR(10), \
     channels VARCHAR(10),  \
     filterMovies VARCHAR(255) DEFAULT NULL, \
     filterMusic VARCHAR(255) DEFAULT NULL, \
     filterTelevision VARCHAR(255) DEFAULT NULL, \
     title VARCHAR(255), \
     is_on_plex INT(10), \
     account_creation_date DATE, \
     account_renewed_date DATE, \
     userID INT NOT NULL, \
     description VARCHAR(255), \
     PRIMARY KEY(userID, serverName) );")

# Create table tempusers
cursor.execute("CREATE TABLE IF NOT EXISTS tempusers(serverName VARCHAR(255) NOT NULL, \
     userID INT NOT NULL, \
     PRIMARY KEY(userID, serverName) );")

#export json from plex
# print(sys.argv)
script_descriptor = open("plex_api_share.py")
a_script = script_descriptor.read()
sys.argv = ["plex_api_share.py", "--backup"]
exec(a_script)
script_descriptor.close()

# import json to pum
exec(open("./api/import_plex_users.py").read())

# warn user near expiration
if warn_user_near_expiration == "1":
        sql_plexusers_expired_account = "SELECT userID FROM plexusers WHERE ISNULL(account_expire_date) = 0 AND DATEDIFF (CURDATE(),account_expire_date) < %s;" % (warn_user_near_expiration_delay)
        cursor.execute(sql_plexusers_expired_account)
        results = cursor.fetchall()
        print(results)
        # for all results send mail to warn account is about to end

# warn and delete expired accounts
if warn_user_account_expiration == "1":
        # select all expired users
        sql_plexusers_expired_account = "SELECT userID FROM plexusers WHERE ISNULL(account_expire_date) = 0 AND DATEDIFF (CURDATE(),account_expire_date) > 0;"
        cursor.execute(sql_plexusers_expired_account)
        results = cursor.fetchall()
        print(results)
        # send mail
        #for all results run plex_api_share.py --unshare --user USER
        #send mail to warn account has ended

# Remove user access
if remove_user_access =="1":
        exec(open("./api/remove_user_access.py").read())


#remove user with is_on_plex = null
sql_plexusers_remove_old_accounts = "DELETE FROM plexusers WHERE is_on_plex = 0;"
cursor.execute(sql_plexusers_remove_old_accounts)

# Commit changes
mydb.commit()
# Close connexion
mydb.close()
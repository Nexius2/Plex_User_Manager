#import os
#print(os.getcwd())
#import subprocess
import mysql.connector
from configparser import ConfigParser

#Read config.ini file
config_object = ConfigParser()
config_object.read(".config/pum.ini")

#Get the conf info
userinfo = config_object["DATABASE"]
db_host = userinfo["host"]
#print("host is {}".format(userinfo["host"]))
db_user = userinfo["user"]
#print("user is {}".format(userinfo["user"]))
db_passwd = userinfo["passwd"]
#print("password is {}".format(userinfo["passwd"]))
db_db = userinfo["db"]

# connect to MySQL
mydb = mysql.connector.connect(
        host = db_host,
        user = db_user,
        passwd = db_passwd,
        database = db_db,
    )
# Check to see if connection to MySQL was created
# print(mydb)

# Create a cursor and initialize it
my_cursor = mydb.cursor()

# Create database if not exists
my_cursor.execute("CREATE DATABASE IF NOT EXISTS pum")

# Create table
my_cursor.execute("CREATE TABLE IF NOT EXISTS plexusers(userID INT NOT NULL, \
     username VARCHAR(255) NOT NULL, \
     email VARCHAR(255) NOT NULL, \
     sections VARCHAR(255), \
     serverName VARCHAR(255), \
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
     account_expire_date DATE, \
     first_name VARCHAR(255), \
     last_name VARCHAR(255), \
     description VARCHAR(255), \
     PRIMARY KEY(userID) );")





#export json from plex
import sys
print(sys.argv)
script_descriptor = open("plex_api_share.py")
a_script = script_descriptor.read()
sys.argv = ["plex_api_share.py", "--backup"]
exec(a_script)
script_descriptor.close()

# import json to pum
exec(open("import_plex_users.py").read())

#generate gui page
#exec(open("pum_web.py").read())





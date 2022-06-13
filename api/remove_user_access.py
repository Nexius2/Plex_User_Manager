from configparser import ConfigParser
import mysql.connector
import sys
import os

# Read config.ini file
config_object = ConfigParser()
config_object.read(".config/pum.ini")
# Get the conf info
userinfo = config_object["DATABASE"]
db_host = userinfo["host"]
db_user = userinfo["user"]
db_passwd = userinfo["passwd"]
db_db = userinfo["db"]

# connect to MySQL
mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_db,
        auth_plugin='mysql_native_password')

# Create a cursor and initialize it
cursor = mydb.cursor()

# get all expired users
sql_plexusers_expired_account = "SELECT username FROM plexusers WHERE ISNULL(account_expire_date) = 0 AND DATEDIFF (CURDATE(),account_expire_date) > 0;"
cursor.execute(sql_plexusers_expired_account)
results = cursor.fetchall()
for result in results:
        #print(result)
        #print(sys.argv)
        # To find path
        import plexapi

        print(plexapi.CONFIG_PATH)

        script_descriptor = open("./plex_api_share.py")
        a_script = script_descriptor.read()
        sys.argv = ["plex_api_share.py", "--unshare", "--user", result[0]]
        print(os.path.abspath(__file__))
        print(sys.argv)
        exec(a_script)
        script_descriptor.close()




# Commit changes
mydb.commit()
# Close connexion
mydb.close()
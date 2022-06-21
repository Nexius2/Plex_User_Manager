from configparser import ConfigParser
import mysql.connector
from plexapi.server import PlexServer, CONFIG
from requests import Session
import sys
import os
PLEX_URL = ''
PLEX_TOKEN = ''
# Read config.ini file
config_object = ConfigParser()
config_object.read(".config/pum.ini")
# Get the conf info
userinfo = config_object["DATABASE"]
db_host = userinfo["host"]
db_user = userinfo["user"]
db_passwd = userinfo["passwd"]
db_db = userinfo["db"]
userinfo = config_object["CONF"]
delete_user_delay_str = userinfo["delete_user_delay"]

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
sql_plexusers_expired_account = "SELECT userID FROM plexusers WHERE DATEDIFF (CURDATE(),account_expire_date) > %s;" % (delete_user_delay_str)
cursor.execute(sql_plexusers_expired_account,)
results = cursor.fetchall()
for result in results:
        #print(result)
        #print(sys.argv)
        # To find path
        import plexapi
        PLEX_URL = PLEX_URL or CONFIG.data['auth'].get('server_baseurl')
        PLEX_TOKEN = PLEX_TOKEN or CONFIG.data['auth'].get('server_token')
        # TAUTULLI_URL = TAUTULLI_URL or CONFIG.data['auth'].get('tautulli_baseurl')
        # TAUTULLI_APIKEY = TAUTULLI_APIKEY or CONFIG.data['auth'].get('tautulli_apikey')
        # USERNAME_IGNORE = [username.lower() for username in USERNAME_IGNORE]
        SESSION = Session()
        # Ignore verifying the SSL certificate
        SESSION.verify = False  # '/path/to/certfile'
        # If verify is set to a path to a directory,
        # the directory must have been processed using the c_rehash utility supplied with OpenSSL.
        if not SESSION.verify:
                # Disable the warning that the request is insecure, we know that...
                from urllib3 import disable_warnings
                from urllib3.exceptions import InsecureRequestWarning
                disable_warnings(InsecureRequestWarning)
        SERVER = PlexServer(baseurl=PLEX_URL, token=PLEX_TOKEN, session=SESSION)
        ACCOUNT = SERVER.myPlexAccount()
        PLEX_USERS = {user.id: user.title for user in ACCOUNT.users()}
        PLEX_USERS.update({int(ACCOUNT.id): ACCOUNT.title})
        UID = result[0]
        print(result)
        print(result[0])
        print(ACCOUNT.id)
        print(ACCOUNT.title)
        print(ACCOUNT.users)
        #ACCOUNT.removeFriend(PLEX_USERS[UID])
        '''
        print(plexapi.CONFIG_PATH)
        script_descriptor = open("./plex_api_share.py")
        a_script = script_descriptor.read()
        sys.argv = ["plex_api_share.py", "--unshare", "--user", result[0]]
        print(os.path.abspath(__file__))
        print(sys.argv)
        exec(a_script)
        script_descriptor.close()
        '''




# Commit changes
mydb.commit()
# Close connexion
mydb.close()
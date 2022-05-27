
import pymysql
import os
import json
import glob
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

path_to_json = glob.glob(r'*.json')
#print(path_to_json)

#check json file
if not path_to_json:
    print("No JSON files... exiting")
    quit()

#load json
json_data = open(path_to_json[0]).read()
json_obj = json.loads(json_data)

# do validation and checks before insert
def validate_string(val):
   if val != None:
        if type(val) is int:
            #for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            return val

# connect to MySQL
con = pymysql.connect(host = db_host,user = db_user,passwd = db_passwd,db = db_db)
cursor = con.cursor()

#set is_on_plex to null
sql_plexusers_is_on_plex_reset = "UPDATE plexusers SET is_on_plex = 0;"
cursor.execute(sql_plexusers_is_on_plex_reset,)

#remove not wanted characters
for mydict in json_obj:
    placeholders = ', '.join(['%s'] * len(mydict))
    columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in mydict.keys())
    values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict.values())
    sections = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict['sections'])
    sections = sections.replace("'", '')
    sections = sections.replace(",", ' &')

    #add plex userID info to plexusers db
    sql_plexusers_import = "INSERT IGNORE INTO plexusers ( userID, account_creation_date ) VALUES ( %s, CURDATE() );" % (mydict['userID'])
    cursor.execute(sql_plexusers_import,)
    #update plex user info to plexusers db
    sql_plexusers_import2 = "UPDATE %s SET username = '%s', email = '%s', serverName = '%s', allowSync = '%s', camera = '%s', channels = '%s', filterMovies = '%s', filterMusic = '%s', filterTelevision = '%s', title = '%s', sections = '%s' WHERE userID = '%s';" % ('plexusers', mydict['username'], mydict['email'], mydict['serverName'], mydict['allowSync'], mydict['camera'], mydict['channels'], mydict['filterMovies'], mydict['filterMusic'], mydict['filterTelevision'], mydict['title'], sections, mydict['userID'])
    cursor.execute(sql_plexusers_import2,)
    #set is_on_plex to 1 if user is on plex export
    sql_plexusers_is_on_plex_set = "UPDATE plexusers SET is_on_plex = 1 WHERE userID = %s;" % (mydict['userID'])
    cursor.execute(sql_plexusers_is_on_plex_set,)

#remove user with is_on_plex = null
sql_plexusers_remove_old_accounts = "DELETE FROM plexusers WHERE is_on_plex = 0;"
cursor.execute(sql_plexusers_remove_old_accounts)

#select all expired users
sql_plexusers_expired_account = "SELECT userID FROM plexusers WHERE ISNULL(account_expire_date) = 0 AND DATEDIFF (CURDATE(),account_expire_date) > 0;"
cursor.execute(sql_plexusers_expired_account)
results = cursor.fetchall()
print(results)
#for all results run plex_api_share.py --unshare --user USER
#send mail to warn account has ended

#warn all soon expired users
sql_plexusers_expired_account = "SELECT userID FROM plexusers WHERE ISNULL(account_expire_date) = 0 AND DATEDIFF (CURDATE(),account_expire_date) < 30;"
cursor.execute(sql_plexusers_expired_account)
results = cursor.fetchall()
print(results)
#for all results send mail to warn account is about to end

#close connexion
con.commit()
con.close()

#delete old json file
os.remove(str(''.join(path_to_json)))



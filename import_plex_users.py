
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

#delete old table
sql_delete = "TRUNCATE TABLE plexusers"
cursor.execute(sql_delete)

for mydict in json_obj:
    placeholders = ', '.join(['%s'] * len(mydict))
    #print(mydict)
    columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in mydict.keys())
    #mydict["sections"] = 
    values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict.values())
    values = ', '.join("'" + str(x).replace("'", '') + "'" for x in mydict.values())
    #print(values)
    sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('plexusers', columns, values)
    cursor.execute(sql,)

#close connexion
con.commit()
con.close()

#delete old json file
os.remove(str(''.join(path_to_json)))



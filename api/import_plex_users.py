import pymysql
import os
import json
import glob
from configparser import ConfigParser


# Read config.ini file
config_object = ConfigParser()
config_object.read(".config/pum.ini")

# Get the conf info
userinfo = config_object["DATABASE"]
db_host = userinfo["host"]
db_user = userinfo["user"]
db_passwd = userinfo["passwd"]
db_db = userinfo["db"]

path_to_json = glob.glob(r'./*.json')

# check json file
if not path_to_json:
    print("No JSON files... exiting")
    quit()

# loop for every json file
for jfile in path_to_json:

    # load json
    json_data = open(jfile).read()
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

    # empty table tempusers
    sql_temp_import = "TRUNCATE TABLE tempusers;"
    cursor.execute(sql_temp_import)

    #remove not wanted characters
    for mydict in json_obj:
        placeholders = ', '.join(['%s'] * len(mydict))
        columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in mydict.keys())
        values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict.values())
        sections = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict['sections'])
        sections = sections.replace("'", '')
        sections = sections.replace(",", ' &')
        #print [re.sub('[^a-zA-Z0-9]+', '', _) for _ in mydict]
        filterMovies = ', '.join("'" + str(x).replace('/', '') + "'" for x in mydict['filterMovies'])
        filterMovies = filterMovies.replace("'", '')
        #print(filterMovies)
        #filterMovies = print(mydict.['filterMovies'])
        #print(filterMovies)
        #print(mydict.keys())
        #print(mydict['label'])
        #print(filterMovies)
        #filterMovies = filterMovies.replace(",", ' &')
        #print(filterMovies)
        #filterMovies = filterMovies.replace(":", '')
        filterMusic = ', '.join("'" + str(x).replace(':', '') + "'" for x in mydict['filterMusic'])
        filterMusic = filterMusic.replace("'", '')
        #filterMusic = filterMusic.replace(",", ' &')
        filterTelevision = ', '.join("'" + str(x).replace(':', '') + "'" for x in mydict['filterTelevision'])
        filterTelevision = filterTelevision.replace("'", '')
        #filterTelevision = filterTelevision.replace(",", ' &')
        #filterMovies = ', '.join("'" + str(x).replace(':', '') + "'" for x in mydict['filterMovies'])
        #filterMovies = print((mydict['filterMovies']))
        #filterMovies = filterMovies.replace(":", '')
        #.replace(":", '')
        #print(mydict['filterMovies'])

        #add plex userID info to plexusers db
        sql_plexusers_import = "INSERT IGNORE INTO plexusers ( userID, account_creation_date, serverName ) VALUES ( %s, CURDATE(), '%s' );" % (mydict['userID'], mydict['serverName'])
        cursor.execute(sql_plexusers_import,)
        #update plex user info to plexusers db
        sql_plexusers_import2 = "UPDATE %s SET username = '%s', email = '%s', allowSync = '%s', camera = '%s', channels = '%s', filterMovies = '%s', filterMusic = '%s', filterTelevision = '%s', title = '%s', sections = '%s' WHERE userID = '%s' AND serverName = '%s';" % ('plexusers', mydict['username'], mydict['email'], mydict['allowSync'], mydict['camera'], mydict['channels'], filterMovies, filterMusic, filterTelevision, mydict['title'], sections, mydict['userID'], mydict['serverName'])
        cursor.execute(sql_plexusers_import2,)
        #set is_on_plex to 1 if user is on plex export
        sql_plexusers_is_on_plex_set = "UPDATE plexusers SET is_on_plex = 1 WHERE userID = %s AND serverName = '%s';" % (mydict['userID'], mydict['serverName'])
        cursor.execute(sql_plexusers_is_on_plex_set,)

        # add to temp db to compare
        sql_temp_import = "INSERT IGNORE INTO tempusers ( userID, serverName ) VALUES ( %s, '%s' );" % (
            mydict['userID'], mydict['serverName'])
        cursor.execute(sql_temp_import, )

    # compare tempusers and plexusers and set plex_is_on to 0
    sql_compare_users = "UPDATE plexusers SET is_on_plex = 0 WHERE userID NOT in (SELECT userID FROM tempusers) AND serverName IN (SELECT serverName FROM tempusers);"
    cursor.execute(sql_compare_users)

    #close connexion
    con.commit()
    con.close()

    #delete old json file
    os.remove(str(''.join(jfile)))

# mark as synced
synced = open('./synced', "w")
synced.close()
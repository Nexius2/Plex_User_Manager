# **********************************************************************************************************************
# *************************************************** imports **********************************************************
# **********************************************************************************************************************
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from configparser import ConfigParser
from tkinter.messagebox import askyesno
import mysql.connector, os, sys, time
from plexapi.server import PlexServer
import requests
import plexapi
import glob
import json
import threading

# **********************************************************************************************************************
# ********************************************* GUI settings ***********************************************************
# **********************************************************************************************************************

root = Tk()
root.title('Plex User Manager')
root.geometry("1100x800")
root.configure(bg="#282828")
style = ttk.Style(root)
style.theme_create("pum_theme", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0],
                                    "tabposition": 'ne',
                                    "background": "#1F1F1F",
                                    "borderwidth": "0",
#                                    "font": "Helvetica 10 bold",
                                    }},
        "TNotebook.Tab": {
            "configure": {"padding": [30, 1],
                          "background": "#1F1F1F",
                          "foreground": "white",
                          "borderwidth": "0",
                          "fieldbackground": "#1F1F1F"},
            "map":       {"background": [("selected", "#383838")],
                          "foreground": [('selected', "#e5a00d")],
                          "borderwidth": "0"}}})

style.theme_use("pum_theme")
# set tabs
notebook = ttk.Notebook(root, style='TNotebook')
# user panel
user_tab: Frame = Frame(notebook)  # frame for user page
notebook.add(user_tab, text="users")
user_tab.configure(background="#1F1F1F")
# server panel
server_tab: Frame = Frame(notebook)  # frame for server page
notebook.add(server_tab, text="servers")
server_tab.configure(background="#1F1F1F")
# setting panel
conf_tab: Frame = Frame(notebook)  # frame for conf page
notebook.add(conf_tab, text="Settings")
conf_tab.configure(background="#1F1F1F")
# help & info panel
help_and_info_tab: Frame = Frame(notebook)  # frame for help & info page
notebook.add(help_and_info_tab, text="Help & info")
help_and_info_tab.configure(background="#1F1F1F")
notebook.pack(expand=True, fill="both")  # expand to space not used

# Configure treeview header color
style.configure('Treeview.Heading',
                background="#1F1F1F",
                font="Helvetica 10 bold",
                foreground="grey")

# Configure the Treeview Colors
style.configure("Treeview",
                background="#D3D3D3",
                foreground="white",
                rowheight=25,
                relief="flat",
                borderwidth=0,
                fieldbackground="#D3D3D3")

# Change Selected Color
style.map('Treeview',
          background=[('selected', "#383838")],
          #font=[('selected', "bold")],
          foreground=[('selected', "#e5a00d")])

# **********************************************************************************************************************
# ************************************************* VARIABLES **********************************************************
# **********************************************************************************************************************
# var for new servers
NEW_PLEX_SERVER = ""

# global config_path
config_path = ".config/"
api_path = "api/"

# Read config.ini file
config_object = ConfigParser()
config_object.read(config_path + "pum.ini")
# Get the conf info
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

# DB connection
# Read config.ini file
config_object = ConfigParser()
config_object.read(config_path + "pum.ini")
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


# **********************************************************************************************************************
# ************************************************* DB create **********************************************************
# **********************************************************************************************************************
def db_create():
    # Create database if not exists
    cursor.execute("CREATE DATABASE IF NOT EXISTS pum")

    # Create table plexusers
    cursor.execute("CREATE TABLE IF NOT EXISTS plexusers(first_name VARCHAR(255), \
         last_name VARCHAR(255), \
         username VARCHAR(255), \
         email VARCHAR(255), \
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
         hidden INT(10) DEFAULT 0, \
         PRIMARY KEY(userID, serverName) );")

    # Create table tempusers
    cursor.execute("CREATE TABLE IF NOT EXISTS tempusers(serverName VARCHAR(255) NOT NULL, \
         userID INT NOT NULL, \
         PRIMARY KEY(userID, serverName) );")

    # Create table plexservers
    cursor.execute("CREATE TABLE IF NOT EXISTS plexservers(serverName VARCHAR(255), \
         token VARCHAR(255) NOT NULL, \
         url VARCHAR(255) NOT NULL, \
         server_offline INT(10) default NULL,\
         PRIMARY KEY(url, token) );")

    # Create table plexlibraries
    cursor.execute("CREATE TABLE IF NOT EXISTS plexlibraries(serverName VARCHAR(255) NOT NULL, \
         email VARCHAR(255) NOT NULL, \
         library VARCHAR(255) NOT NULL, \
         PRIMARY KEY(library, serverName, email) );")

    # Create table plexfilterMovies
    cursor.execute("CREATE TABLE IF NOT EXISTS plexfilterMovies(serverName VARCHAR(255) NOT NULL, \
         email VARCHAR(255) NOT NULL, \
         filterMovies VARCHAR(255) NOT NULL, \
         PRIMARY KEY(filterMovies, serverName, email) );")

    # Create table plexfilterMusic
    cursor.execute("CREATE TABLE IF NOT EXISTS plexfilterMusic(serverName VARCHAR(255) NOT NULL, \
            email VARCHAR(255) NOT NULL, \
            filterMusic VARCHAR(255) NOT NULL, \
            PRIMARY KEY(filterMusic, serverName, email) );")

    # Create table plexfilterTelevision
    cursor.execute("CREATE TABLE IF NOT EXISTS plexfilterTelevision(serverName VARCHAR(255) NOT NULL, \
            email VARCHAR(255) NOT NULL, \
            filterTelevision VARCHAR(255) NOT NULL, \
            PRIMARY KEY(filterTelevision, serverName, email) );")

# **********************************************************************************************************************
# *********************************************** import data **********************************************************
# **********************************************************************************************************************
def import_data():
    global NEW_PLEX_SERVER, NEW_PLEX_URL, NEW_PLEX_TOKEN
    root.title('Plex User Manager... loading data...')
    config_path = ".config/"
    api_path = "api/"
    # DB connection
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
    # Get the conf info
    userinfo = config_object["DATABASE"]
    db_host = userinfo["host"]
    db_user = userinfo["user"]
    db_passwd = userinfo["passwd"]
    db_db = userinfo["db"]

    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
    # Get the conf info
    userinfo = config_object["CONF"]
    remove_user_access = userinfo["remove_user_access"]
    # connect to MySQL
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_db,
        auth_plugin='mysql_native_password')
    # Create a cursor and initialize it
    cursor = mydb.cursor()

    # clean old entries
    cursor.execute(
        "SELECT * FROM plexfilterMovies WHERE NOT EXISTS(SELECT NULL FROM plexusers WHERE plexusers.email = plexfilterMovies.email);")
    deleted_filterMovies = cursor.fetchall()
    for delet_filtMov in deleted_filterMovies:
        cursor.execute("DELETE FROM plexfilterMovies WHERE serverName = %s AND email = %s AND library = %s;",
                       [delet_filtMov[0], delet_filtMov[1], delet_filtMov[2]])
        print("Old entry : filterMovies " + delet_filtMov[2] + " has been removed on server " + delet_filtMov[0] + " for user " +
              delet_filtMov[1])
    cursor.execute(
        "SELECT * FROM plexfilterMusic WHERE NOT EXISTS(SELECT NULL FROM plexusers WHERE plexusers.email = plexfilterMusic.email);")
    deleted_filterMusic = cursor.fetchall()
    for delet_filtMus in deleted_filterMusic:
        cursor.execute("DELETE FROM plexfilterMusic WHERE serverName = %s AND email = %s AND library = %s;",
                       [delet_filtMus[0], delet_filtMus[1], delet_filtMus[2]])
        print("Old entry : filterMusic " + delet_filtMus[2] + " has been removed on server " + delet_filtMus[0] + " for user " +
              delet_filtMus[1])
    cursor.execute(
        "SELECT * FROM plexfilterTelevision WHERE NOT EXISTS(SELECT NULL FROM plexusers WHERE plexusers.email = plexfilterTelevision.email);")
    deleted_filterTelevision = cursor.fetchall()
    for delet_filtTV in deleted_filterTelevision:
        cursor.execute("DELETE FROM plexfilterTelevision WHERE serverName = %s AND email = %s AND library = %s;",
                       [delet_filtTV[0], delet_filtTV[1], delet_filtTV[2]])
        print("Old entry : filterTelevision " + delet_filtTV[2] + " has been removed on server " + delet_filtTV[0] + " for user " + delet_filtTV[1])
    cursor.execute(
        "SELECT * FROM plexlibraries WHERE NOT EXISTS(SELECT NULL FROM plexusers WHERE plexusers.email = plexlibraries.email);")
    deleted_libraries = cursor.fetchall()
    for delet_lib in deleted_libraries:
        cursor.execute("DELETE FROM plexlibraries WHERE serverName = %s AND email = %s AND library = %s;", [delet_lib[0], delet_lib[1], delet_lib[2]])
        print("Old entry : library " + delet_lib[2] + " has been removed on server " + delet_lib[0] + " for user " + delet_lib[1])

    # remove user access if expired
    if remove_user_access == "1":
        cursor.execute("SELECT email, serverName FROM plexusers WHERE account_expire_date < CURDATE() AND NOT (SELECT email FROM plexlibraries WHERE plexusers.email = plexlibraries.email AND plexusers.serverName = plexlibraries.serverName);")
        expired_user = cursor.fetchall()
        #print(expired_user)
        for exp_usr in expired_user:
            usr_job = expired_user[0]
            config_path = ".config/"
            # DB connection
            # Read config.ini file
            config_object = ConfigParser()
            config_object.read(config_path + "pum.ini")
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
            # get server token and url
            cursor.execute("SELECT * FROM plexservers WHERE serverName = %s;", [usr_job[1]])
            selected_plex_info = cursor.fetchall()
            # print(type(selected_plex_info))
            new_selected_plex_info = selected_plex_info[0]
            PLEX_URL = str(new_selected_plex_info[2])
            PLEX_TOKEN = str(new_selected_plex_info[1])
            # write to plex_api config.ini
            plex_config_object = ConfigParser()
            plex_config_object.read(plexapi.CONFIG_PATH)
            plex_config_object['auth']['server_baseurl'] = PLEX_URL
            plex_config_object['auth']['server_token'] = PLEX_TOKEN
            with open(plexapi.CONFIG_PATH, 'w') as plex_configfile:
                plex_config_object.write(plex_configfile)
            # export json from plex
            os.system("python3 plex_api_share.py --unshare --user " + usr_job[0])
            cursor.execute("UPDATE plexusers SET sections = 'NULL' WHERE email = %s AND serverName = %s;", [usr_job[0], usr_job[1]])
            print("unshare all libraries for user " + usr_job[0] + " on server " + usr_job[1])


    if NEW_PLEX_SERVER:
        records = [NEW_PLEX_SERVER, NEW_PLEX_URL, NEW_PLEX_TOKEN]
    else:
        cursor.execute("SELECT * FROM plexservers WHERE server_offline = 0;")
        records = cursor.fetchall()
    for record in records:
        #serverName = record[0]
        PLEX_TOKEN = record[1]
        PLEX_URL = record[2]
        sess = requests.Session()
        # Ignore verifying the SSL certificate
        sess.verify = False  # '/path/to/certfile'
        # If verify is set to a path to a directory,
        # the directory must have been processed using the c_rehash utility supplied
        # with OpenSSL.
        if sess.verify is False:
            # Disable the warning that the request is insecure, we know that...
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # test if server online
        try:
            plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=sess)
        except:
            cursor.execute("UPDATE plexservers SET server_offline = 1 WHERE token = %s AND url = %s;",
                           [PLEX_TOKEN, PLEX_URL])
            #return
        else:
            # if the name has changed then update
            plex = PlexServer(PLEX_URL, PLEX_TOKEN, session=sess)
            if record[0] != plex.friendlyName:
                cursor.execute("UPDATE plexservers SET serverName = %s WHERE token = %s AND url = %s;", [plex.friendlyName, PLEX_TOKEN, PLEX_URL])
            # server is online
            cursor.execute("UPDATE plexservers SET server_offline = 0 WHERE token = %s AND url = %s;", [PLEX_TOKEN, PLEX_URL])
            serverName = plex.friendlyName
            #print(serverName)
            #print(PLEX_TOKEN)
            #print(PLEX_URL)
            #print(PLEX_TOKEN)
            plex_config_object = ConfigParser()
            plex_config_object.read(plexapi.CONFIG_PATH)
            plex_config_object['auth']['server_baseurl'] = PLEX_URL
            plex_config_object['auth']['server_token'] = PLEX_TOKEN
            with open(plexapi.CONFIG_PATH, 'w') as plex_configfile:
                plex_config_object.write(plex_configfile)
            # export json from plex
            os.system("python3 plex_api_share.py --backup")
            print(serverName + " json created")
            NEW_PLEX_SERVER = ""

    # empty table tempusers
    cursor.execute("TRUNCATE TABLE tempusers;")
    # import user data
    path_to_json = glob.glob(r'./*.json')
    # check json file
    if not path_to_json:
        print("No JSON files... ")
        #quit()
    # loop for every json file
    for jfile in path_to_json:
        # load json
        json_data = open(jfile).read()
        json_obj = json.loads(json_data)
        # do validation and checks before insert
        def validate_string(val):
            if val != None:
                if type(val) is int:
                    # for x in val:
                    #   print(x)
                    return str(val).encode('utf-8')
                else:
                    return val

        # remove not wanted characters
        for mydict in json_obj:
            # check if filterMovies exist and put it in DB
            if mydict['filterMovies']:
                filtermovie_entrie = mydict['filterMovies']
                cursor.execute("DELETE FROM plexfilterMovies WHERE email = %s AND serverName = %s;",
                               [mydict['email'], mydict['serverName']])
                for key in filtermovie_entrie['label']:
                    cursor.execute("INSERT INTO plexfilterMovies SET filterMovies = %s, email = %s, serverName = %s;",
                                   [key, mydict['email'], mydict['serverName']])

            # check if filterMusic exist and put it in DB
            if mydict['filterMusic']:
                filterMusic_entrie = mydict['filterMusic']
                cursor.execute("DELETE FROM plexfilterMusic WHERE email = %s AND serverName = %s;",
                               [mydict['email'], mydict['serverName']])
                for key in filterMusic_entrie['label']:
                    cursor.execute("INSERT INTO plexfilterMusic SET filterMusic = %s, email = %s, serverName = %s;",
                                   [key, mydict['email'], mydict['serverName']])

            # check if filterTelevision exist and put it in DB
            if mydict['filterTelevision']:
                filterTelevision_entrie = mydict['filterTelevision']
                cursor.execute("DELETE FROM plexfilterTelevision WHERE email = %s AND serverName = %s;",
                               [mydict['email'], mydict['serverName']])
                for key in filterTelevision_entrie['label']:
                    cursor.execute(
                        "INSERT INTO plexfilterTelevision SET filterTelevision = %s, email = %s, serverName = %s;",
                        [key, mydict['email'], mydict['serverName']])

            # check if sections exist and put it in DB
            if mydict['sections']:
                sections_entrie = mydict['sections']
                #print(sections_entrie)
                cursor.execute("DELETE FROM plexlibraries WHERE email = %s AND serverName = %s;",
                               [mydict['email'], mydict['serverName']])
                for key in sections_entrie:
                    cursor.execute(
                        "INSERT INTO plexlibraries SET library = %s, email = %s, serverName = %s;",
                        [key, mydict['email'], mydict['serverName']])

            # create or update user
            #print(mydict['userID'])
            #print(mydict['serverName'])
            #print(mydict['allowSync'])
            #print(mydict['camera'])
            #print(mydict['channels'])
            #print(mydict['email'])
            #print(mydict['title'])
            #print(mydict['username'])

            cursor.execute("INSERT IGNORE INTO plexusers SET userID = %s, account_creation_date = CURDATE(), serverName = %s;", [mydict['userID'], mydict['serverName']])
            cursor.execute("UPDATE plexusers SET allowSync = %s, camera = %s, channels = %s, email = %s, title = %s, username = %s, is_on_plex = 1 WHERE userID = %s AND serverName = %s;", [
                    mydict['allowSync'], mydict['camera'], mydict['channels'], mydict['email'], mydict['title'], mydict['username'], mydict['userID'], mydict['serverName']])

            # add to temp db to compare
            cursor.execute("INSERT IGNORE INTO tempusers SET userID = %s, serverName = %s;", [mydict['userID'], mydict['serverName']])
    print("json files imported to db")



    # delete old json file
    app_dir = os.listdir(os.getcwd())
    for json_item in app_dir:
        if json_item.endswith(".json"):
            os.remove(os.path.join(os.getcwd(), json_item))
    # compare tempusers and plexusers and remove old user
    cursor.execute("DELETE FROM plexusers WHERE is_on_plex = 0 AND userID NOT in (SELECT userID FROM tempusers) AND serverName IN (SELECT serverName FROM tempusers);")
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()
    '''# clear my_server_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get server data back
    query_user_info()'''
    # clear my_server_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get server data back
    root.title('Plex User Manager')
    query_user_info()
    multithreading_sync_data()

def multithreading_import_data():
    thread_import_data = threading.Thread(target=import_data, name="import data")
    thread_import_data.start()

def sync_data():
    #time.sleep(86400)
    time.sleep(int(sync_plex_delai)*3600)
    multithreading_import_data()
    print("waited for " + sync_plex_delai + " Hours, data synced")
    # clear my_server_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get server data back
    query_user_info()

def multithreading_sync_data():
    thread_sync_data = threading.Thread(target=sync_data, name="sync data")
    thread_sync_data.daemon = True
    thread_sync_data.start()

db_create()

# check if server is configured to sync
cursor.execute("SELECT serverName FROM plexservers;")
records = cursor.fetchall()
if records:
    multithreading_import_data()
else:
    tkinter.messagebox.showinfo(title="Server missing", message="please add server in server panel")



# **********************************************************************************************************************
# ********************************************* user panel *************************************************************
# **********************************************************************************************************************

# missing if server_offline == 1 then do not update user

def query_user_info():
    # DB connection
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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
    # Select info from db
    if hide_guest_str == "1" and hide_no_lib_users_str != "1":
        cursor.execute("SELECT * FROM plexusers WHERE title != 'Guest';")
    if hide_no_lib_users_str == "1" and hide_guest_str != "1":
        #cursor.execute("SELECT * FROM plexusers WHERE hidden != '1';")
        cursor.execute("SELECT DISTINCT plexusers.* FROM plexusers, plexlibraries WHERE plexusers.email = plexlibraries.email AND plexusers.serverName = plexlibraries.serverName;")
    if hide_no_lib_users_str == "1" and hide_guest_str == "1":
        cursor.execute("SELECT DISTINCT plexusers.* FROM plexusers, plexlibraries WHERE plexusers.email = plexlibraries.email AND plexusers.serverName = plexlibraries.serverName AND plexusers.title != 'Guest';")
    if hide_no_lib_users_str != "1" and hide_guest_str != "1":
        cursor.execute("SELECT * FROM plexusers;")
    records = cursor.fetchall()
    # Add our data to the screen
    global count
    count = 0
    for record in records:
        if count % 2 == 0:
            my_user_tree.insert(parent='', index='end', iid=str(count), text='',
                                values=(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], record[12], record[13], record[14], record[15], record[16], record[17], record[18]),
                                tags=('evenrow',))
        else:
            my_user_tree.insert(parent='', index='end', iid=str(count), text='',
                                values=(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], record[12], record[13], record[14], record[15], record[16], record[17], record[18]),
                                tags=('oddrow',))
        # increment counter
        count += 1
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()

# Create a Treeview Frame
user_tree_frame = Frame(user_tab)
user_tree_frame.configure(background="#1F1F1F")
user_tree_frame.pack(fill="x", expand=1, pady=10)

# Create a Treeview Scrollbar
user_tree_scroll = Scrollbar(user_tree_frame)
user_tree_scroll.configure(background="#1F1F1F")
user_tree_scroll.pack(side=RIGHT, fill=Y)

# Create The Treeview
my_user_tree = ttk.Treeview(user_tree_frame, yscrollcommand=user_tree_scroll.set, selectmode="extended")
my_user_tree.pack(fill="x")

# Configure the Scrollbar
user_tree_scroll.config(command=my_user_tree.yview)

# Define Our Columns
my_user_tree['columns'] = ("First Name", "Last Name", "Username", "email", "server_name", "expire_date") #, "libraries")

# Format Our Columns
my_user_tree.column("#0", width=0, stretch=NO)
my_user_tree.column("First Name", anchor=W, width=130)
my_user_tree.column("Last Name", anchor=W, width=140)
my_user_tree.column("Username", anchor=CENTER, width=180)
my_user_tree.column("email", anchor=CENTER, width=260)
my_user_tree.column("server_name", anchor=CENTER, width=160)
my_user_tree.column("expire_date", anchor=CENTER, width=120)
#my_user_tree.column("libraries", anchor=CENTER, width=140) 40

# Create Headings
my_user_tree.heading("#0", text="", anchor=W)
my_user_tree.heading("First Name", text="First Name", anchor=W)
my_user_tree.heading("Last Name", text="Last Name", anchor=W)
my_user_tree.heading("Username", text="Username", anchor=CENTER)
my_user_tree.heading("email", text="email", anchor=CENTER)
my_user_tree.heading("server_name", text="server name", anchor=CENTER)
my_user_tree.heading("expire_date", text="expire date", anchor=CENTER)
#my_user_tree.heading("libraries", text="libraries", anchor=CENTER)

# Select record
def select_user_record(e):
    config_path = ".config/"
    api_path = "api/"
    # DB connection
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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
    # Clear entry boxes
    # mettre state en disabled pour avoir les case grise, mais napplique plus le entry
    first_name_entry.delete(0,END)
    last_name_entry.delete(0, END)
    username_entry.config(disabledbackground="#282828",
                          disabledforeground="white",
                          state="normal")
    username_entry.delete(0, END)
    email_entry.config(disabledbackground="#282828",
                       disabledforeground="white",
                       state="normal")
    email_entry.delete(0, END)
    serverName_entry.config(disabledbackground="#282828",
                            disabledforeground="white",
                            state="normal")
    serverName_entry.delete(0, END)
    account_expire_date_entry.delete(0, END)
    sections_entry.config(disabledbackground="#282828",
                          disabledforeground="white",
                          state="normal")
    sections_entry.delete(0, END)
    allowSync_entry.config(disabledbackground="#282828",
                           disabledforeground="white",
                           state="normal")
    allowSync_entry.delete(0, END)
    camera_entry.config(disabledbackground="#282828",
                        disabledforeground="white",
                        state="normal")
    camera_entry.delete(0, END)
    channels_entry.config(disabledbackground="#282828",
                          disabledforeground="white",
                          state="normal")
    channels_entry.delete(0, END)
    filterMovies_entry.config(disabledbackground="#282828",
                              disabledforeground="white",
                              state="normal")
    filterMovies_entry.delete(0, END)
    filterMusic_entry.config(disabledbackground="#282828",
                             disabledforeground="white",
                             state="normal")
    filterMusic_entry.delete(0, END)
    filterTelevision_entry.config(disabledbackground="#282828",
                                  disabledforeground="white",
                                  state="normal")
    filterTelevision_entry.delete(0, END)
    title_entry.config(disabledbackground="#282828",
                       disabledforeground="white",
                       state="normal")
    title_entry.delete(0, END)
    is_on_plex_entry.config(disabledbackground="#282828",
                            disabledforeground="white",
                            state="normal")
    is_on_plex_entry.delete(0, END)
    userID_entry.config(disabledbackground="#282828",
                        disabledforeground="white",
                        state="normal")
    userID_entry.delete(0, END)
    account_creation_date_entry.delete(0, END)
    account_renewed_date_entry.delete(0, END)
    #userID_entry.delete(0, END)
    description_entry.delete(0, END)

    # Grab record number
    selected = my_user_tree.focus()
    # Grab record values
    values = my_user_tree.item(selected, 'values')
    # print(values)

    # Output entry boxes
    try:
        first_name_entry.insert(0, values[0])
        last_name_entry.insert(0, values[1])
        username_entry.insert(0, values[2])
        username_entry.config(state="disabled",
                              disabledbackground="#282828")
        email_entry.insert(0, values[3])
        email_entry.config(state="disabled",
                           disabledbackground="#282828")
        serverName_entry.insert(0, values[4])
        serverName_entry.config(state="disabled",
                                disabledbackground="#282828")
        account_expire_date_entry.insert(0, values[5])

        #print("user sections unknown: " + values[6])
        # get the libraries for selected user
        cursor.execute("SELECT library FROM plexlibraries WHERE email = %s AND serverName = %s;", [values[3], values[4]])
        user_libraries = cursor.fetchall()
        # display libraries in clean way
        for libraries in user_libraries:
            sections_entry.insert(0, libraries[0] + " - ")
        sections_entry.config(state="disabled",
                              disabledbackground="#282828")
        allowSync_entry.insert(0, values[7])
        allowSync_entry.config(state="disabled",
                               disabledbackground="#282828")
        camera_entry.insert(0, values[8])
        camera_entry.config(state="disabled",
                            disabledbackground="#282828")
        channels_entry.insert(0, values[9])
        channels_entry.config(state="disabled",
                              disabledbackground="#282828")
        # get the filterMovies for selected user
        cursor.execute("SELECT filterMovies FROM plexfilterMovies WHERE email = %s AND serverName = %s;",
                       [values[3], values[4]])
        user_filterMovies = cursor.fetchall()
        # display filterMovies in clean way
        for filterMovies in user_filterMovies:
            filterMovies_entry.insert(0, filterMovies[0] + " - ")
        filterMovies_entry.config(state="disabled",
                                  disabledbackground="#282828")
        # get the filterMusic for selected user
        cursor.execute("SELECT filterMusic FROM plexfilterMusic WHERE email = %s AND serverName = %s;",
                       [values[3], values[4]])
        user_filterMusic = cursor.fetchall()
        # display filterMovies in clean way
        for filterMusic in user_filterMusic:
            filterMusic_entry.insert(0, filterMusic[0] + " - ")
        filterMusic_entry.config(state="disabled",
                                 disabledbackground="#282828")
        # get the filterTelevision for selected user
        cursor.execute("SELECT filterTelevision FROM plexfilterTelevision WHERE email = %s AND serverName = %s;",
                       [values[3], values[4]])
        user_filterTelevision = cursor.fetchall()
        # display filterTelevision in clean way
        for filterTelevision in user_filterTelevision:
            filterTelevision_entry.insert(0, filterTelevision[0] + " - ")
        filterTelevision_entry.config(state="disabled",
                                      disabledbackground="#282828")
        title_entry.insert(0, values[13])
        title_entry.config(state="disabled",
                           disabledbackground="#282828")
        is_on_plex_entry.insert(0, values[14])
        is_on_plex_entry.config(state="disabled",
                                disabledbackground="#282828")

        account_creation_date_entry.insert(0, values[15])
        account_renewed_date_entry.insert(0, values[16])
        userID_entry.insert(0, values[17])
        userID_entry.config(state="disabled",
                            disabledbackground="#282828")
        description_entry.insert(0, values[18])

        # keep values to avoid request if identical
        global old_account_creation_date_entry
        old_account_creation_date_entry = values[15]
        global old_account_renewed_date_entry
        old_account_renewed_date_entry = values[16]
        global old_account_expire_date_entry
        old_account_expire_date_entry = values[5]
        # Commit changes
        mydb.commit()
        # Close connexion
        mydb.close()
    except:
        pass

# Update Record
def update_user_record():
    config_path = ".config/"
    api_path = "api/"
    # DB connection
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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
    # Grab the record number
    selected = my_user_tree.focus()
    # Update record
    my_user_tree.item(selected, text="", values=(
    first_name_entry.get(), last_name_entry.get(), username_entry.get(), email_entry.get(), serverName_entry.get(),
    account_expire_date_entry.get(), sections_entry.get(), allowSync_entry.get(), camera_entry.get(),
    channels_entry.get(), filterMovies_entry.get(), filterMusic_entry.get(), filterTelevision_entry.get(),
    title_entry.get(), is_on_plex_entry.get(), account_creation_date_entry.get(), account_renewed_date_entry.get(),
    userID_entry.get(), description_entry.get(),))


    if account_creation_date_entry.get() != "None" and account_creation_date_entry.get() != old_account_creation_date_entry:
        cursor.execute("UPDATE plexusers SET account_creation_date = %s WHERE userID = %s;",
                       [
                           account_creation_date_entry.get(),
                           userID_entry.get()
                       ])

    if account_renewed_date_entry.get() != "None" and account_renewed_date_entry.get() != old_account_renewed_date_entry:
        cursor.execute("UPDATE plexusers SET account_renewed_date = %s WHERE userID = %s AND serverName = %s;",
                       [
                           account_renewed_date_entry.get(),
                           userID_entry.get(),
                           serverName_entry.get()
                       ])

    if account_expire_date_entry.get() != "None" and account_expire_date_entry.get() != old_account_expire_date_entry:
        cursor.execute("UPDATE plexusers SET account_expire_date = %s WHERE userID = %s AND serverName = %s;",
                       [
                           account_expire_date_entry.get(),
                           userID_entry.get(),
                           serverName_entry.get()
                       ])

    cursor.execute("UPDATE plexusers SET first_name = %s, last_name = %s, description = %s WHERE email = %s;",
                   [
                       first_name_entry.get(),
                       last_name_entry.get(),
                       description_entry.get(),
                       email_entry.get()
                   ])
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()

# delete user
def delete_user():
    # DB connection
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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
    # Grab the record number
    selected = my_user_tree.focus()
    if not email_entry.get() == '':
        # message box to be sure
        delete_user_confirmation_box = askyesno("delete selected user", "you are going to delete " + email_entry.get() + " are you sure?")
        #print(delete_user_confirmation_box)
        # confirmation box
        if delete_user_confirmation_box:
            current_user_serverName = serverName_entry.get()
            current_user_email = email_entry.get()
            # delete user from db
            cursor.execute("DELETE FROM plexusers WHERE email = %s;", [email_entry.get()])
            print("user " + email_entry.get() + " deleted from DB")
            first_name_entry.delete(0, END)
            last_name_entry.delete(0, END)
            username_entry.delete(0, END)
            email_entry.config(disabledbackground="#282828",
                               disabledforeground="white",
                               state="normal")
            email_entry.delete(0, END)
            serverName_entry.config(disabledbackground="#282828",
                                    disabledforeground="white",
                                    state="normal")
            serverName_entry.delete(0, END)
            account_expire_date_entry.delete(0, END)
            sections_entry.config(disabledbackground="#282828",
                                  disabledforeground="white",
                                  state="normal")
            sections_entry.delete(0, END)
            allowSync_entry.config(disabledbackground="#282828",
                                   disabledforeground="white",
                                   state="normal")
            allowSync_entry.delete(0, END)
            camera_entry.config(disabledbackground="#282828",
                                disabledforeground="white",
                                state="normal")
            camera_entry.delete(0, END)
            channels_entry.config(disabledbackground="#282828",
                                  disabledforeground="white",
                                  state="normal")
            channels_entry.delete(0, END)
            filterMovies_entry.config(disabledbackground="#282828",
                                      disabledforeground="white",
                                      state="normal")
            filterMovies_entry.delete(0, END)
            filterMusic_entry.config(disabledbackground="#282828",
                                     disabledforeground="white",
                                     state="normal")
            filterMusic_entry.delete(0, END)
            filterTelevision_entry.config(disabledbackground="#282828",
                                          disabledforeground="white",
                                          state="normal")
            filterTelevision_entry.delete(0, END)
            title_entry.config(disabledbackground="#282828",
                               disabledforeground="white",
                               state="normal")
            title_entry.delete(0, END)
            is_on_plex_entry.config(disabledbackground="#282828",
                                    disabledforeground="white",
                                    state="normal")
            is_on_plex_entry.delete(0, END)
            userID_entry.config(disabledbackground="#282828",
                                disabledforeground="white",
                                state="normal")
            userID_entry.delete(0, END)
            account_creation_date_entry.delete(0, END)
            account_renewed_date_entry.delete(0, END)
            # userID_entry.delete(0, END)
            description_entry.delete(0, END)

            # delete user from plex
            try:
                cursor.execute("SELECT * FROM plexservers WHERE serverName = %s;", [current_user_serverName])
                delete_user_srv_data = cursor.fetchall()
                #print(current_user_serverName)
                #print(delete_user_srv_data)
                #print(delete_user_srv_data[0])
                for current_servers in delete_user_srv_data:
                    from plexapi.server import PlexServer
                    from requests import Session
                    CURRENT_PLEX_TOKEN = current_servers[1]
                    CURRENT_PLEX_URL = current_servers[2]
                    #print(current_servers[1])
                    #print(current_servers[2])
                    if CURRENT_PLEX_TOKEN == '' or CURRENT_PLEX_URL == '':
                        return
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
                    SERVER = PlexServer(baseurl=CURRENT_PLEX_URL, token=CURRENT_PLEX_TOKEN, session=SESSION)
                    ACCOUNT = SERVER.myPlexAccount()
                    #PLEX_USERS = {user.id: user.title for user in ACCOUNT.users()}
                    #PLEX_USERS.update({int(ACCOUNT.id): ACCOUNT.title})
                    #print(ACCOUNT.id)
                    #print(ACCOUNT.title)
                    #print(ACCOUNT.users)
                    #print(current_user_email)
                    #print(PLEX_USERS)
                    ACCOUNT.removeFriend(current_user_email)
                    print("user " + current_user_email + " deleted from Plex")
            except:
                pass
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()
    # clear my_server_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get server data back
    query_user_info()

# add user
def add_user():
    #exec(open("./modules/add_plex_user.py").read())
    add_user_window = Toplevel(root)
    add_user_window.title('Plex User Manager: adding user')
    add_user_window.geometry("900x700")
    add_user_window.configure(bg="#282828")



    config_path = ".config/"
    # DB connection
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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

    # add the user
    def add_user_command():
        import re
        config_path = ".config/"
        # DB connection
        # Read config.ini file
        config_object = ConfigParser()
        config_object.read(config_path + "pum.ini")
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
        # global selected_server
        print("email : " + email_entry.get())
        # global selected_server
        print("server : " + server_clicked.get()[2:-3])
        add_user_library_selected = ''
        for add_user_library_selected_item in library_listbox.curselection():
            add_user_library_selected = add_user_library_selected + str(library_listbox.get(add_user_library_selected_item))
        #print("selected libraries " + add_user_library_selected)
        add_user_library_selected = re.sub(r"[\(\)]", '', add_user_library_selected)
        add_user_library_selected = add_user_library_selected.replace(',', ' ')

        #get server token and url
        cursor.execute("SELECT * FROM plexservers WHERE serverName = %s;", [server_clicked.get()[2:-3]])
        selected_plex_info = cursor.fetchall()
        #print(type(selected_plex_info))
        new_selected_plex_info = selected_plex_info[0]
        PLEX_URL = str(new_selected_plex_info[2])
        PLEX_TOKEN = str(new_selected_plex_info[1])
        # write to plex_api config.ini
        plex_config_object = ConfigParser()
        plex_config_object.read(plexapi.CONFIG_PATH)
        plex_config_object['auth']['server_baseurl'] = PLEX_URL
        plex_config_object['auth']['server_token'] = PLEX_TOKEN
        with open(plexapi.CONFIG_PATH, 'w') as plex_configfile:
            plex_config_object.write(plex_configfile)
        # export json from plex
        os.system("python3 plex_api_invite.py --user " + email_entry.get() + " --libraries " + add_user_library_selected)
        print("plex_api_invite.py --user " + email_entry.get() + " --libraries " + add_user_library_selected)
        #print(PLEX_TOKEN)
        #print(PLEX_URL)
        # Commit changes
        mydb.commit()
        # Close connexion
        mydb.close()
        add_user_window.destroy()


    # library selection
    def select_library(server_clicked):
        config_path = ".config/"
        # DB connection
        # Read config.ini file
        config_object = ConfigParser()
        config_object.read(config_path + "pum.ini")
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

        # library selection
        cursor.execute("SELECT DISTINCT library FROM plexlibraries WHERE serverName = %s;", [server_clicked[0]])
        library_result = cursor.fetchall()
        library_listbox.delete(0, END)
        library_listbox.insert(0, *library_result)

        #for lib_result in library_result:
        #print(library_result)


        # Commit changes
        mydb.commit()
        # Close connexion
        mydb.close()

    # email entry
    email_label = Label(add_user_window, text="new user email : ")
    email_label.grid(row=0, column=0, padx=10, pady=30, sticky=W)
    email_label.config(background="#282828",
                       foreground="white")
    email_entry = Entry(add_user_window, width=30)
    email_entry.grid(row=0, column=1, padx=10, pady=10, sticky=W)

    # server selection
    cursor.execute("SELECT serverName FROM plexservers;")
    server_records = cursor.fetchall()
    server_selection_label = Label(add_user_window, text="select server to add user ")
    server_selection_label.grid(row=1, column=0, padx=10, pady=10, sticky=W)
    server_selection_label.config(background="#282828",
                                  foreground="white")
    server_clicked = StringVar()
    server_clicked.set("select server")
    server_name_drop = OptionMenu(add_user_window, server_clicked, *server_records, command=select_library) #, command=select_library
    server_name_drop.grid(row=1, column=1, padx=10, pady=10, sticky=W)
    global selected_server
    selected_server = server_clicked.get()[2:-3]

    library_selection_label = Label(add_user_window, text="select library to add to user ")
    library_selection_label.grid(row=1, column=2, padx=10, pady=10, sticky=W)
    library_selection_label.config(background="#282828",
                                   foreground="white")

    #library_frame_for_user = Frame(add_user_window)
    #library_for_user_scrollbar = Scrollbar(add_user_window, orient=VERTICAL)

    library_listbox = Listbox(add_user_window, selectmode=MULTIPLE) #, yscrollcommand=library_for_user_scrollbar.set)
    #library_for_user_scrollbar.config(command=library_listbox.yview)
    library_listbox.grid(row=1, column=3, padx=10, pady=10, sticky=W)
    #library_for_user_scrollbar.grid(sticky=E)


    #library_listbox.insert(0, *library_result)





    create_user_button = Button(add_user_window, text="add user", command=add_user_command)
    create_user_button.grid(row=20, column=0, padx=10, pady=10, sticky='W')

    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()

# Create Striped Row Tags
my_user_tree.tag_configure('oddrow', background="#303030")
my_user_tree.tag_configure('evenrow', background="#2B2B2B")

# Add Record Entry Boxes
user_data_frame = LabelFrame(user_tab, text="Selected User Information")
user_data_frame.pack(fill="x", expand=1, padx=20)

# Configure the user_data_frame color
user_data_frame.configure(background="#282828",
                          foreground="white")

first_name_label = Label(user_data_frame, text="First Name")
first_name_label.grid(row=0, column=0, padx=10, pady=10)
first_name_label.config(background="#282828",
                        foreground="white")
first_name_entry = Entry(user_data_frame)
first_name_entry.grid(row=0, column=1, padx=10, pady=10)

last_name_label = Label(user_data_frame, text="Last Name")
last_name_label.grid(row=0, column=2, padx=10, pady=10)
last_name_label.config(background="#282828",
                       foreground="white")
last_name_entry = Entry(user_data_frame)
last_name_entry.grid(row=0, column=3, padx=10, pady=10)

username_label = Label(user_data_frame, text="Username")
username_label.grid(row=0, column=4, padx=10, pady=10)
username_label.config(background="#282828",
                      foreground="white")
username_entry = Entry(user_data_frame)
username_entry.grid(row=0, column=5, padx=10, pady=10)
username_entry.config(disabledbackground="#282828",
                      state="disabled")

email_label = Label(user_data_frame, text="email")
email_label.grid(row=1, column=0, padx=10, pady=10)
email_label.config(background="#282828",
                   foreground="white")
email_entry = Entry(user_data_frame)
email_entry.grid(row=1, column=1, padx=10, pady=10)
email_entry.config(disabledbackground="#282828",
                   state="disabled")

serverName_label = Label(user_data_frame, text="serverName")
serverName_label.grid(row=1, column=2, padx=10, pady=10)
serverName_label.config(background="#282828",
                        foreground="white")
serverName_entry = Entry(user_data_frame)
serverName_entry.grid(row=1, column=3, padx=10, pady=10)
serverName_entry.config(disabledbackground="#282828",
                        state="disabled")

account_expire_date_label = Label(user_data_frame, text="expire date")
account_expire_date_label.grid(row=2, column=4, padx=10, pady=10)
account_expire_date_label.config(background="#282828",
                                 foreground="white")
account_expire_date_entry = Entry(user_data_frame)
account_expire_date_entry.grid(row=2, column=5, padx=10, pady=10)

sections_label = Label(user_data_frame, text="libraries")
sections_label.grid(row=3, column=0, padx=10, pady=10)
sections_label.config(background="#282828",
                      foreground="white")
sections_entry = Entry(user_data_frame)
sections_entry.grid(row=3, column=1, padx=10, pady=10)
sections_entry.config(disabledbackground="#282828",
                      state="disabled")

title_label = Label(user_data_frame, text="title")
title_label.grid(row=3, column=2, padx=10, pady=10)
title_label.config(background="#282828",
                   foreground="white")
title_entry = Entry(user_data_frame)
title_entry.grid(row=3, column=3, padx=10, pady=10)
title_entry.config(disabledbackground="#282828",
                   state="disabled")

userID_label = Label(user_data_frame, text="userID")
userID_label.grid(row=3, column=4, padx=10, pady=10)
userID_label.config(background="#282828",
                    foreground="white")
userID_entry = Entry(user_data_frame)
userID_entry.grid(row=3, column=5, padx=10, pady=10)
userID_entry.config(disabledbackground="#282828",
                    state="disabled")

account_creation_date_label = Label(user_data_frame, text="account_creation_date")
account_creation_date_label.grid(row=2, column=0, padx=10, pady=10)
account_creation_date_label.config(background="#282828",
                                   foreground="white")
# global account_creation_date_entry
account_creation_date_entry = Entry(user_data_frame)
account_creation_date_entry.grid(row=2, column=1, padx=10, pady=10)

account_renewed_date_label = Label(user_data_frame, text="account_renewed_date")
account_renewed_date_label.grid(row=2, column=2, padx=10, pady=10)
account_renewed_date_label.config(background="#282828",
                                  foreground="white")
account_renewed_date_entry = Entry(user_data_frame)
account_renewed_date_entry.grid(row=2, column=3, padx=10, pady=10)

description_label = Label(user_data_frame, text="description")
description_label.grid(row=1, column=4, padx=10, pady=10)
description_label.config(background="#282828",
                         foreground="white")
description_entry = Entry(user_data_frame)
description_entry.grid(row=1, column=5, padx=10, pady=10)

allowSync_label = Label(user_data_frame, text="allowSync")
allowSync_label.grid(row=4, column=0, padx=10, pady=10)
allowSync_label.config(background="#282828",
                       foreground="white")
allowSync_entry = Entry(user_data_frame)
allowSync_entry.grid(row=4, column=1, padx=10, pady=10)
allowSync_entry.config(disabledbackground="#282828",
                       state="disabled")

camera_label = Label(user_data_frame, text="camera")
camera_label.grid(row=4, column=2, padx=10, pady=10)
camera_label.config(background="#282828",
                    foreground="white")
camera_entry = Entry(user_data_frame)
camera_entry.grid(row=4, column=3, padx=10, pady=10)
camera_entry.config(disabledbackground="#282828",
                    state="disabled")

channels_label = Label(user_data_frame, text="channels")
channels_label.grid(row=4, column=4, padx=10, pady=10)
channels_label.config(background="#282828",
                      foreground="white")
channels_entry = Entry(user_data_frame)
channels_entry.grid(row=4, column=5, padx=10, pady=10)
channels_entry.config(disabledbackground="#282828",
                      state="disabled")

filterMovies_label = Label(user_data_frame, text="filterMovies")
filterMovies_label.grid(row=5, column=0, padx=10, pady=10)
filterMovies_label.config(background="#282828",
                          foreground="white")
filterMovies_entry = Entry(user_data_frame)
filterMovies_entry.grid(row=5, column=1, padx=10, pady=10)
filterMovies_entry.config(disabledbackground="#282828",
                          state="disabled")

filterMusic_label = Label(user_data_frame, text="filterMusic")
filterMusic_label.grid(row=5, column=2, padx=10, pady=10)
filterMusic_label.config(background="#282828",
                         foreground="white")
filterMusic_entry = Entry(user_data_frame)
filterMusic_entry.grid(row=5, column=3, padx=10, pady=10)
filterMusic_entry.config(disabledbackground="#282828",
                         state="disabled")

filterTelevision_label = Label(user_data_frame, text="filterTelevision")
filterTelevision_label.grid(row=5, column=4, padx=10, pady=10)
filterTelevision_label.config(background="#282828",
                              foreground="white")
filterTelevision_entry = Entry(user_data_frame)
filterTelevision_entry.grid(row=5, column=5, padx=10, pady=10)
filterTelevision_entry.config(disabledbackground="#282828",
                              state="disabled")

is_on_plex_label = Label(user_data_frame, text="is on plex")
is_on_plex_label.grid(row=6, column=4, padx=10, pady=10)
is_on_plex_label.config(background="#282828",
                        foreground="white")
is_on_plex_entry = Entry(user_data_frame)
is_on_plex_entry.grid(row=6, column=5, padx=10, pady=10)
is_on_plex_entry.config(disabledbackground="#282828",
                        state="disabled")

update_button = Button(user_data_frame, text="Update Record", command=update_user_record)
update_button.grid(row=6, column=0, padx=10, pady=10)
update_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

delete_user_button = Button(user_data_frame, text="delete selected user", command=delete_user)
delete_user_button.grid(row=6, column=1, padx=10, pady=10)
delete_user_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

# Bind the treeview
my_user_tree.bind("<ButtonRelease>", select_user_record)

# Add user frame
plex_user_option_frame = LabelFrame(user_tab, text="Plex User Options")
plex_user_option_frame.pack(fill="x", expand=1, padx=20)
# Configure the plex_add_user_frame color
plex_user_option_frame.configure(background="#282828",
                               foreground="white")
# add user button
add_user_button = Button(plex_user_option_frame, text="Add user", command=add_user)
add_user_button.grid(row=200, column=200, padx=10, pady=10)
add_user_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

# user count
cursor.execute("SELECT COUNT(DISTINCT userID) FROM plexusers;")
user_count_result = cursor.fetchall()
# Add plex info frame
plex_user_info_frame = LabelFrame(user_tab, text="Plex User Information")
plex_user_info_frame.pack(fill="x", expand=1, padx=20)
# Configure the plex_info_frame color
plex_user_info_frame.configure(background="#282828",
                               foreground="white")
user_count_label = Label(plex_user_info_frame, text="number of users : ")
user_count_label.grid(row=0, column=0, padx=10, pady=10)
user_count_label.config(background="#282828",
                        foreground="white")
user_count_result_label = Label(plex_user_info_frame, text=user_count_result)
user_count_result_label.grid(row=0, column=1)
user_count_result_label.config(background="#282828",
                               foreground="white")



# **********************************************************************************************************************
# ********************************************* server panel ***********************************************************
# **********************************************************************************************************************

def query_server_info():
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_db,
        auth_plugin='mysql_native_password')
    # Create a cursor and initialize it
    cursor = mydb.cursor()
    # Select info from db
    cursor.execute("SELECT * FROM plexservers;")
    records = cursor.fetchall()
    # Add our data to the screen
    global count
    count = 0
    for record in records:
        if record[3] == 0:
            server_status = "Online"
            # status_color = "red"
        else:
            server_status = "Offline"
            # status_color = "white"
        if count % 2 == 0:
            my_server_tree.insert(parent='', index='end', iid=str(count), text='',
                                  values=(record[0], record[1], record[2], server_status),
                                  tags=('evenrow',))
        else:
            my_server_tree.insert(parent='', index='end', iid=str(count), text='',
                                  values=(record[0], record[1], record[2], server_status),
                                  tags=('oddrow',))
        # increment counter
        count += 1

# Select server record
def select_server_record(e):
    # Clear entry boxes

    server_serverName_entry.config(disabledbackground="#282828",
                            disabledforeground="white",
                            state="normal")
    server_serverName_entry.delete(0, END)
    token_entry.config(disabledbackground="#282828",
                       disabledforeground="white",
                       state="normal")
    token_entry.delete(0, END)
    url_entry.config(disabledbackground="#282828",
                     disabledforeground="white",
                     state="normal")
    url_entry.delete(0, END)
    server_offline_entry.config(disabledbackground="#282828",
                                disabledforeground="white",
                                state="normal")
    server_offline_entry.delete(0, END)

    # Grab record number
    server_selected = my_server_tree.focus()
    # Grab record values
    server_values = my_server_tree.item(server_selected, 'values')
    # Output entry boxes
    server_serverName_entry.insert(0, server_values[0])
    server_serverName_entry.config(disabledbackground="#282828", state="disabled")
    token_entry.insert(0, server_values[1])
    token_entry.config(disabledbackground="#282828", state="disabled")
    url_entry.insert(0, server_values[2])
    url_entry.config(disabledbackground="#282828", state="disabled")
    server_offline_entry.insert(0, server_values[3])
    server_offline_entry.config(disabledbackground="#282828", state="disabled")


# Update server Record
def delete_server_record():
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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
    cursor.execute("DELETE FROM plexservers WHERE ServerName = %s AND url = %s;", [serverName_entry.get(), url_entry.get()])
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()
    # clear my_server_tree
    my_server_tree.delete(*my_server_tree.get_children())
    # get server data back
    query_server_info()
    server_serverName_entry.delete(0, END)
    url_entry.delete(0, END)
    token_entry.delete(0, END)
    server_offline_entry.delete(0, END)


# Add server record
def add_server_record():
    NEW_PLEX_TOKEN = new_token_entry.get()
    NEW_PLEX_URL = new_url_entry.get()
    if NEW_PLEX_TOKEN == '' or NEW_PLEX_URL == '':
        return
    # Read config.ini file
    config_object = ConfigParser()
    config_object.read(config_path + "pum.ini")
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
    sess = requests.Session()
    # Ignore verifying the SSL certificate
    sess.verify = False  # '/path/to/certfile'
    # If verify is set to a path to a directory,
    # the directory must have been processed using the c_rehash utility supplied
    # with OpenSSL.
    if sess.verify is False:
        # Disable the warning that the request is insecure, we know that...
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    # test if server online
    try:
        plex = PlexServer(NEW_PLEX_URL, NEW_PLEX_TOKEN, session=sess)
    except:
        print("error connecting to server, check your inpout")
        tkinter.messagebox.showinfo(title="Connection error", message="input error or server Offline")
        #cursor.execute("INSERT IGNORE INTO plexservers SET server_offline = 0, token = %s, url = %s;", [NEW_PLEX_TOKEN, NEW_PLEX_URL])
    else:
        cursor.execute(
            "INSERT IGNORE INTO plexservers SET server_offline = 0, serverName = %s, token = %s, url = %s;",
            [plex.friendlyName, NEW_PLEX_TOKEN, NEW_PLEX_URL])

    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()
    # import data from new server
    global NEW_PLEX_SERVER
    NEW_PLEX_SERVER = "plex.friendlyName"
    multithreading_import_data()
    # clear my_server_tree
    my_server_tree.delete(*my_server_tree.get_children())
    # get server data back
    query_server_info()


# Create a Treeview Frame
server_tree_frame = Frame(server_tab)
#server_tree_frame.config(background="red")
#server_tree_frame.configure(background="#1F1F1F")
server_tree_frame.pack(fill="x", expand=1, pady=10)

# Create a Treeview Scrollbar
server_tree_scroll = Scrollbar(server_tree_frame)
#server_tree_scroll.configure(background="#1F1F1F")
server_tree_scroll.pack(side=RIGHT, fill=Y)

# Create The Treeview
my_server_tree = ttk.Treeview(server_tree_frame, yscrollcommand=server_tree_scroll.set, selectmode="extended")
my_server_tree.pack(fill="x") # need to check the fill="x"

# Configure the Scrollbar
server_tree_scroll.config(command=my_server_tree.yview, background="#1F1F1F")

# Define Our Columns
my_server_tree['columns'] = ("Server Name", "Token", "URL", "State")

# Format Our Columns
my_server_tree.column("#0", width=0, stretch=NO)
my_server_tree.column("Server Name", anchor=W, width=150)
my_server_tree.column("Token", anchor=W, width=200)
my_server_tree.column("URL", anchor=CENTER, width=250)
my_server_tree.column("State", anchor=CENTER, width=70)

# Create Headings
my_server_tree.heading("#0", text="", anchor=W)
my_server_tree.heading("Server Name", text="Server Name", anchor=W)
my_server_tree.heading("Token", text="Token", anchor=W)
my_server_tree.heading("URL", text="URL", anchor=CENTER)
my_server_tree.heading("State", text="State", anchor=CENTER)

# Create Striped Row Tags
my_server_tree.tag_configure('oddrow', background="#303030")
my_server_tree.tag_configure('evenrow', background="#2B2B2B")

# delete entry zone
# Add Record Entry Boxes
server_data_frame = LabelFrame(server_tab, text="Delete Server options")
server_data_frame.pack(fill="x", expand=1, padx=20)

# Configure the server_data_frame color
server_data_frame.configure(background="#282828",
                            foreground="white")

server_serverName_label = Label(server_data_frame, text="server name")
server_serverName_label.grid(row=0, column=0, padx=10, pady=10)
server_serverName_label.config(background="#282828",
                               foreground="white")
server_serverName_entry = Entry(server_data_frame, width=30)
server_serverName_entry.grid(row=0, column=1, padx=10, pady=10)
server_serverName_entry.config(state="disabled",
                               disabledbackground="#282828")

token_label = Label(server_data_frame, text="token")
token_label.grid(row=1, column=2, padx=10, pady=10)
token_label.config(background="#282828",
                   foreground="white")
token_entry = Entry(server_data_frame, width=30)
token_entry.grid(row=1, column=3, padx=10, pady=10)
token_entry.config(state="disabled",
                   disabledbackground="#282828")

url_label = Label(server_data_frame, text="URL")
url_label.grid(row=1, column=0, padx=10, pady=10)
url_label.config(background="#282828",
                 foreground="white")
url_entry = Entry(server_data_frame, width=30)
url_entry.grid(row=1, column=1, padx=10, pady=10)
url_entry.config(state="disabled",
                 disabledbackground="#282828")

server_offline_label = Label(server_data_frame, text="state")
server_offline_label.grid(row=0, column=2, padx=10, pady=10)
server_offline_label.config(background="#282828",
                            foreground="white")
server_offline_entry = Entry(server_data_frame, width=30)
server_offline_entry.grid(row=0, column=3, padx=10, pady=10)
server_offline_entry.config(state="disabled",
                            disabledbackground="#282828")

# delete server button
delete_server_button = Button(server_data_frame, text="Delete Record", command=delete_server_record)
delete_server_button.grid(row=1, column=4, padx=10, pady=10)
delete_server_button.config(background="#e5a00d", activebackground="#383838", foreground="white",
                            activeforeground="white", border="0", font='Helvetica 10 bold')

# Bind the treeview
my_server_tree.bind("<ButtonRelease>", select_server_record)

# add server zone
# Add Record Entry Boxes
server_add_data_frame = LabelFrame(server_tab, text="Add Server options")
server_add_data_frame.pack(fill="x", expand=1, padx=20)
# Configure the server_data_frame color
server_add_data_frame.configure(background="#282828",
                                foreground="white")
# URL label
new_url_label = Label(server_add_data_frame, text="URL")
new_url_label.grid(row=0, column=0, padx=10, pady=10)
new_url_label.config(background="#282828",
                     foreground="white")
# URL entry box
new_url_entry = Entry(server_add_data_frame, width=30)
new_url_entry.insert(0, "https://192.168.1.1:32400")
new_url_entry.grid(row=0, column=1, padx=10, pady=10)
# Token label
new_token_label = Label(server_add_data_frame, text="token")
new_token_label.grid(row=0, column=2, padx=10, pady=10)
new_token_label.config(background="#282828",
                       foreground="white")
# Token entry box
new_token_entry = Entry(server_add_data_frame, width=30)
new_token_entry.insert(0, "myplextoken")
new_token_entry.grid(row=0, column=3, padx=10, pady=10)
# add server button
add_server_button = Button(server_add_data_frame, text="add server", command=add_server_record)
add_server_button.grid(row=0, column=4, padx=10, pady=10)
add_server_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white",
                         border="0", font='Helvetica 10 bold')




# server count
cursor.execute("SELECT COUNT(DISTINCT serverName) FROM plexservers;")
server_count_result = cursor.fetchall()
# library count
cursor.execute("SELECT COUNT(DISTINCT library) FROM plexlibraries;")
library_count_result = cursor.fetchall()
# Add plex server info frame
plex_server_info_frame = LabelFrame(server_tab, text="Plex Server Information")
plex_server_info_frame.pack(fill="x", expand=1, padx=20)
# Configure the plex_server_info_frame color
plex_server_info_frame.configure(background="#282828",
                                 foreground="white")
# display server count
server_count_label = Label(plex_server_info_frame, text="number of servers : ")
server_count_label.grid(row=0, column=0, padx=10, pady=10)
server_count_label.config(background="#282828",
                          foreground="white")
server_count_result_label = Label(plex_server_info_frame, text=server_count_result)
server_count_result_label.grid(row=0, column=1)
server_count_result_label.config(background="#282828",
                                 foreground="white")
# display separation label
server_separation_label = Label(plex_server_info_frame, text="  / ")
server_separation_label.grid(row=0, column=2, padx=10, pady=10)
server_separation_label.config(background="#282828",
                          foreground="white")
# display library count
library_count_label = Label(plex_server_info_frame, text="number of libraries : ")
library_count_label.grid(row=0, column=3, padx=10, pady=10)
library_count_label.config(background="#282828",
                          foreground="white")
library_count_result_label = Label(plex_server_info_frame, text=library_count_result)
library_count_result_label.grid(row=0, column=4)
library_count_result_label.config(background="#282828",
                                 foreground="white")

# **********************************************************************************************************************
# ********************************************* setting panel **********************************************************
# **********************************************************************************************************************
# setting gui
# conf frame
conf_frame = LabelFrame(conf_tab)
conf_frame.configure(background="#1F1F1F", border="0")  # color code 1F1F1F
conf_frame.pack(padx=20, anchor="w", fill="x")
# set tabs
notebook2 = ttk.Notebook(conf_frame, style='TNotebook')

general_tab: Frame = Frame(notebook2)  # frame for general page
communication_tab: Frame = Frame(notebook2)  # frame for communication page
#user_option_tab: Frame = Frame(notebook2)  # frame for user_option page
#gui_option_tab: Frame = Frame(notebook2)  # frame for gui_option page
backup_restore_tab: Frame = Frame(notebook2)  # frame for backup_restore page

notebook2.add(general_tab, text="General")
notebook2.add(communication_tab, text="Communication")
#notebook2.add(user_option_tab, text="User options")
#notebook2.add(gui_option_tab, text="GUI options")
notebook2.add(backup_restore_tab, text="Backup & Restore")

general_tab.configure(background="#1F1F1F")
#general_tab.pack(fill='both')
communication_tab.configure(background="#1F1F1F")
#user_option_tab.configure(background="#1F1F1F")
#gui_option_tab.configure(background="#1F1F1F")
backup_restore_tab.configure(background="#1F1F1F")
# update_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')
notebook2.pack(expand=True, fill="both")  # expand to space not used

# GENERAL TAB **********************************************************************************************************
# Hide Guest
# hide guest button
def hide_guest_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['hide_guest'] = str(hide_guest_but.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)
    global hide_guest_str
    hide_guest_str = str(hide_guest_but.get())
    # clear my_user_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get user data back
    query_user_info()


# hide users with no lib button
def hide_no_lib_users_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['hide_no_lib_users'] = str(hide_no_lib_users_but.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)
    global hide_no_lib_users_str
    hide_no_lib_users_str = str(hide_no_lib_users_but.get())
    # clear my_user_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get user data back
    query_user_info()



def save_user_options_conf_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['hide_guest'] = str(hide_guest_but.get())
    config_object['CONF']['hide_no_lib_users'] = str(hide_no_lib_users_but.get())
    config_object['CONF']['remove_user_access'] = str(remove_user_access_but.get())
    config_object['CONF']['sync_plex_delai'] = str(sync_plex_delai_entry.get())

    #config_object['CONF']['delete_user'] = str(delete_user_but.get())
    #config_object['CONF']['delete_user_delay'] = str(delete_user_conf.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)
    global hide_guest_str
    hide_guest_str = str(hide_guest_but.get())
    global hide_no_lib_users_str
    hide_no_lib_users_str = str(hide_no_lib_users_but.get())
    global sync_plex_delai_str
    sync_plex_delai_str = str(sync_plex_delai_entry.get())
    # clear my_user_tree
    my_user_tree.delete(*my_user_tree.get_children())
    # get user data back
    query_user_info()

# hide guest button
hide_guest_but = IntVar(value=hide_guest_str)
Checkbutton(general_tab, text="Hide Guest user", variable=hide_guest_but, onvalue=1, offvalue=0,
            activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F",
            foreground="white", selectcolor="grey", takefocus="0", bd="0").grid(row=0, column=0, padx=10, pady=10, sticky='w')

# hide users with no lib button
hide_no_lib_users_but = IntVar(value=hide_no_lib_users_str)
Checkbutton(general_tab, text="Hide user without libraries", variable=hide_no_lib_users_but, onvalue=1, offvalue=0,
            activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F",
            foreground="white", selectcolor="grey", takefocus="0", bd="0").grid(row=1, column=0, padx=10, pady=10, sticky='w')

# remove access when account has expired
remove_user_access_but = IntVar(value=remove_user_access)
Checkbutton(general_tab, text="remove access when account has expired", variable=remove_user_access_but, onvalue=1,
            offvalue=0, activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F",
            foreground="white", selectcolor="grey", takefocus="0", bd="0").grid(row=2, column=0, padx=10, pady=10, sticky='w')
remove_user_access_but_description_label = Label(general_tab, text="Librairies access will be removed from user")
remove_user_access_but_description_label.grid(row=3, column=0, padx=20, sticky='w')
remove_user_access_but_description_label.config(background="#1F1F1F",
                                                foreground="grey")

# sync app with plex entry
sync_plex_delai_label = Label(general_tab, text="delay in seconds, between every plex sync (default is 24 Hours)")
sync_plex_delai_label.grid(row=4, column=0, padx=10, pady=10, sticky='w')
sync_plex_delai_label.config(background="#1F1F1F",
                             foreground="white")
sync_plex_delai_entry = Entry(general_tab)
sync_plex_delai_entry.insert(0, sync_plex_delai)
sync_plex_delai_entry.grid(row=4, column=1, padx=10, pady=10, sticky='w')
'''# delete user when expired
delete_user_but = IntVar(value=delete_user)
Checkbutton(general_tab, text="delete expired users", variable=delete_user_but, onvalue=1, offvalue=0,
            activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F", foreground="white",
            selectcolor="grey", takefocus="0", bd="0").grid(row=4, column=0, padx=10, pady=10, sticky='w')
delay_after_warning = Label(general_tab, text="Delay after warning", font=("helvetica, 10"))
delay_after_warning.grid(row=5, column=0, padx=10, pady=10, sticky='w')
delay_after_warning.config(background="#1F1F1F",
                        foreground="white")'''

'''delete_user_conf = Entry(general_tab, background="#555555", foreground="white", relief=FLAT)
delete_user_conf.delete(0, END)
delete_user_conf.insert(0, delete_user_delay_str)
delete_user_conf.grid(row=4, column=0, padx=3, sticky='w')
delete_user_conf_label = Label(general_tab, text="Delay in days after expiration to delete user")
delete_user_conf_label.grid(row=5, column=0, sticky='w')
delete_user_conf_label.config(background="#1F1F1F",
                        foreground="grey")
'''
save_user_options_settings_button = Button(general_tab, text="Save", command=save_user_options_conf_command)
save_user_options_settings_button.grid(row=20, column=0, padx=300, pady=10, sticky='W')
save_user_options_settings_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')



# **********************************************************************************************************************
# ********************************************* help & info panel ******************************************************
# **********************************************************************************************************************
# help & info frame
help_and_info_tab_frame = LabelFrame(help_and_info_tab)
help_and_info_tab_frame.configure(background="#1F1F1F", border="0")
help_and_info_tab_frame.pack(padx=20, anchor="w")
# help & info page
# get version number in VERSION file
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as handle:
    for version in handle.readlines():
        version = version.strip()
# display version number
version_label = Label(help_and_info_tab_frame, text="Version: " + str(version))
version_label.configure(background="#1F1F1F", border="0", foreground="white")
version_label.grid(row=0, column=0, padx=10, pady=10)


# Run to pull data from db on start
query_user_info()
query_server_info()

# Commit changes
mydb.commit()
# Close connexion
mydb.close()

root.mainloop()

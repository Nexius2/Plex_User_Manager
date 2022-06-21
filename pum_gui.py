from tkinter import *
from tkinter import ttk
from configparser import ConfigParser
import mysql.connector, os, sys, time

root = Tk()
root.title('Plex User Manager')
#root.iconbitmap(r'./images/pum_logo.ico')
#logo = PhotoImage(file='./images/pum_logo.png')
#root.call('wm', 'iconphoto', root._w, logo)
root.geometry("1100x800")


# Configure the root color
# root.configure(background="#1F1F1F")

# tabs_frame = Frame(root)
# tabs_frame.pack()
# style = ttk.Style(tabs_frame)
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

home_tab: Frame = Frame(notebook)  # frame for home page
conf_tab: Frame = Frame(notebook)  # frame for conf page
help_and_info_tab: Frame = Frame(notebook)  # frame for help & info page

notebook.add(home_tab, text="Home")
notebook.add(conf_tab, text="Settings")
notebook.add(help_and_info_tab, text="Help & info")

home_tab.configure(background="#1F1F1F")
conf_tab.configure(background="#1F1F1F")
help_and_info_tab.configure(background="#1F1F1F")
# update_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

notebook.pack(expand=True, fill="both")  # expand to space not used

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

# Create database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS pum")

# Create table plexusers
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
     hidden INT(10) DEFAULT 0, \
     PRIMARY KEY(userID, serverName) );")

# Create table tempusers
cursor.execute("CREATE TABLE IF NOT EXISTS tempusers(serverName VARCHAR(255) NOT NULL, \
     userID INT NOT NULL, \
     PRIMARY KEY(userID, serverName) );")

# check is db is empty to sync
cursor.execute("SELECT userID FROM plexusers;")
records = cursor.fetchall()
if not records:
    exec(open("./sync.py").read())

# Commit changes
mydb.commit()
# Close connexion
mydb.close()

# Get all user information from db
def query_user_info():
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
    hidden_str = userinfo["hide_guest"]
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
    if hidden_str == "1":
        cursor.execute("SELECT * FROM plexusers WHERE hidden = 0;")
    else:
        cursor.execute("SELECT * FROM plexusers;")
    records = cursor.fetchall()
    # Add our data to the screen
    global count
    count = 0

    for record in records:
        if count % 2 == 0:
            # my_tree.insert(parent='', index='end', iid=count, text='',
            my_tree.insert(parent='', index='end', iid=str(count), text='',
                           values=(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], record[12], record[13], record[14], record[15], record[16], record[17], record[18]),
                           tags=('evenrow',))
        else:
            # my_tree.insert(parent='', index='end', iid=count, text='',
            my_tree.insert(parent='', index='end', iid=str(count), text='',
                           values=(record[0], record[1], record[2], record[3], record[4], record[5], record[6], record[7], record[8], record[9], record[10], record[11], record[12], record[13], record[14], record[15], record[16], record[17], record[18]),
                           tags=('oddrow',))
        # increment counter
        count += 1
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()

# Add Some Style
# style = ttk.Style()

# Pick A Theme
# style.theme_use('default')

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

# Create a Treeview Frame
tree_frame = Frame(home_tab)
tree_frame.configure(background="#1F1F1F")
tree_frame.pack(fill="x", expand=1, pady=10)

# Create a Treeview Scrollbar
tree_scroll = Scrollbar(tree_frame)
tree_scroll.configure(background="#1F1F1F")
tree_scroll.pack(side=RIGHT, fill=Y)

# Create The Treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode="extended")
#Treeview.config(backgound="#212121")
my_tree.pack()

# Configure the Scrollbar
tree_scroll.config(command=my_tree.yview)


# Define Our Columns
my_tree['columns'] = ("First Name", "Last Name", "Username", "email", "servername", "expire_date", "sections")
#my_tree.config("columns",
#               background="#212121")

# Format Our Columns
my_tree.column("#0", width=0, stretch=NO)
my_tree.column("First Name", anchor=W, width=100)
my_tree.column("Last Name", anchor=W, width=100)
my_tree.column("Username", anchor=CENTER, width=180)
my_tree.column("email", anchor=CENTER, width=250)
my_tree.column("servername", anchor=CENTER, width=140)
my_tree.column("expire_date", anchor=CENTER, width=120)
my_tree.column("sections", anchor=CENTER, width=140)

# Create Headings
my_tree.heading("#0", text="", anchor=W)
my_tree.heading("First Name", text="First Name", anchor=W)
my_tree.heading("Last Name", text="Last Name", anchor=W)
my_tree.heading("Username", text="Username", anchor=CENTER)
my_tree.heading("email", text="email", anchor=CENTER)
my_tree.heading("servername", text="servername", anchor=CENTER)
my_tree.heading("expire_date", text="expire date", anchor=CENTER)
my_tree.heading("sections", text="sections", anchor=CENTER)

# Select record
def select_record(e):
        # refresh page when is synced
        if os.path.isfile('./synced'):
            # display message box
            #global update_box
            #update_box = Toplevel(root)
            #update_box.title("information")
            #update_box.iconbitmap('./images/pum_logo.ico')
            #update_box.geometry("200x100")
            #update_box.config(bg="#282828")
            #update_box_label = Label(update_box, text="Updating...", bg="#282828", fg="white")
            #update_box_label.pack(pady="10")
            #update_box_frame = Frame(update_box, bg="#282828")
            #update_box_frame.pack(pady=5)
            #time.sleep(3)  # time for message
            os.remove(str(''.join('./synced')))
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

        # Clear entry boxes
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
        selected = my_tree.focus()
        # Grab record values
        values = my_tree.item(selected, 'values')
        print(values)

        # Output entry boxes
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
        sections_entry.insert(0, values[6])
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
        filterMovies_entry.insert(0, values[10])
        filterMovies_entry.config(state="disabled",
                                  disabledbackground="#282828")
        filterMusic_entry.insert(0, values[11])
        filterMusic_entry.config(state="disabled",
                                 disabledbackground="#282828")
        filterTelevision_entry.insert(0, values[12])
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

# Update Record
def update_record():
        # Grab the record number
        selected = my_tree.focus()
        # Update record
        my_tree.item(selected, text="", values=(first_name_entry.get(), last_name_entry.get(), username_entry.get(), email_entry.get(), serverName_entry.get(), account_expire_date_entry.get(), sections_entry.get(), allowSync_entry.get(), camera_entry.get(), channels_entry.get(), filterMovies_entry.get(), filterMusic_entry.get(), filterTelevision_entry.get(), title_entry.get(), is_on_plex_entry.get(), account_creation_date_entry.get(), account_renewed_date_entry.get(), userID_entry.get(), description_entry.get(),))
        # first_name = first_name_entry.get()
        # if first_name is None:
        #    first_name = ''
        # last_name = last_name_entry.get()
        # if last_name is None:
        #    last_name = ''
        # description = description_entry.get()
        # if description is None:
        #    description = ''
        # id_value = userID_entry.get()
        # print(first_name)
        # inputs = (first_name, last_name, description, id_value)
        # print(inputs)
        # print(first_name, last_name, description, account_creation_date, account_renewed_date, account_expire_date)
        # test for blank date

        if not account_creation_date_entry.get() == "None" and account_creation_date_entry.get() != old_account_creation_date_entry:
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
            cursor.execute("""UPDATE plexusers SET
                                		account_creation_date = %s
                                		WHERE userID = %s AND serverName = %s""",
                           [
                               account_creation_date_entry.get(),
                               userID_entry.get(),
                               serverName_entry.get()
                           ])
            # Commit changes
            mydb.commit()
            # Close connexion
            mydb.close()

        if not account_renewed_date_entry.get() == "None" and account_renewed_date_entry.get() != old_account_renewed_date_entry:
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
            cursor.execute("""UPDATE plexusers SET
                                		account_renewed_date = %s
                                		WHERE userID = %s AND serverName = %s""",
                           [
                               account_renewed_date_entry.get(),
                               userID_entry.get(),
                               serverName_entry.get()
                           ])
            # Commit changes
            mydb.commit()
            # Close connexion
            mydb.close()

        if not account_expire_date_entry.get() == "None" and account_expire_date_entry.get() != old_account_expire_date_entry:
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
            cursor.execute("""UPDATE plexusers SET
                    		account_expire_date = %s
                    		WHERE userID = %s AND serverName = %s""",
                           [
                               account_expire_date_entry.get(),
                               userID_entry.get(),
                               serverName_entry.get()
                           ])
            # Commit changes
            mydb.commit()
            # Close connexion
            mydb.close()

        # SQL command
        # sql3 = """UPDATE plexusers SET first_name = '%s', last_name = '%s', account_creation_date = %s, account_renewed_date = %s, account_expire_date = %s, description = '%s' WHERE userID = '%s';"""
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
        cursor.execute("""UPDATE plexusers SET
        		first_name = %s,
        		last_name = %s,
        		description = %s
        		WHERE userID = %s AND serverName = %s""",
                       [
                           first_name_entry.get(),
                           last_name_entry.get(),
                           description_entry.get(),
                           userID_entry.get(),
                           serverName_entry.get()
                       ])
        # cursor.execute(sql3, inputs)
        # Commit changes
        mydb.commit()
        # Close connexion
        mydb.close()


# user count
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
# count users
cursor = mydb.cursor()
sql_user_count = "SELECT COUNT(userID) FROM plexusers;"
cursor.execute(sql_user_count)
# count servers
user_count_result = cursor.fetchall()
sql_server_count = "SELECT COUNT(DISTINCT serverName) FROM plexusers;"
cursor.execute(sql_server_count)
# count sections
server_count_result = cursor.fetchall()
sql_library_count = "SELECT COUNT(DISTINCT sections) FROM plexusers;"
cursor.execute(sql_library_count)
library_count_result = cursor.fetchall()
# display all servers
server_list = "SELECT DISTINCT serverName FROM plexusers;"
cursor.execute(server_list)
global servers_result
servers_result = cursor.fetchall()
# Commit changes
mydb.commit()
# Close connexion
mydb.close()

# Create Striped Row Tags
my_tree.tag_configure('oddrow', background="#303030")
my_tree.tag_configure('evenrow', background="#2B2B2B")

# Add Record Entry Boxes
data_frame = LabelFrame(home_tab, text="User information")
data_frame.pack(fill="x", expand=1, padx=20)

# Configure the data_frame color
data_frame.configure(background="#282828",
                     foreground="white")

first_name_label = Label(data_frame, text="First Name")
first_name_label.grid(row=0, column=0, padx=10, pady=10)
first_name_label.config(background="#282828",
                        foreground="white")
first_name_entry = Entry(data_frame)
first_name_entry.grid(row=0, column=1, padx=10, pady=10)

last_name_label = Label(data_frame, text="Last Name")
last_name_label.grid(row=0, column=2, padx=10, pady=10)
last_name_label.config(background="#282828",
                        foreground="white")
last_name_entry = Entry(data_frame)
last_name_entry.grid(row=0, column=3, padx=10, pady=10)

username_label = Label(data_frame, text="Username")
username_label.grid(row=0, column=4, padx=10, pady=10)
username_label.config(background="#282828",
                        foreground="white")
username_entry = Entry(data_frame)
username_entry.grid(row=0, column=5, padx=10, pady=10)
username_entry.config(disabledbackground="#282828",
                        state="disabled")

email_label = Label(data_frame, text="email")
email_label.grid(row=1, column=0, padx=10, pady=10)
email_label.config(background="#282828",
                        foreground="white")
email_entry = Entry(data_frame)
email_entry.grid(row=1, column=1, padx=10, pady=10)
email_entry.config(disabledbackground="#282828",
                   state="disabled")

serverName_label = Label(data_frame, text="serverName")
serverName_label.grid(row=1, column=2, padx=10, pady=10)
serverName_label.config(background="#282828",
                        foreground="white")
serverName_entry = Entry(data_frame)
serverName_entry.grid(row=1, column=3, padx=10, pady=10)
serverName_entry.config(disabledbackground="#282828",
                        state="disabled")

account_expire_date_label = Label(data_frame, text="expire date")
account_expire_date_label.grid(row=2, column=4, padx=10, pady=10)
account_expire_date_label.config(background="#282828",
                        foreground="white")
account_expire_date_entry = Entry(data_frame)
account_expire_date_entry.grid(row=2, column=5, padx=10, pady=10)

sections_label = Label(data_frame, text="sections")
sections_label.grid(row=3, column=0, padx=10, pady=10)
sections_label.config(background="#282828",
                        foreground="white")
sections_entry = Entry(data_frame)
sections_entry.grid(row=3, column=1, padx=10, pady=10)
sections_entry.config(disabledbackground="#282828",
                      state="disabled")

title_label = Label(data_frame, text="title")
title_label.grid(row=3, column=2, padx=10, pady=10)
title_label.config(background="#282828",
                        foreground="white")
title_entry = Entry(data_frame)
title_entry.grid(row=3, column=3, padx=10, pady=10)
title_entry.config(disabledbackground="#282828",
                   state="disabled")

userID_label = Label(data_frame, text="userID")
userID_label.grid(row=3, column=4, padx=10, pady=10)
userID_label.config(background="#282828",
                        foreground="white")
userID_entry = Entry(data_frame)
userID_entry.grid(row=3, column=5, padx=10, pady=10)
userID_entry.config(disabledbackground="#282828",
                    state="disabled")

account_creation_date_label = Label(data_frame, text="account_creation_date")
account_creation_date_label.grid(row=2, column=0, padx=10, pady=10)
account_creation_date_label.config(background="#282828",
                        foreground="white")
# global account_creation_date_entry
account_creation_date_entry = Entry(data_frame)
account_creation_date_entry.grid(row=2, column=1, padx=10, pady=10)

account_renewed_date_label = Label(data_frame, text="account_renewed_date")
account_renewed_date_label.grid(row=2, column=2, padx=10, pady=10)
account_renewed_date_label.config(background="#282828",
                        foreground="white")
account_renewed_date_entry = Entry(data_frame)
account_renewed_date_entry.grid(row=2, column=3, padx=10, pady=10)

description_label = Label(data_frame, text="description")
description_label.grid(row=1, column=4, padx=10, pady=10)
description_label.config(background="#282828",
                        foreground="white")
description_entry = Entry(data_frame)
description_entry.grid(row=1, column=5, padx=10, pady=10)

allowSync_label = Label(data_frame, text="allowSync")
allowSync_label.grid(row=4, column=0, padx=10, pady=10)
allowSync_label.config(background="#282828",
                        foreground="white")
allowSync_entry = Entry(data_frame)
allowSync_entry.grid(row=4, column=1, padx=10, pady=10)
allowSync_entry.config(disabledbackground="#282828",
                       state="disabled")

camera_label = Label(data_frame, text="camera")
camera_label.grid(row=4, column=2, padx=10, pady=10)
camera_label.config(background="#282828",
                        foreground="white")
camera_entry = Entry(data_frame)
camera_entry.grid(row=4, column=3, padx=10, pady=10)
camera_entry.config(disabledbackground="#282828",
                    state="disabled")

channels_label = Label(data_frame, text="channels")
channels_label.grid(row=4, column=4, padx=10, pady=10)
channels_label.config(background="#282828",
                        foreground="white")
channels_entry = Entry(data_frame)
channels_entry.grid(row=4, column=5, padx=10, pady=10)
channels_entry.config(disabledbackground="#282828",
                      state="disabled")

filterMovies_label = Label(data_frame, text="filterMovies")
filterMovies_label.grid(row=5, column=0, padx=10, pady=10)
filterMovies_label.config(background="#282828",
                        foreground="white")
filterMovies_entry = Entry(data_frame)
filterMovies_entry.grid(row=5, column=1, padx=10, pady=10)
filterMovies_entry.config(disabledbackground="#282828",
                          state="disabled")

filterMusic_label = Label(data_frame, text="filterMusic")
filterMusic_label.grid(row=5, column=2, padx=10, pady=10)
filterMusic_label.config(background="#282828",
                        foreground="white")
filterMusic_entry = Entry(data_frame)
filterMusic_entry.grid(row=5, column=3, padx=10, pady=10)
filterMusic_entry.config(disabledbackground="#282828",
                         state="disabled")

filterTelevision_label = Label(data_frame, text="filterTelevision")
filterTelevision_label.grid(row=5, column=4, padx=10, pady=10)
filterTelevision_label.config(background="#282828",
                        foreground="white")
filterTelevision_entry = Entry(data_frame)
filterTelevision_entry.grid(row=5, column=5, padx=10, pady=10)
filterTelevision_entry.config(disabledbackground="#282828",
                              state="disabled")

is_on_plex_label = Label(data_frame, text="is on plex")
is_on_plex_label.grid(row=6, column=4, padx=10, pady=10)
is_on_plex_label.config(background="#282828",
                        foreground="white")
is_on_plex_entry = Entry(data_frame)
is_on_plex_entry.grid(row=6, column=5, padx=10, pady=10)
is_on_plex_entry.config(disabledbackground="#282828",
                              state="disabled")

update_button = Button(data_frame, text="Update Record", command=update_record)
update_button.grid(row=6, column=0, padx=10, pady=10)
update_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

# Bind the treeview
my_tree.bind("<ButtonRelease>", select_record)

# Add plex info frame
plex_info_frame = LabelFrame(home_tab, text="Plex Information")
plex_info_frame.pack(fill="x", expand=1, padx=20)

# Configure the plex_info_frame color
plex_info_frame.configure(background="#282828",
                       foreground="white")
# plex user count
user_count_label = Label(plex_info_frame, text="number of users : ")
user_count_label.grid(row=0, column=0, padx=10, pady=10)
user_count_label.config(background="#282828",
                        foreground="white")
user_count_result_label = Label(plex_info_frame, text=user_count_result)
user_count_result_label.grid(row=0, column=1)
user_count_result_label.config(background="#282828",
                        foreground="white")
# plex server count
server_count_label = Label(plex_info_frame, text="number of servers : ")
server_count_label.grid(row=0, column=2, padx=10, pady=10)
server_count_label.config(background="#282828",
                        foreground="white")
server_count_result_label = Label(plex_info_frame, text=server_count_result)
server_count_result_label.grid(row=0, column=3)
server_count_result_label.config(background="#282828",
                        foreground="white")
# plex library count
library_count_label = Label(plex_info_frame, text="number of libraries : ")
library_count_label.grid(row=0, column=4, padx=10, pady=10)
library_count_label.config(background="#282828",
                        foreground="white")
library_count_result_label = Label(plex_info_frame, text=library_count_result)
library_count_result_label.grid(row=0, column=5)
library_count_result_label.config(background="#282828",
                        foreground="white")

# conf frame
conf_frame = LabelFrame(conf_tab)
conf_frame.configure(background="#1F1F1F", border="0")  # color code 1F1F1F
conf_frame.pack(padx=20, anchor="w", fill="x")
# conf_tab page






'''
style.theme_create("pum_conf_theme", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0],
                                    "tabposition": 'ws',
                                    "background": "#1F1F1F",
                                    "borderwidth": "0",
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

style.theme_use("pum_conf_theme")
'''

# set tabs
notebook2 = ttk.Notebook(conf_frame, style='TNotebook')

general_tab: Frame = Frame(notebook2)  # frame for general page
communication_tab: Frame = Frame(notebook2)  # frame for communication page
user_option_tab: Frame = Frame(notebook2)  # frame for user_option page
gui_option_tab: Frame = Frame(notebook2)  # frame for gui_option page
backup_restore_tab: Frame = Frame(notebook2)  # frame for backup_restore page

notebook2.add(general_tab, text="General")
notebook2.add(communication_tab, text="Communication")
notebook2.add(user_option_tab, text="User options")
notebook2.add(gui_option_tab, text="GUI options")
notebook2.add(backup_restore_tab, text="Backup & Restore")

general_tab.configure(background="#1F1F1F")
#general_tab.pack(fill='both')
communication_tab.configure(background="#1F1F1F")
user_option_tab.configure(background="#1F1F1F")
gui_option_tab.configure(background="#1F1F1F")
backup_restore_tab.configure(background="#1F1F1F")
# update_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')
notebook2.pack(expand=True, fill="both")  # expand to space not used








'''
#left frame
left_conf_frame = LabelFrame(conf_frame)
left_conf_frame.config(background="#1F1F1F", border="0")  # color code 1F1F1F
left_conf_frame.pack(side=LEFT)
'''
# Read config.ini file
config_object = ConfigParser()
config_object.read(".config/pum.ini")
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
# cron_conf_str = userinfo["cron_conf"]
nbr_backup_to_keep_str = userinfo["nbr_backup_to_keep"]
# Read config.ini file for plex
config_object = ConfigParser()
config_object.read(".config/plexapi/config.ini")
# Get the conf info
userinfo = config_object["auth"]
plex_url_str = userinfo["server_baseurl"]
plex_token_str = userinfo["server_token"]


# buttons
# warn users of near expiration
# function warn_user_near_expiration_command
def warn_user_near_expiration_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['warn_user_near_expiration'] = str(warn_user_near_expiration_but.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)
warn_user_near_expiration_but = IntVar(value=warn_user_near_expiration)
Checkbutton(communication_tab, text="warn users of near expiration", variable=warn_user_near_expiration_but, onvalue=1, offvalue=0, activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F", foreground="white", selectcolor="grey", takefocus="0", bd="0", command=warn_user_near_expiration_command).grid(row=0, column=0, padx=10, pady=10)
delay_before_warning = Entry(communication_tab)
delay_before_warning.delete(0, END)
delay_before_warning.insert(0, warn_user_near_expiration_delay)
delay_before_warning.grid(row=1, column=0, padx=10, pady=10)
delay_before_warning_label = Label(communication_tab, text="(delay in days before expiration to warn user)")
delay_before_warning_label.grid(row=1, column=1)
delay_before_warning_label.config(background="#1F1F1F",
                        foreground="white")
# warn users of account expiration
# function warn_user_account_expiration_command
def warn_user_account_expiration_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['warn_user_account_expiration'] = str(warn_user_account_expiration_but.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)
warn_user_account_expiration_but = IntVar(value=warn_user_account_expiration)
Checkbutton(communication_tab, text="warn users of account expiration", variable=warn_user_account_expiration_but, onvalue=1, offvalue=0, activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F", foreground="white", selectcolor="grey", takefocus="0", bd="0", command=warn_user_account_expiration_command).grid(row=2, column=0, padx=10, pady=10)

#######################################
#        Settings/User options        #
#######################################
def save_user_options_conf_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['remove_user_access'] = str(remove_user_access_but.get())
    config_object['CONF']['delete_user'] = str(delete_user_but.get())
    config_object['CONF']['delete_user_delay'] = str(delete_user_conf.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)

# remove access when account has expired
remove_user_access_but = IntVar(value=remove_user_access)
Checkbutton(user_option_tab, text="remove access when account has expired", variable=remove_user_access_but, onvalue=1, offvalue=0, activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F", foreground="white", selectcolor="grey", takefocus="0", bd="0").grid(row=0, column=0, sticky='w')
remove_user_access_but_description_label = Label(user_option_tab, text="Librairies will be removed from user")
remove_user_access_but_description_label.grid(row=1, column=0, sticky='w')
remove_user_access_but_description_label.config(background="#1F1F1F",
                        foreground="grey")
# delete user when expired
delete_user_but = IntVar(value=delete_user)
Checkbutton(user_option_tab, text="delete user when expired", variable=delete_user_but, onvalue=1, offvalue=0, activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F", foreground="white", selectcolor="grey", takefocus="0", bd="0").grid(row=2, column=0, sticky='w')
delay_after_warning = Label(user_option_tab, text="Delay after warning", font=("helvetica, 10"))
delay_after_warning.grid(row=3, column=0, sticky='w')
delay_after_warning.config(background="#1F1F1F",
                        foreground="white")
delete_user_conf = Entry(user_option_tab, background="#555555", foreground="white", relief=FLAT)
delete_user_conf.delete(0, END)
delete_user_conf.insert(0, delete_user_delay_str)
delete_user_conf.grid(row=4, column=0, padx=3, sticky='w')
delete_user_conf_label = Label(user_option_tab, text="Delay in days after expiration to delete user")
delete_user_conf_label.grid(row=5, column=0, sticky='w')
delete_user_conf_label.config(background="#1F1F1F",
                        foreground="grey")
save_user_options_settings_button = Button(user_option_tab, text="Save", command=save_user_options_conf_command)
save_user_options_settings_button.grid(row=6, column=0, padx=3, pady=10, sticky='w')
save_user_options_settings_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

#######################################
#           Settings/general          #
#######################################
# plex_sync_delay_conf_command function
def save_general_conf_command():
    pum_config_object = ConfigParser()
    pum_config_object.read(".config/pum.ini")
    pum_config_object['CONF']['plex_db_sync'] = str(plex_sync_delay_conf.get())
    with open(".config/pum.ini", 'w') as pum_configfile:
        pum_config_object.write(pum_configfile)
    plex_config_object = ConfigParser()
    plex_config_object.read(".config/plexapi/config.ini")
    plex_config_object['auth']['server_baseurl'] = str(plex_url_conf.get())
    plex_config_object['auth']['server_token'] = str(plex_token_conf.get())
    with open(".config/plexapi/config.ini", 'w') as plex_configfile:
        plex_config_object.write(plex_configfile)

# Plex sync
# plex_sync_conf_frame_left = Frame(general_tab, background="yellow", width=1)
# plex_sync_conf_frame_left.configure(background="#1F1F1F")
#plex_sync_conf_frame_right = Frame(general_tab, background="#1F1F1F", width=100)
# plex_sync_conf_frame.pack(fill='both')
plex_sync_delay_conf = Entry(general_tab, width=10, background="#555555", foreground="white", relief=FLAT)
plex_sync_delay_conf.delete(0, END)
plex_sync_delay_conf.insert(0, plex_db_sync_str)
plex_sync_delay_conf.grid(row=1, column=0, padx=3, sticky='w')
plex_sync_delay_conf_label = Label(general_tab, text="Plex db sync delay", font=("helvetica, 10"))
plex_sync_delay_conf_label.grid(row=0, column=0, sticky='w')
plex_sync_delay_conf_label.config(background="#1F1F1F",
                        foreground="white")
plex_sync_delay_conf_label2 = Label(general_tab, text="sync will run every X hours (default: 24)")
plex_sync_delay_conf_label2.grid(row=2, column=0, sticky='w')
plex_sync_delay_conf_label2.config(background="#1F1F1F",
                        foreground="#555555")

# Plex conf
plex_url_conf = Entry(general_tab, width=25, background="#555555", foreground="white", relief=FLAT)
plex_url_conf.delete(0, END)
plex_url_conf.insert(0, plex_url_str)
plex_url_conf.grid(row=4, column=0, padx=3, sticky='w')
plex_url_conf_label = Label(general_tab, text="Plex URL", font=("helvetica, 10"))
plex_url_conf_label.grid(row=3, column=0, sticky='w')
plex_url_conf_label.config(background="#1F1F1F",
                        foreground="white")
plex_token_conf = Entry(general_tab, width=25, background="#555555", foreground="white", relief=FLAT)
plex_token_conf.delete(0, END)
plex_token_conf.insert(0, plex_token_str)
plex_token_conf.grid(row=6, column=0, padx=3, sticky='w')
plex_token_conf_label = Label(general_tab, text="Plex token", font=("helvetica, 10"))
plex_token_conf_label.grid(row=5, column=0, sticky='w')
plex_token_conf_label.config(background="#1F1F1F",
                        foreground="white")
save_general_settings_button = Button(general_tab, text="Save", command=save_general_conf_command)
save_general_settings_button.grid(row=7, column=0, padx=3, pady=10, sticky='w')
save_general_settings_button.config(background="#e5a00d", activebackground="#383838", foreground="white", activeforeground="white", border="0", font='Helvetica 10 bold')

#######################################
#      Settings/Backup & restore      #
#######################################
nbr_backup_to_keep_conf = Entry(backup_restore_tab, width=3)
nbr_backup_to_keep_conf.delete(0, END)
nbr_backup_to_keep_conf.insert(0, nbr_backup_to_keep_str)
nbr_backup_to_keep_conf.grid(row=0, column=1, padx=10, pady=10)
nbr_backup_to_keep_conf_label = Label(backup_restore_tab, text="Keep backup for")
nbr_backup_to_keep_conf_label.grid(row=0, column=0)
nbr_backup_to_keep_conf_label.config(background="#1F1F1F",
                        foreground="white")
nbr_backup_to_keep_conf_label = Label(backup_restore_tab, text="days")
nbr_backup_to_keep_conf_label.grid(row=0, column=2)
nbr_backup_to_keep_conf_label.config(background="#1F1F1F",
                        foreground="white")


#######################################
#        Settings/GUI options         #
#######################################
# Hide Guest
# function hide_guest_command
def hide_guest_command():
    config_object = ConfigParser()
    config_object.read(".config/pum.ini")
    config_object['CONF']['hide_guest'] = str(hide_guest_but.get())
    with open(".config/pum.ini", 'w') as configfile:
        config_object.write(configfile)
    # mark as synced to reload treeview
    synced = open('./synced', "w")
    synced.close()
hide_guest_but = IntVar(value=hide_guest_str)
Checkbutton(gui_option_tab, text="Hide Guest user", variable=hide_guest_but, onvalue=1, offvalue=0, activeforeground="#e5a00d", activebackground="#1F1F1F", background="#1F1F1F", foreground="white", selectcolor="grey", takefocus="0", bd="0", command=hide_guest_command).grid(row=7, column=0, padx=10, pady=10)

# display server list
# print(servers_result[0])
# drop down menu
def drop_menu_server_lit():
    #drop_menu_server_lit_label = Label(left_conf_frame, text=clicked.get()).grid(row=8, column=2, padx=10, pady=10)
    selected_server = clicked.get()

    print(selected_server[2:-3])
    print(type(selected_server))
    # connect to MySQL
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        passwd=db_passwd,
        database=db_db,
        auth_plugin='mysql_native_password')
    # Create a cursor and initialize it
    cursor = mydb.cursor()
    # sql_remove_servers = "DELETE FROM plexusers WHERE serverName = %s;" % (selected_server[2:-3])
    sql_remove_servers = "UPDATE plexusers SET is_on_plex = 0, hidden = 1 WHERE serverName = '%s';" % (selected_server[2:-3])
    cursor.execute(sql_remove_servers,)
    # mark as synced to hide old servers
    synced = open('./synced', "w")
    synced.close()
    # Commit changes
    mydb.commit()
    # Close connexion
    mydb.close()
clicked = StringVar()
clicked.set(servers_result[0])
drop_menu = OptionMenu(gui_option_tab, clicked, *servers_result)
drop_menu.grid(row=8, column=0, padx=10, pady=10)
drop_menu_button = Button(gui_option_tab, text="Delete selected server entries", command=drop_menu_server_lit).grid(row=8, column=1, padx=10, pady=10)



# serapation
#sep = ttk.Separator(conf_frame, orient='vertical')
#sep.pack(padx="5", pady="5", fill="y", expand="true")
'''
# conf right panel
right_conf_frame = LabelFrame(conf_frame)
right_conf_frame.config(background="#1F1F1F", border="0")  # color code 1F1F1F
right_conf_frame.pack(side=RIGHT)
'''
email_text_label = Label(communication_tab, text="desciption for email conf")
email_text_label.grid(row=10, column=0)
email_text_label.config(background="#1F1F1F",
                        foreground="white")

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

root.mainloop()
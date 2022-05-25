
import pymysql
import os
import json
import glob
import mysql.connector
import webbrowser
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
#con = pymysql.connect(host = db_host,user = db_user,passwd = db_passwd,db = db_db)
con = mysql.connector.connect(host = db_host,user = db_user,passwd = db_passwd,db = db_db)
cursor = con.cursor()

if con:
    print ("Connected Successfully")
else:
    print ("Connection Not Established")

select_plex_users = """SELECT * FROM plexusers"""
cursor = con.cursor()
cursor.execute(select_plex_users)
result = cursor.fetchall()

p = []

tbl = "<tr><td>ID</td><td>username</td><td>Email</td><td>sections</td><td>serverName</td><td>allowSync</td><td>camera</td><td>channels</td><td>filterMovies</td><td>filterMusic</td><td>filterTelevision</td><td>title</td></tr>"
#"<tr><td><th>ID</th></td><td><th>username</th></td><td><th>Email</th></td><td><th>sections</th></td><td><th>serverName</th></td><td><th>allowSync</th></td><td><th>camera</th></td><td><th>channels</th></td><td><th>filterMovies</th></td><td><th>filterMusic</th></td><td><th>filterTelevision</th></td><td><th>title</th></td></tr>"
p.append(tbl)

for row in result:
    a = "<tr><td>%s</td>"%row[0]
    p.append(a)
    b = "<td>%s</td>"%row[1]
    p.append(b)
    c = "<td>%s</td>"%row[2]
    p.append(c)
    d = "<td>%s</td>"%row[3]
    p.append(d)
    e = "<td>%s</td>"%row[4]
    p.append(e)
    f = "<td>%s</td>"%row[5]
    p.append(f)
    g = "<td>%s</td>"%row[6]
    p.append(g)
    h = "<td>%s</td>"%row[7]
    p.append(h)
    i = "<td>%s</td>"%row[8]
    p.append(i)
    j = "<td>%s</td>"%row[9]
    p.append(j)
    k = "<td>%s</td>"%row[10]
    p.append(k)
    l= "<td>%s</td></tr>"%row[11]
    p.append(l)


contents = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
<meta content="text/html; charset=ISO-8859-1"
http-equiv="content-type">
<title>plex user manager</title>
</head>
<style>
      table,
      th,
      td {
        padding: 10px;
        border: 1px solid black;
        border-collapse: collapse;
      }
    </style>
<body>
<table>
%s
</table>
</body>
</html>
'''%(p)

filename = 'pum_web.html'

def main(contents, filename):
    output = open(filename,"w")
    output.write(contents)
    output.close()

main(contents, filename)    
webbrowser.open(filename)

if(con.is_connected()):
    cursor.close()
    con.close()
    print("MySQL connection is closed.")    


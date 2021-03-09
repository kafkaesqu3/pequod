import sqlite3
import os


sqlite_file = 'ghdb.sqlite'

conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

categories = ["Files Containing Juicy Info", "Pages Containing Login Portals", "Sensitive Directories", "Web Server Detection", "Various Online Devices", "Advisories and Vulnerabilities", "Files Containing Passwords", "Footholds", "Error Messages", "Network or Vulnerability Data", "Vulnerable Servers", "Files Containing Usernames", "Sensitive Online Shopping Info", "Vulnerable Files"]

for category in categories: 
    c.execute("SELECT title FROM ghdb where category = \"{}\"".format(category))
    category_filename = category.replace(" ", "_")
    f = open("ghdb-" + category_filename + ".txt", 'w+')
    rows = c.fetchall()
    for row in rows:
        f.write((str(row)[2:-3]) + '\n')
    print("ghdb-{}.txt: {} entries".format(category_filename, len(rows)))

conn.close()

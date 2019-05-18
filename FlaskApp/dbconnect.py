import MySQLdb

def connection():
    conn = MySQLdb.connect(host="localhost",
                           user="root",
                           passwd="njalsson",
                           db="pastebin")

    c = conn.cursor()
    return c, conn

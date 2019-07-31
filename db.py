import pymysql
def connection():
    con = pymysql.connect(host="localhost", user="root", password="password", db="tsk", port=3306)
    cur = con.cursor()
    return cur, con

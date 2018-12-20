import pymysql as mysql
from . import site_settings as site

from contextlib import closing

def escapeString(s):
    return mysql.escape_string(s)

def doQuery(query):
        
    conn = mysql.connect(host = site.host,
                            user = site.user,
                            passwd = site.password,
                            db = site.database)
    with closing(conn.cursor()) as cursor:
        nRows = cursor.execute(query)
        result = cursor.fetchall()
        conn.commit()
    conn.close()
    
    return (nRows, result)

nRows, result = doQuery('SELECT * FROM `werewolf` LIMIT 1')

print('werewolf db test returned %s rows.' % nRows)

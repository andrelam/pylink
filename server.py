from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import urllib
import config as cfg
import sqlite3
from sqlite3 import Error
import contextlib


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def init_db():
    database = cfg.pylink_db
    sql_create_links = """ CREATE TABLE IF NOT EXISTS links (
                                 id integer PRIMARY KEY,
                                 link text NOT NULL,
                                 description text
                           ); """

    conn = create_connection(database)
    if conn is not None:
        create_table(conn, sql_create_links)
        return conn
    else:
        print("Error! Cannot initialize database")
        return None

db = init_db()


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        fi = open(cfg.pylink_file, 'rb')
        response = BytesIO(fi.read())
        fi.close()
        self.wfile.write(response.getvalue())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        response = BytesIO()
        response.write(b'Received: ')
        response.write(body)
        response.write(b'\n')
        self.wfile.write(response.getvalue())
        fo = open(cfg.pylink_file, "ab")
        fo.write(urllib.parse.unquote(body[4:].decode()).encode())
        fo.write(b'\n')
        fo.close()
        db.execute("INSERT INTO links (link) VALUES (?)",
                (str(urllib.parse.unquote(body[4:].decode())),))
        db.commit()

httpd = HTTPServer(('', cfg.pylink_port), SimpleHTTPRequestHandler)

with contextlib.closing(db):
    httpd.serve_forever()

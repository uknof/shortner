#!/usr/bin/env python

import sqlite3
from passlib.hash import pbkdf2_sha256

DATABASE = "urls.db"


def get_db():
    db = sqlite3.connect(DATABASE)

    def make_dicts(cursor, row):
        return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))
    db.row_factory = make_dicts
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


class User():

    def __init__(self, username):
        username = username.lower().strip()
        userdb = query_db("select * from users where username = ?", [username])
        if len(userdb) == 0:
	       raise Exception("No user '%s' found" % (username))
        self.username = userdb[0]["username"]

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def get(username):
        return User(username)

    @staticmethod
    def get_all():
        users = []
        for userrow in query_db("select username from users order by username"):
            username = userrow["username"]
            user = User(username)
            users.append(user)
        return users

    @staticmethod
    def exists(username):
        username = username.lower().strip()
        userdb = query_db("select * from users where username = ?", [username])
        if len(userdb) == 0:
	    return False
        else:
            return True

    @staticmethod
    def authenticate(username, password):
        username = username.lower().strip()
        if len(username) == 0 or len(password) == 0:
            return None
        userdb = query_db("select * from users where username = ?", [username])
        if len(userdb) == 1:       
            # user exists, check the hash
            hash = userdb[0]["password"]
            if pbkdf2_sha256.verify(password, hash):
                return User(username)
        return None

    @staticmethod
    def create(username, password):
        username = username.lower().strip()
        if User.exists(username) is True:
            raise Exception("user '%s' already exists" % (username))
        hash = pbkdf2_sha256.encrypt(password, rounds=200000, salt_size=16)
        db = get_db()
        db.execute('insert into users (username,password) values (?,?)', [username, hash])
        db.commit()        
        if User.exists(username) is False:
	       raise Exception("created user '%s' does not exist" % (username))
        u = User(username)
        if u is None:
           raise Exception("created user '%s' is None" % (username))
        return u

    @staticmethod
    def delete(username):
        username = username.lower().strip()
        if User.exists(username) is False:
            raise Exception("user '%s' does not exist" % (username))
        db = get_db()
        db.execute('delete from users where username = ?', [username])
        db.commit()
        return None


class Totals():

    def __init__(self):
        return

    def get_all(self):
        return {}


class Url():

    def __init__(self, short):
        rows = query_db('select *,(select sum(hits4) from hits where hits.short=urls.short) as hits4,(select sum(hits6) from hits where hits.short=urls.short) as hits6 from urls where short = ?', [short])
        row = rows[0]
        self.custom = row["custom"]
        self.dest = row["dest"]
        self.createdby = row["createdby"]
        self.createdon = row["createdon"]
        self.short = row["short"]
        self.hits4 = row["hits4"]
        self.hits6 = row["hits6"]

    def hits(self):
        h = []
        h = query_db("select * from hits where short=? order by hitdate desc", [self.short])
        return []

    @staticmethod
    def total():
        urls = query_db('select count(*) as urls from urls')[0]["urls"]
        return urls

    @staticmethod
    def match(matchurl):
        short = matchurl.lower()
        match = query_db("select short from urls where (short=? or custom=?)", [short, short])
        if len(match) == 0:
            return None
        return Url(match[0]["short"])

    @staticmethod
    def get_all():
        urls = []
        urlrows = query_db('select short from urls')
        for row in urlrows:
            url = Url(row["short"])
            urls.append(url)
        return urls

    @staticmethod
    def unique_short():
        matches = 1
        while matches == 1:
            short = ''.join(random.choice(['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']) for i in range(5))
            matches = query_db("select * from urls where short=?", [short])
        return short

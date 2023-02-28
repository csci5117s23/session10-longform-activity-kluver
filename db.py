""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""

from contextlib import contextmanager
import logging
import os

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      # cursor = connection.cursor()
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def reset_logins():
    with get_db_cursor(True) as cur:
        cur.execute("delete from s10_logins")

def has_logged_in_before(userId):
    with get_db_cursor(True) as cur:
        cur.execute("select id from s10_logins where id = %s", (userId,))
        if cur.fetchone() is None:
            # not found.
            cur.execute("insert into s10_logins (id) values (%s)", (userId,))
            return False
        else:
            return True


def get_pens(page, per_page=15):
    """
    page is 0 indexed.
    """
    with get_db_cursor(False) as cur:
        cur.execute("select id, name, image from pens limit %s offset %s", (per_page, per_page*page))
        return cur.fetchall()

def get_pen(pen_id):
    with get_db_cursor(False) as cur:
        cur.execute("select * from pens where id = %s", (pen_id,))
        return cur.fetchone()

def get_likes(pen_id):
    ### NOTE -- this really should be a join that's properly integrated into the two above functions
    ### But I didn't want to break out the complex SQL for an example like this.
    #### Just note this is inefficient.
    with get_db_cursor(False) as cur:
        cur.execute("select count(*) from pen_likes where pen_id = %s", (pen_id,))
        counts = cur.fetchone()
        return counts[0]

def get_does_like(pen_id, user_id):
    with get_db_cursor(False) as cur:
        ### Again -- this should really be done with the above in one request. terrible form that it isn't.
        cur.execute("select count(*) from pen_likes where pen_id = %s and user_id=%s", (pen_id,user_id))
        counts = cur.fetchone()
        return counts[0]!=0

def like_pen(pen_id, user_id):
    with get_db_cursor(True) as cur:
        cur.execute("""insert into pen_likes (user_id, pen_id) values (%s, %s) 
                       on conflict do nothing""" , (user_id, pen_id,))


def unlike_pen(pen_id, user_id):
    with get_db_cursor(True) as cur:
        cur.execute("""delete from pen_likes where user_id = %s and pen_id=%s""" , (user_id, pen_id,))




def search_pens_like(term, page, per_page=15):
    """
    page is 0 indexed.
    """
    with get_db_cursor(False) as cur:
        term = "%"+term+"%"
        term.replace(" ", "%")
        # % is the wildcard for like.
        cur.execute("select id, name, image from pens where text like %s limit %s offset %s", (term, per_page, per_page*page))
        return cur.fetchall()



def search_pens(term, page, per_page=15):
    """
    page is 0 indexed.
    """
    with get_db_cursor(False) as cur:
        # The where uses the full text search algorithm to match 
        # the order likewise uses full text search to match
        cur.execute("""select id, name, image 
                       from pens 
                       where to_tsvector('english', text) @@ plainto_tsquery('english', %s) 
                       order by ts_rank(to_tsvector('english', text), plainto_tsquery('english', %s)) desc 
                       limit %s offset %s""", 
                       (term, term, per_page, per_page*page))
        return cur.fetchall()

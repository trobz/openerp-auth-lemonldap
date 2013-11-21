#!/usr/bin/env python

import re
import argparse
import xmlrpclib
import MySQLdb
import MySQLdb.cursors



def check_user(new_user, users):
    for user in users:
        if user['username'] == new_user['username']:
            if user['oe_database'] != new_user['oe_database']:
                print """Warning: user %s already exist with \
                         a different database (%s), it will \
                         be updated !""" % ( new_user['username'], new_user['oe_database']) 
            return True
    return False
 

class AttributeHolder:
    """
    Attribute holder
    """
    def __init__(self, **entries): 
        self.__dict__.update(entries)
        
    def has(self, name):
        return name in self.__dict__;



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import user from an OpenERP instance into LemonLDAP database")

    parser.add_argument('host', help='OpenERP XML-RPC Host')
    parser.add_argument('port', help='OpenERP XML-RPC Port')
    parser.add_argument('database', help='OpenERP database')
    parser.add_argument('user', help='OpenERP XML-RPC username')
    parser.add_argument('password', help='OpenERP XML-RPC password')
    
    parser.add_argument('--mysql-db', default="lemon_user_auth", help='MySQL database name')
    parser.add_argument('--mysql-user', default="lemonldap", help='MySQL username')
    parser.add_argument('--mysql-password', default="We_1deQnBc", help='MySQL password')
    
    options = AttributeHolder(**vars(parser.parse_args()))
    
    
    # get all existing user in db
    db = MySQLdb.connect(host="localhost", port=3306, user=options.mysql_user, passwd=options.mysql_password, db=options.mysql_db, cursorclass=MySQLdb.cursors.DictCursor)
    cur = db.cursor()
    cur.execute("SELECT id, oe_id, username, oe_database FROM lemon_user")
    mysql_users = cur.fetchall()    
    cur.close()

    # get xml-rpc user uid
    sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/common' % (options.host, options.port))
    uid = sock.login(options.database, options.user, options.password)
    
    sock = xmlrpclib.ServerProxy('http://%s:%s/xmlrpc/object' % (options.host, options.port))
    
    # get user ids
    ids = sock.execute(options.database, uid, options.password, 'res.users', 'search', [])
    users = sock.execute(options.database, uid, options.password, 'res.users', 'read', ids, ['id', 'login', 'password'])
    
    insert = []
    insert_pwd = []
    update = []
    update_pwd = []

    for user in users:
        user = AttributeHolder(**user)
        partners = sock.execute(options.database, uid, options.password, 'res.partner', 'read', user.partner_id, ['email'])
        
        attr = {
            'oe_id': user.id,
            'oe_database': options.database,
            'username': user.login,
            'email': partners['email'] or "",
            'password': user.password,
            'created_at': 'null',
            'updated_at': 'null'            
        }
        
        if not check_user(attr, mysql_users):
            print "insert user %s" % attr['username']
            insert.append("({oe_id}, '{oe_database}', '{username}', '{email}', {created_at}, {updated_at})".format(**attr))
            insert_pwd.append("('{username}', sha1('{password}'), {created_at}, {updated_at})".format(**attr))
        else:
            print "update user %s" % attr['username']
            update.append([attr['oe_id'], attr['oe_database'], attr['email'], attr['username']])
            update_pwd.append([attr['password'], attr['username']])

    insert_query = """
    INSERT INTO lemon_user (oe_id, oe_database, username, email, created_at, updated_at) 
        VALUES """ + (",".join(insert)) + ';' if len(insert) > 0 else None
    insert_pwd_query = """
    INSERT INTO lemon_auth (username, password, created_at, updated_at) 
        VALUES """ + (",".join(insert_pwd)) + ';' if len(insert_pwd) > 0 else None
    
    update_query = """  
        UPDATE lemon_user
            SET oe_id=%s, 
                oe_database=%s, 
                email=%s, 
                updated_at=null
            WHERE username=%s                    
    """
    update_pwd_query = """  
        UPDATE lemon_auth
            SET password=sha1(%s),
                updated_at=null 
            WHERE username=%s                   
    """

    cur = db.cursor()
    if insert_query and insert_pwd_query:
        cur.execute(insert_query)
        cur.execute(insert_pwd_query)
        print "SQL> %s user(s) inserted" % len(insert)

    if len(update) > 0 and len(update_pwd):
        cur.executemany(update_query, update)        
        cur.executemany(update_pwd_query, update_pwd)        
        print "SQL> %s user(s) updated" % len(update)
    
    cur.close()

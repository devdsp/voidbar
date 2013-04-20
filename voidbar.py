#!/usr/bin/env python

import serial
import sys
import select
import sqlite3

db = sqlite3.connect('data.sqlite')
db.row_factory = sqlite3.Row

def get_user(identifier):
    cur = db.cursor()
    user = cur.execute(
        "select * from users join accounts on users.account_id = accounts.id where users.identifier=?",(identifier,)
    ).fetchone()
    cur.close()
    return user

def get_item(identifier):
    cur = db.cursor()
    item = cur.execute(
        "select * from items where identifier=?",(identifier,)
    ).fetchone()
    cur.close()
    return item

def readline(prompt = "> "):
    ser = serial.Serial('/dev/ttyS0','9600',timeout=1)
    sys.stdout.write( "\n" + prompt )
    sys.stdout.flush()
    
    line = ""
    while True:
        inputs = [sys.stdin,ser]
        (readable,writeable,exceptionable) = select.select(inputs,[],inputs);
        for r in readable:
            if sys.stdin in readable:
                return sys.stdin.readline().strip()
            elif ser in readable:
                char = ser.read(1)
                if char == "\r":
                    ser.close()
                    print
                    return line
                line += char;
                sys.stdout.write(char)
                sys.stdout.flush()

def idle():
    while True:
        line = readline("VoidBar> ")
        if line == 'exit':
            return
             
        user = get_user( line )
        item = get_item( line )

        if user:
            do_user( user )
        elif item:
            do_item( item )
        else:
            do_new( line )

def do_user(user):
    print "Hi %s, your balance is $%.02f" % (
        user['description'],user['balance']
    )

    while True:
        line = readline(prompt = "VoidBar/" + user['description'] + "> ")
        if line == 'exit' or line == '':
            break

        item = get_item(line)

        if item:
            do_user_item( user, item )

def do_item(item):
    print "%s is %s, it %s $%0.02f" % (
        item['identifier'], 
        item['description'],
        "costs" if item['value'] < 0 else "credits",
        item['value'] if item['value'] > 0 else -item['value']
    ) 

def do_user_item(user,item):
    do_item(item);
    cur = db.cursor();
    cur.execute(
        'UPDATE accounts SET balance = balance + ? WHERE id = ?',
        (item['value'],user['id'])
    )
    db.commit()
    cur.close()
    user = get_user( user['identifier'] )
    print "Your new balance is: $%.02f" % (user['balance']) 

def do_new(barcode):
    print "I don't recognise that input..."
    print "Do you want to add a new [item], [user] or account [identifier]?"
    while True:
        line = readline( prompt = "VoidBar/new> ")
        if line == 'exit' or line == '':
            break
        if line == 'item':
            return do_new_item(barcode)
        if line == 'user':
            return do_new_user(barcode)
        if line == 'identifier':
            return do_new_identifier(barcode)


def do_new_item(barcode):
    print "Adding %s as a new item.";
    print "What is this item?"
    description = readline(prompt = "VoidBar/new/item: Description > ")
    if not description:
        print "You didn't give a description"
        return;
    print "What affect does this have on the user's balance?"
    print "NOTE: if it costs money to buy this item then the number must be negative"
    value = float(readline(prompt = "VoidBar/new/item: value > "))
    if not value:
        print "You didn't give a value"
        return;
    
    cur = db.cursor()
    cur.execute( "insert into items (identifier,value,description) values (?,?,?)", ( barcode, value, description ) )
    db.commit()
    cur.close()


def do_new_user(barcode):
    print "Adding %s as a new user account.";
    print "Who is this user?"
    description = readline(prompt = "VoidBar/new/user: Description > ")
    if not description:
        print "You didn't give a description"
        return;
    
    cur = db.cursor()
    cur.execute( "insert into accounts (description, balance) values (?,?)", ( description,0 ) )
    cur.execute( "insert into users (account_id, identifier) values (?,?)", (cur.lastrowid,barcode ) )
    db.commit()
    cur.close()

def do_new_identifier(barcode):
    print "Adding %s as a new identifier.";
    print "Use an existing identifer to bind the new identifier"
    user = get_user(readline(prompt = "VoidBar/new/identifer: existing > "))
    if not user:
        print "couldn't get the user from that token"
        return;
    
    cur = db.cursor()
    cur.execute( "insert into users (account_id, identifier) values (?,?)", (user['account_id'],barcode ) )
    db.commit()
    cur.close()


print "VoidBar POS system writen by Adam, inspired by Brmbar"

idle();


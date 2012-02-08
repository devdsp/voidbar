#!/usr/bin/env python

import serial
import sys
import select
import sqlite3

db = sqlite3.connect('data.db')
db.row_factory = sqlite3.Row

def get_user(identifier):
    cur = db.cursor()
    user = cur.execute(
        "select * from users where identifier=?",(identifier,)
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
        user['identifier'],user['balance']
    )

    line = readline(prompt = "VoidBar/" + user['identifier'] + "> ")
    if line == 'exit':
        return
    
    item = get_item(line)

    if item:
        do_user_item( user, item )

def do_item(item):
    print "%s is %s, it %s $%0.02f" % (
        item['identifier'], 
        item['name'], 
        "costs" if item['value'] < 0 else "credits",
        item['value'] if item['value'] > 0 else -item['value']
    ) 

def do_user_item(user,item):
    do_item(item);
    cur = db.cursor();
    cur.execute(
        'UPDATE users SET balance = balance + ? WHERE identifier = ?',
        (item['value'],user['identifier'])
    )
    db.commit()
    cur.close()
    user = get_user( user['identifier'] )
    print "Your new balance is: $%.02f" % (user['balance']) 

def do_new(barcode):
    print "I don't recognise that barcode..."
    print "and Adam hasn't finished programming me. So you can't teach me yet."

print "VoidBar POS system writen by Adam, inspired by Brmbar"

idle();


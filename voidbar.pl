#!/usr/bin/env python

import serial
import sys
import select

people = {
    '#059': {'name': 'devdsp', 'balance': 0 }
}

things = {
    'F4029764001807': { 
        'name': 'Club-Mate',
        'value': -3.40 
    },
    'F9313139217043': {
        'name': 'an eraser',
        'value' : 5
    }
}

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
	    if line in people.keys():
	    	do_user( line )
	    elif line in things.keys():
		    do_item( line )
	    else:
    		do_new( line )

def do_user(barcode):
    user = people[barcode]
    line = readline(prompt = "VoidBar/" + user['name'] + "> ")
    if line == 'exit':
        return
    elif line in things.keys():
        do_user_item( barcode, line )

def do_item(barcode):
    item = things[barcode]
    print "%s is %s, it %s $%0.02f" % (
        barcode, 
        item['name'], 
        "costs" if item['value'] < 0 else "credits",
        item['value'] if item['value'] > 0 else -item['value']
    ) 

def do_user_item(user_code,item_code):
    do_item(item_code);
    user = people[user_code]
    item = things[item_code]
    user['balance'] += item['value']
    print "Your new balance is: $%.02f" % (user['balance']) 

def do_new(barcode):
    print "I don't recognise that barcode..."
    print "and Adam hasn't finished programming me. So you can't teach me yet."

print "VoidBar POS system writen by Adam, inspired by Brmbar"

idle();


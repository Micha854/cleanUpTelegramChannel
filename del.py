#!/usr/bin/env python3
__author__ = "Micha854"
__copyright__ = "Copyright 2020, Micha854"
__version__ = "0.10.1"
__status__ = "Prod"

# generic/built-in and other libs
import telepot
import sys
import ast
import os
import json

from pprint import pprint
from configparser import ConfigParser

# function to add to JSON 
def write_json(feeds, filename='response.json'): 
    with open(filename, mode='w', encoding='utf8') as data: 
        json.dump(feeds, data, ensure_ascii=False, indent=4) 

### DUBUG MODE
debug = False

### no config specified
if len(sys.argv) <= 1:
    print("Es wurde keine Config geladen...")

### no start message_id specified
elif len(sys.argv) <= 2:
    print("Gib an, ab welcher Message ID gelöscht werden soll...")

### RUN SCRIPT
else:
    ### read config file
    config = ConfigParser()
    config.read(sys.argv[1], encoding='utf-8')

    token     = config["settings"]["token"]
    chatid    = config["settings"]["chatid"]
    save_ids  = ast.literal_eval(config["settings"]["save_ids"])
    save_user = config["settings"]["save_user"]

    start = int(sys.argv[2])
    bot = telepot.Bot(token)

    ### create update.txt file
    if os.path.isfile('update.txt'):
        datei = open('update.txt','r')
        check_offset = datei.read()
        offset = check_offset if int(check_offset) else 100000001
    ### set default update_id
    else:
        offset = 100000001
    
    ### load response from getUpdates
    response = bot.getUpdates(offset=offset, allowed_updates=['channel_post', 'message'])
    last_update = 0
    
    ### debug
    if debug == True:
        pprint(response)
        print("\n\n")
    
    ### create response.json file
    if not os.path.isfile("response.json"):
        feeds = response
        write_json(feeds)

    ### load response.json
    else:    
        with open("response.json") as feedsjson:
            feeds = json.load(feedsjson)

        ### load getUpdates date to response.json file
        for message in response:
            if message['update_id'] not in feeds:
                feeds.append(message)

    ### set result variables
    deleted = 0
    non_del = 0
    filter  = 0

    ### go through all messages
    for message in feeds:
        if 'channel_post' in message:
            messageID  = message['channel_post']['message_id']
            messageUSR = message['channel_post']['author_signature']
        elif 'message' in message:
            messageID  = message['message']['message_id']
            messageUSR = message['message']['from']['username']
            
        ### check whether the message is deleted
        if messageID > start and messageID not in (save_ids) and messageUSR not in (save_user):
            try:
                bot.deleteMessage((chatid, messageID))
                print("Nachricht " + str(messageID) + " wurde gelöscht!")
                feeds.remove(message)
                deleted +=1
            except:
                print("Konnte Nachricht " + str(messageID) + " nicht löschen!!!")
                non_del +=1
        ### message is not deleted
        else:
            if messageUSR in (save_user):
                print("=====> Nachrichten von: " + str(save_user) + " werden nicht gelöscht!!!")
            elif messageID in (save_ids):
                print("=====> Nachricht: " + str(messageID) + " wird nicht gelöscht!!!")
            elif start > messageID:
                print("=====> Nachrichten kleiner ID: " + str(start) + " werden nicht gelöscht!!!")
            
            filter +=1
        
        ### get last update_id
        last_update = message['update_id']

    ### save next update_id
    if int(last_update):
        f = open('update.txt', 'w')
        f.write(str(last_update+1))
        f.close()

    ### save response.json
    write_json(feeds)

    ### result output
    print("\n " + str(deleted) + " Nachrichten wurden gelöscht")
    print(" " + str(non_del) + " Nachrichten konnten nicht gelöscht werden")
    print(" " + str(filter) + " Nachrichten wurden aufgrund des Filters nicht gelöscht\n")
    
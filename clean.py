#!/usr/bin/env python3
__author__ = "Micha854"
__copyright__ = "Copyright 2020, Micha854"
__version__ = "0.10.4"
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

    token     = config.get("settings", "token")
    chatid    = config.get("settings", "chatid")
    save_ids  = ast.literal_eval(config.get("settings", "save_ids"))
    save_user = config.get("settings", "save_user")
    debug     = config.getboolean("settings", "debug")

    start = int(sys.argv[2])
    bot = telepot.Bot(token)

    ### readout next update_id
    if os.path.isfile('update.txt'):
        datei = open('update.txt','r')
        check_offset = datei.read()
        offset = check_offset
    ### set default update_id
    else:
        offset = 100000001

    ### readout response.json
    if os.path.isfile("response.json"):
        with open("response.json") as feedsjson:
            feeds = json.load(feedsjson)
    else:
        feeds = []

    ### fetch all updates and save to json
    channels = []
    last_update = 0
    fetch = 0
    while True:

        ### load response from getUpdates
        response = bot.getUpdates(offset=offset, allowed_updates=['channel_post', 'message'])

        ### load getUpdates data to response.json file
        for message in response:
            try:
                if 'channel_post' in message:
                    title = message['channel_post']['chat']['title']
                elif 'message' in message:
                    title = message['message']['chat']['title']
            except:
                title = None

            if message['update_id'] not in feeds:
                feeds.append(message)
                last_update = message['update_id']
                fetch += 1

            if title not in channels:
                channels.append(title)

        offset = last_update + 1

        if len(response) < 100:
            break

        else:
            print(" ...fetching " + str(fetch) + " messages")


    ### get chatid
    try:
        get_chatid = bot.getChat(chatid)
    except:
        get_chatid = {'id': None, 'title': 'CHAT NOT FOUND', 'type': None}

    ### debug
    if debug == True:
        print("=====> chat info:")
        pprint(get_chatid)
        print("\n=====> getUpdates:")
        pprint(response)
        print("\n\n")

    ### save next update_id
    if int(last_update):
        f = open('update.txt', 'w')
        f.write(str(last_update+1))
        f.close()

    ### set result variables
    deleted = 0
    non_del = 0
    filter  = 0

    ### go through all messages
    for message in feeds[:]:
        try:
            if 'channel_post' in message:
                messageID  = message['channel_post']['message_id']
                messageUSR = message['channel_post']['author_signature']
                messageCHAT= message['channel_post']['chat']['id']
            elif 'message' in message:
                messageID  = message['message']['message_id']
                messageUSR = message['message']['from']['username']
                messageCHAT= message['message']['chat']['id']
        except:
            messageID  = None
            messageUSR = None
            messageCHAT= None

        ### it is the chat_id from the config
        if messageCHAT == get_chatid['id']:
            ### check whether the message is deleted
            if messageID > start and messageID not in (save_ids) and messageUSR not in (save_user):
                try:
                    bot.deleteMessage((chatid, messageID))
                    print("Nachricht " + str(messageID) + " wurde gelöscht!")
                    deleted +=1
                except:
                    print("Konnte Nachricht " + str(messageID) + " nicht löschen!!!")
                    non_del +=1
                feeds.remove(message)
            ### message is not deleted
            else:
                if messageUSR in (save_user):
                    print("=====> Nachrichten von: " + str(save_user) + " werden nicht gelöscht!!!")
                elif messageID in (save_ids):
                    print("=====> Nachricht: " + str(messageID) + " wird nicht gelöscht!!!")
                elif start > messageID:
                    print("=====> Nachrichten kleiner ID: " + str(start) + " werden nicht gelöscht!!!")

                filter +=1

    ### save response.json
    write_json(feeds)

    ### result output
    print("\n Fetching " + str(fetch) + " Messages from " + str(channels))
    print("\n gelöscht von ==> " + str(get_chatid['type']) + " ==> " + str(get_chatid['title']) + ":\n")
    print(" " + str(deleted) + " Nachrichten wurden gelöscht")
    print(" " + str(non_del) + " Nachrichten konnten nicht gelöscht werden")
    print(" " + str(filter) + " Nachrichten wurden aufgrund des Filters nicht gelöscht\n")
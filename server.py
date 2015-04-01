import random
import json
from datetime import datetime
import httplib, urllib
import logging as logger

# External dependencies
import Queue
from flask import Flask, request
import sqlite3
from nexmomessage import NexmoMessage # pip install -e git+https://github.com/marcuz/libpynexmo.git#egg=nexmomessage

from config import WIT_ACCESS_TOKEN, NEXMO_API_KEY, NEXMO_API_SECRET, NEXMO_PHONE_NO, LOGGER_SERVER, SQLITE_DATABASE, DEBUG_SMS, BLACKLIST
from getaroom import get_available_rooms

app = Flask(__name__)
ban_lookup = json.loads(open(BLACKLIST).read())

logger.basicConfig(filename=LOGGER_SERVER,level=logger.DEBUG)
@app.route('/getaroom', methods=['GET', 'POST'])
def getaroom():
    sender_no = request.values.get('msisdn')
    body = request.values.get('text')

    if is_banned(sender_no):
        logger.warn("Number banned! - %s - %s", (body, sender_no))
        return "Number banned"

    if sender_no is None or body is None:
        return 'Invalid message.'

    logger.info("Received request - %s - %s" % (body, sender_no))

    # TODO: account for concatenated & unicode messages
    wit_response = send_to_wit(body)
    sms_response = parse_response(json.loads(wit_response))
    if DEBUG_SMS:
        print("SMS DEBUG: %s - from - %s" % (sms_response, sender_no))
    else:
        send_sms(sender_no, sms_response)
    print wit_response

    return sms_response

def send_to_wit(message):
    conn = httplib.HTTPSConnection('api.wit.ai')
    headers = {'Authorization': 'Bearer %s' % (WIT_ACCESS_TOKEN,)}
    params = urllib.urlencode({'v': '20141022', 'q': message})
    url = '/message?%s' % (params,)
    conn.request('GET', url, '', headers)
    response = conn.getresponse()
    return response.read()

def parse_response(response):
    intent =  response['outcomes'][0]['intent']
    if intent == 'getaroom':
        return parse_getaroom(response)
    elif intent == 'help':
        return 'This service finds you a vacant room on Virginia Tech\'s campus.\nTry: "get a room in TORG"'
    elif intent == 'stop':
        return parse_joke(response)
    else:
        return 'Invalid message. Try "get a room in TORG"'

def parse_getaroom(response):
    if 'outcomes' in response and len(response['outcomes']) > 0:
        outcome = response['outcomes'][0]
        if 'entities' in outcome and len(outcome['entities']) > 0:
            entity = outcome['entities']
            if 'building' in entity and len(entity['building']) > 0:
                building = entity['building'][0]['value']

                rooms = get_available_rooms(building, datetime.now())
                if len(rooms) == 0:
                    return "Sorry, there aren't any rooms available in that building right now."
                else:
                    building_name = rooms[0].building_name
                    string = ''
                    if len(rooms) == 1:
                        string += 'Hey! I found one room in %s:\n\n' % (building_name,)
                    elif len(rooms) <= 3:
                        string += 'Hey! I found %d rooms in %s:\n\n' % (len(rooms), building_name)
                    else:
                        string += 'Hey! Here are the three available rooms in %s:\n\n' % (building_name,)

                iterations = min((3, len(rooms)))
                for i, room in enumerate(rooms[:iterations]):
                    if not room.end_availability:
                        string += '- %s %s (open rest of day)' % (room.building_code, room.number)
                    else:
                        string += '- %s %s (open until %s)' % (room.building_code, room.number, room.end_availability)
                    if i is not iterations - 1:
                        string += '\n'

                return string

    return "Invalid message. Try 'get a room in TORG'"

def is_banned(number):
    bans = ban_lookup['bans']
    if number in bans:
        return True
    return False

def parse_joke(response):
    string = 'Congratulations! You have been signed up for Emperor Penguin Facts.\n\n'
    num = random.randint(0, 4)
    if num is 0:
        string += 'Did you know emperor penguins stand up to 4ft tall?'
    elif num is 1:
        string += 'Male emperor penguins are the primary caregivers for newborn offspring.'
    elif num is 2:
        string += 'Emperor penguins are featured on more than 30 countries stamps.'
    elif num is 3:
        string += 'Emperor penguins fast longer than any other bird, going 115 days without eating during chick incubation!'
    elif num is 4:
        string += 'Penguins. Penguins. Pengiuns. Pegnuins. PENGUISN. PENGEUNINS. PENGSUINSG OEPJG SODFKSDFO FSDFDSFSS'

    return string


def check_rate_limited(number):
    con = sqlite3.connect(SQLITE_DATABASE)
    with con:
        cur = con.cursor()
        cmd = 'SELECT * FROM users WHERE phone_no = ?'
        cur.execute(cmd, (number,))

def send_sms(number, message):
    msg = {
        'reqtype'   : 'json',
        'api_key'   : NEXMO_API_KEY,
        'api_secret': NEXMO_API_SECRET,
        'from'      : NEXMO_PHONE_NO,
        'to'        : number,
        'text'      : message
    }
    sms = NexmoMessage(msg)
    sms.set_text_info(msg['text'])
    response = sms.send_request()
    if not response:
        logger.error("[NEXMO] Failed to send response: %s [to] %s" % (message, number))
        print "Failed to send response"

if __name__ == "__main__":
    app.run(host='0.0.0.0')

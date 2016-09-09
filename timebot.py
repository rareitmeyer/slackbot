# A simple slack chatbot to tell timezone-aware time, writen
# in python3.
#
# Copyright 2016 R. A. Reitmeyer
#
# Released under the MIT license, in hope it might help
# someone else get started with a bot.

# standard libraries
import datetime
import logging
import os
import pprint
import re
import sys
import time

# libraries that must be installed from pypi.python.org via pip.
import pytz
import slackclient


# The bot will need to recognize messages sent to it, which starts
# with knowning what its own name is. By default, assume the bot name
# matches the python filename (so timebot.py is on slack as timebot),
# but if you rename the bot when adding it to slack, adjust this
# line...
BOTNAME = os.path.basename(re.sub('[.]pyc?$', '', __file__))


def read_timezone():
    """Grab the local machine timezone from /etc/timezone on linux,
    or a local 'timezone' file if not-linux. The timezone file
    must contain a timezone name, like Canada/Newfoundland or
    Europe/Berlin.
    """
    if sys.platform == 'linux':
        with open('/etc/timezone', 'r') as fp:
            return pytz.timezone(fp.read().strip())
    else:
        with open('timezone', 'r') as fp:
            return pytz.timezone(fp.read().strip())


# Define some handy time zones. For example purposes, I'll
# assume UTC, California and India are important timezones
# that are worth some special aliases and optimizations.
UTC = pytz.timezone('UTC')
PACIFIC = pytz.timezone('America/Los_Angeles')
INDIA = pytz.timezone('Asia/Kolkata')
LOCAL = read_timezone()

KNOWN_TIMEZONES = {t.lower():t for t in pytz.common_timezones}

# Build and save the message to parse
MESSAGE_PAT = re.compile('what time is it in (?P<place>[A-Za-z/_]+)[?]$', flags=re.IGNORECASE)
def process_message(client, message):
    """Processes a 'what time is it in <place>?' message,
    assuming place is a timezone name or a shorthand like
    India or California.
    """
    # should log incoming message, including conversation id.
    m = MESSAGE_PAT.search(message['text'])
    if not m:
        client.api_call('chat.postMessage', channel=message['channel'], text='I did not understand. I can answer questions of the form "what time is it in <place>?"', as_user=True)
        # failure case... log failure
        return
    place = m.group('place').lower()

    now = datetime.datetime.fromtimestamp(time.time(), UTC)
    # Handle some special aliases like india or california,
    # then handle all the common timezones in the tz database.
    if place in ['utc']:
        pass
    elif place in ['india', 'asia/kolkata']:
        now = now.astimezone(INDIA)
    elif place in ['pacific','us/pacific','america/los_angles','california']:
        now = now.astimezone(PACIFIC)
    elif place in KNOWN_TIMEZONES:
        tz = pytz.timezone(KNOWN_TIMEZONES[place])
        now = now.astimezone(tz)
    else:
        client.api_call('chat.postMessage', channel=message['channel'], text='I do not recognize {place} as a timezone, but I understand india, us/pacific and utc. Try one of those!'.format(place=place))
        # failure case... log failure
        return

    # success case:
    client.api_call('chat.postMessage', channel=message['channel'], text='It is now {now} in {place}'.format(now=now.strftime('%Y-%m-%dT%H:%M:%S'), place=place))
    return


# A slack bot is created in slack team, and creation of the bot
# creates a special API key the bot must use to authenticate.
# That API key must be kept private, and so (in this bot) is
# read from a .<botname>_token file in the same directory as the
# python source.
def read_token():
    token_file = os.path.join(os.path.dirname(__file__),'.'+BOTNAME+'_token')
    if not os.path.exists(token_file):
        logging.fatal("Must have a slack token for this bot in a file named {token_file}".format(token_file=token_file))
        sys.exit(1)
    with open(token_file, 'r') as fp:
        return fp.read().strip()



def main():
    # Connect to slack and run the basic test
    client = slackclient.SlackClient(read_token())
    test_data = client.api_call("api.test")
    print(test_data)
    # Every api call returns a dict with an 'ok' field
    # that will be True if the call worked.
    assert(test_data['ok'])

    # Get the list of channels and dump it out, just FYI.
    channels = client.api_call("channels.list")
    assert(channels['ok'])
    channels = {c['id']:c for c in channels['channels']}
    pprint.pprint(channels)

    # Make a dict of users by user name
    users = client.api_call('users.list')
    assert(users['ok'])
    users = {u['name']:u for u in users['members']}

    # Build a recognition regex to look for messages
    # that explicitly mention this bot.
    bot_id = users[BOTNAME]['id']
    to_bot = re.compile('<@{bot_id}>'.format(bot_id=bot_id))
    
    
    # Connect to the slack team via RTM.
    if client.rtm_connect():
        while True:
            data = client.rtm_read()
            # filter down to just messages with text, to ignore
            # typing or message updates among other things
            messages = [d for d in data if d.get('type') == 'message' and 'text' in d]
            if messages:
                # work with all messages, if interested in all...
                print(messages)
                # ... or loop over individual messages to find ones
                # mentioning the bot, and process just those.
                for m in messages:
                    if to_bot.search(m['text']):
                        process_message(client, m)
            # wait a little before checking again.
            time.sleep(1)
    else:
        logging.fatal("connection failed.")
        sys.exit(1)


if __name__ == '__main__':
    main()

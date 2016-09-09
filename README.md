# Simple slack chatbot to tell timezone-aware time in Python 3.

This is an example that may inspire someone else to start playing
with Slack chatbots in Python 3. It is released under the MIT
license.


## Creating a bot

### On slack

* Go to your slack team, or create one.

* Open a channel, and click + add an app or custom integration

* Click build (top right) to build a new app

* Click get started with a custom integration

* Pick bots

* Name your bot (timebot) and step through the setup.

* Save your bot's API token!

* Back in your slack team, invite the newly-created bot user to 
   each channel you'd like the bot to listen to: /invite @timebot


### On your computer

* Save the bot's API token into a file next to timebot.py, named
   .timebot_token.

* If you're on Windows or MacOS, create a file with your offical
   timezone name (like 'Europe/Berlin' or 'America/Newfoundland')
   named 'timezone'. On Linux, you can skip this step because you'll
   have /etc/timezone.

* Use pip to install pytz and slackclient modules, if not 
  already installed.

* Run the chatbot in a terminal window via 'python3 timebot.py'

* The bot will respond as long as the python program runs.


### Back in slack

* On your slack channel, type a few messages that do not involve the
   bot, like 'hello'. Will see them in the console window, but bot will
   not respond.

* Now try a message to the bot that asks the time: 
   @timebot, what time is it in India?

* You can give any valid timezone name ("America/New_York" or
   "Australia/Hobart"), as well as a few shorthand names
   ("California" or "India").

* If timebot is asked a question it does not know how to handle, it
   encourages a question it will recognize.


## Next steps

* Look at the code and think about how you'd want to extend it
   to do something useful for you.


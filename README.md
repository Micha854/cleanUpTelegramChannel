# cleanUpTelegramChannel

#### HELP ON DISCORD: https://discord.gg/rgkcZ6b

with this tool you can clean up your telegram channels

use the same bot token in all channels that you want to clean up. you create a separate config for each telegram channel.

before you start you have to deactivate /setprivacy in @BotFather!

"Sign messages" must be activated in all channels!

## install telepot:
`pip3 install telepot`

## start the cleanup with:
`python3 clean.py config.ini 2500`

2500 specifies the message_id from which to delete. All previous ids are ignored!
if you want to delete all ids use "0" as the start parameter

have fun
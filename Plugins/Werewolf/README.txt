This plugin moderates and leads a game of werewolf. You can read the rules on
http://www.eblong.com/zarf/werewolf.html
Project home is at https://launchpad.net/supybot-werewolf

Note for Freenode/OFTC users:
If the bot gets kicked because of flooding ("Excess Flood") try
to increase supybots throttle time with:
config supybot.protocols.irc.throttleTime 3.0

3.0 is a value that works for freenode, 1.0 is the default value. It represents
the time between messages sent by the bot.


Please also note that currently it probably is not possible to play in more
than one channel at the same time. If you want to run the bot in many
channels please create different supybot configurations.

If you need help setting the game up, have a look at
https://answers.launchpad.net/supybot-werewolf/+faqs

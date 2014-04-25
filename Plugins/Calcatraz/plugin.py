###
# by SpiderDave
###

import re
import urllib

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True

    def calc(self, irc, msg, args, text):
        """<expression>

        Uses www.calcatraz.com to calculate the value of <expression>.
        """
        url = 'https://www.calcatraz.com/calculator/api?c=%s' % utils.web.urlquote(text)
        html = utils.web.getUrl(url).strip()
        if not html:
            irc.error("I couldn't get a response from calcatraz.com.")
            return
        if html:
            if html=="answer":
                irc.reply("Error: I couldn't get a proper answer from Calcatraz.")
            else:
                irc.reply(html)
        else:
            irc.reply("Error: I couldn't get a response from Calcatraz.")
    calc = wrap(calc, [additional('text')])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

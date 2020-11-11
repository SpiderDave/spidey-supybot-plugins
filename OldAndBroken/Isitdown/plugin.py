###
# Copyright (c) 2016, SpiderDave
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

import re

try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
except:
    PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Plugin):
    """Add the help for "@plugin help <Plugin Name>" here
    """
    threaded = True
    def isitdown(self, irc, msg, args, text):
        """
        Check if a website is down using isup.me
        """
        
        url = format("""http://isup.me/%s""", utils.web.urlquote(text))
        try:
            html = utils.web.getUrl(url)
        except:
            irc.reply('Error: Could not get information from isup.me')
            return
        
        if re.search(r"It's just you", html, re.I | re.S):
            irc.reply("It's up")
            return
        elif re.search(r"It's not just you!", html, re.I | re.S):
            irc.reply("It's down")
            return
        else:
            irc.reply('Unknown')
    isitdown = wrap(isitdown, ['text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

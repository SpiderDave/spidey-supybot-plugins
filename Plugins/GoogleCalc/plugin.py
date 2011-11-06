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

        Uses Google's calculator to calculate the value of <expression>.
        """
        url = 'http://www.google.com/ig/calculator?hl=en&q=%s' % utils.web.urlquote(text)
        html = utils.web.getUrl(url)
        if not html:
            irc.error("I couldn't get a response from Google.")
            return
        #{lhs: "1 foot",rhs: "12 inches",error: "",icc: false}
        m = re.search('\{lhs: ".*?",rhs: "(.*?)",error: ".*?",icc: .*?}', html, re.I | re.S)
        if m:
            s=m.group(1)
            s = utils.str.normalizeWhitespace(s)
            s = s.replace('\xc2\xa0','') #remove the nbsp
            if s:
                irc.reply(s)
                return
            else:
                irc.reply('No result found.')
                return
        else:
            irc.error('Did not find a proper result from the calculator')
    calc = wrap(calc, [additional('text')])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

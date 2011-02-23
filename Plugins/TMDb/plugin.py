###
# by SpiderDave
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

import tmdb

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True

    def tmdb(self, irc, msg, args, text):
        """<film>

        Get information on <film> from TMDb
        """
        
        try:
            t = tmdb.search(text)
        except:
            irc.reply("Error: I couldn't get that information")
            return


        try:
            m=t[0]
        except:
            irc.reply('Not found.')
            return
        
        for key in m.keys():
            if isinstance(m[key],basestring):
                m[key]=m[key].encode('UTF-8')
        
        irc.reply('%s %s (%s) %s: %s' % (m['url'], ircutils.bold(m['name']),m['released'].split('-')[0], m['rating'], m['overview']))
    tmdb = wrap(tmdb, ['text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

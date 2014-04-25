###
# by SpiderDave
###

import supybot.utils as utils
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

import tmdb3 as tmdb

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
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            key=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return
        
        tmdb.set_key(key)
        tmdb.set_cache('null')
        
        try:
            res=tmdb.searchMovie(text)
        except:
            irc.reply("Error: I couldn't get a response from TMDb.")
            return
        
        if len(res)==0:
            irc.reply("Sorry, I couldn't find anything on that one.")
            return
        res=res[0] #just use the first one found
        text='%s (%s) %s/10 http://www.themoviedb.org/movie/%s %s' % ( ircutils.bold(res.title), res.releasedate.year, res.userrating, res.id, res.overview)
        irc.reply(text)
    tmdb = wrap(tmdb, ['text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

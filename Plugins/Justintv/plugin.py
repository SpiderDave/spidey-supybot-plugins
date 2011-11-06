###
# by SpiderDave
###
import socket
import urllib

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

simplejson = None

try:
    simplejson = utils.python.universalImport('json')
except ImportError:
    pass

try:
    # The 3rd party simplejson module was included in Python 2.6 and renamed to
    # json.  Unfortunately, this conflicts with the 3rd party json module.
    # Luckily, the 3rd party json module has a different interface so we test
    # to make sure we aren't using it.
    if simplejson is None or hasattr(simplejson, 'read'):
        simplejson = utils.python.universalImport('simplejson',
                                                  'local.simplejson')
except ImportError:
    raise callbacks.Error, \
            'You need Python2.6 or the simplejson module installed to use ' \
            'this plugin.  Download the module at ' \
            '<http://undefined.org/python/#simplejson>.'


# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True
    def jtvlive(self, irc, msg, args, things):
        """ <channel> [<channel> ...]
        
        Displays current live Justin.tv channels given a list.
        """
        #kawaiirice, fxomoonglade, hashe, liquidtlo, liquidhuk, liquidhaypro, spanishiwa
        channels=things
        
        searchurl='http://api.justin.tv/api/stream/list.json'
        headers = utils.web.defaultHeaders
        #usernames=['kawaiirice','fxomoonglade','hashe','liquidtlo','liquidhuk','liquidhaypro','spanishiwa']
        islive=[]
        out=[]


        opts = {}
        opts['channel']=','.join(channels)
        fd = utils.web.getUrlFd('%s?%s' % (searchurl,
                                           urllib.urlencode(opts)),
                                headers)
        json = simplejson.load(fd)
        fd.close()

        if not json:
            # Most likely no streams are live
            pass
        else:
            for c in json:
                channelurl=c['channel']['channel_url'].encode('utf-8')
                if 'live' in c['name']:
                    if c.get('title'):
                        title=c['title'].encode('utf-8')
                    else:
                        title='(no title)'
                    out.append('%s %s' % (channelurl, title))
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No current live streams.')
    jtvlive = wrap(jtvlive, [many('anything')])

    
    def livestreamlive(self, irc, msg, args, things):
        """ <channel> [<channel> ...]
        
        Displays current live Livestream channels given a list.
        """
        channels=things
        
        headers = utils.web.defaultHeaders
        islive=[]
        out=[]


        opts = {}
        opts['channel']=','.join(channels)
        
        for c in channels:
            searchurl = 'http://x%sx.api.channel.livestream.com/2.0/livestatus.json' % c.replace('_','-')
            fd = utils.web.getUrlFd(searchurl, headers)

            json = simplejson.load(fd)
            fd.close()

            if not json:
                # Most likely no streams are live
                pass
            else:
                if json['channel']:
                    if json['channel']['isLive']:
                        channelurl='http://www.livestream.com/%s' % c
                        out.append('%s' % channelurl)
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No current live streams.')
    livestreamlive = wrap(livestreamlive, [many('anything')])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

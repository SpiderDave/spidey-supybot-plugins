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
    def twitchtvlive(self, irc, msg, args, things):
        """ <channel> [<channel> ...]
        
        Displays current live Twitch.tv channels given a list.  Note: channel names are case-sensitive.
        """
        channels=things
        
        searchurl='https://api.twitch.tv/kraken/streams'
        headers = utils.web.defaultHeaders
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
            if json:
                if not json.get('streams'):
                    # got a response, but streams is empty; nothing live.
                    irc.reply('No current live streams.')
                    return
            for c in json.get('streams'):
                channel=c.get('channel')
                channelurl=channel['url'].encode('utf-8')
                title=channel.get('status','(no title)').encode('utf-8')
                out.append('%s %s' % (channelurl, title))
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No current live streams.')
    twitchtvlive = wrap(twitchtvlive, [many('anything')])

    
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

    def hitboxtvlive(self, irc, msg, args, things):
        """ <channel> [<channel> ...]
        
        Displays current live hitbox.tv channels given a list.
        """
        channels=things
        
        headers = utils.web.defaultHeaders
        islive=[]
        out=[]

        opts = {}
        opts['channel']=','.join(channels)
        
        for c in channels:
            searchurl = 'http://www.hitbox.tv/api/media/live/%s/showHidden=true' % c
            try:
                fd = utils.web.getUrlFd(searchurl, headers)
                json = simplejson.load(fd)
                fd.close()
            except:
                # Probably not a valid user
                json=None
                pass

            if not json:
                pass
            else:
                live=json['livestream'][0]['media_is_live']
                if live == '1':
                    channelurl='http://www.hitbox.tv/%s' % c
                    out.append('%s' % channelurl)
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No current live streams.')
    hitboxtvlive = wrap(hitboxtvlive, [many('anything')])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

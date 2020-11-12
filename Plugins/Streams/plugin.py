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
import json

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """This plugin displays live channels from streaming sites."""
#    def twitchtvlive(self, irc, msg, args, things):
#        """ <channel> [<channel> ...]
        
#        Displays current live Twitch.tv channels given a list.  Note: channel names are case-sensitive.
#        """
#        threaded = True
#        channels=things
        
#        searchurl='https://api.twitch.tv/kraken/streams'
#        headers = utils.web.defaultHeaders
#        islive=[]
#        out=[]
        
#        opts = {}
#        opts['channel']=','.join(channels)
#        fd = utils.web.getUrlFd('%s?%s' % (searchurl,
#                                           urllib.urlencode(opts)),
#                                headers)
#        json = simplejson.load(fd)
#        fd.close()

#        if not json:
            # Most likely no streams are live
#            pass
#        else:
#            if json:
#                if not json.get('streams'):
                    # got a response, but streams is empty; nothing live.
#                    irc.reply('No current live streams.')
#                    return
#            for c in json.get('streams'):
#                channel=c.get('channel')
#                channelurl=channel['url'].encode('utf-8')
#                title=channel.get('status','(no title)').encode('utf-8')
#                out.append('%s %s' % (channelurl, title))
#        if out:
#            irc.reply(' | '.join(out))
#        else:
#            irc.reply('No current live streams.')
#    twitchtvlive = wrap(twitchtvlive, [many('anything')])
    
    def smashcastlive(self, irc, msg, args, things):
        """ <channel> [<channel> ...]
        
        Displays current live channels on www.smashcast.tv given a list.
        """
        threaded = True
        channels=things
        
        headers = utils.web.defaultHeaders
        islive=[]
        out=[]

        opts = {}
        opts['channel']=','.join(channels)
        
        for c in channels:
            searchurl = 'https://www.smashcast.tv/api/media/live/%s/showHidden=true' % c
            try:
                fd = utils.web.getUrlFd(searchurl, headers)
                jsonData = json.load(fd)
                fd.close()
            except:
                # Probably not a valid user
                jsonData=None
                pass

            if not jsonData:
                pass
            else:
                live=jsonData['livestream'][0]['media_is_live']
                if live == '1':
                    channelurl='http://www.smashcast.tv/%s' % c
                    out.append('%s' % channelurl)
        if out:
            irc.reply(' | '.join(out))
        else:
            irc.reply('No current live streams.')
    smashcastlive = wrap(smashcastlive, [many('anything')])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

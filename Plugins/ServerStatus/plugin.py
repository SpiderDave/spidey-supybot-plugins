###
# by SpiderDave
###
import urllib

import re
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os
try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
except:
    PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x


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

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Plugin):
    """Contains commands for checking the server status of various games."""
#    I have no idea how long gstatus.de has been down, just removing this for now.
#
#    def diablo3(self, irc, msg, args):
#        """
#        Get Diablo 3 server status from www.gstatus.de
#        """
#        threaded = True
#        url = 'http://www.gstatus.de/game/diablo3'
#        try:
#            html = utils.web.getUrl(url)
#        except:
#            irc.reply('Error: could not get a response from gstatus.de')
#            return
#        m = re.search(r'<tr><td.*?>Europe</td>.*?Login.*?</i>(.*?)</span>.*?Americas</td>.*?Login.*?</i>(.*?)</span>.*?Asia</td>.*?Login.*?</i>(.*?)</span>', html, re.I | re.S)
        
#        if m:
#            text='Diablo 3 Server Status: Europe: %s | Americas: %s | Asia: %s' % (m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
#            text=text.replace("Available","up")
#            text=text.replace("Unavailable","down")
#            irc.reply(text)
#        else:
#            irc.reply('Error: could not get information from gstatus.de')
#    diablo3 = wrap(diablo3)
    
    def leagueoflegends(self, irc, msg, args, region):
        """<region>
        
        Get League of Legends server status for the given region.
        """
        threaded = True
        
        api_key = self.registryValue('riotAPIKey')
        validRegions = self.registryValue('lolValidRegions')
        defaultRegion = self.registryValue('lolDefaultRegion')
        
        if api_key == '':
            irc.error('Missing Riot API key.  Please set plugins.riotAPIKey.')
            return
        if validRegions == '':
            # Should be something like this: RU KR PBE1 BR1 OC1 JP1 NA1 EUN1 EUW1 TR1 LA1 LA2
            irc.error('Missing valid regions.  Please set plugins.lolValidRegions.')
            return
        if defaultRegion == '':
            defaultRegion = 'NA1'
            pass
            # irc.error('Missing default region.  Please set plugins.lolValidRegions.')
            #return
        
        region = region or defaultRegion
        if region.lower() not in validRegions.lower().split():
            irc.error('Valid regions are %s' % validRegions)
            return
        
        url = 'https://%s.api.riotgames.com/lol/status/v3/shard-data' % region.lower()
        headers = utils.web.defaultHeaders
        
        opts = {}
        opts['api_key']=api_key
        fd = utils.web.getUrlFd('%s?%s' % (url,
                                           urllib.urlencode(opts)),
                                headers)
        
        json = simplejson.load(fd)
        fd.close()
        
        out = ''
        
        if not json:
            irc.error('Could not get data.')
            return
        else:
            if json:
                if not json.get('services'):
                    # got a response, but services is empty.
                    irc.error('Could not get data.')
                    return
            for c in json.get('services'):
                if c.get('slug') == 'game':
                    out = '%s: %s' % (json.get('name'), c.get('status'))
        if out:
            irc.reply(out)
        else:
            irc.error('Could not get data.')


    leagueoflegends = wrap(leagueoflegends, [optional('somethingWithoutSpaces')])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

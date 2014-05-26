###
# by SpiderDave
###

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

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Plugin):
    """Contains commands for checking the server status of various games."""
    threaded = True
    def diablo3(self, irc, msg, args):
        """
        Get Diablo 3 server status from www.gstatus.de
        """
        url = 'http://www.gstatus.de/game/diablo3'
        try:
            html = utils.web.getUrl(url)
        except:
            irc.reply('Error: could not get a response from gstatus.de')
            return
        m = re.search(r'<tr><td.*?>Europe</td>.*?Login.*?</i>(.*?)</span>.*?Americas</td>.*?Login.*?</i>(.*?)</span>.*?Asia</td>.*?Login.*?</i>(.*?)</span>', html, re.I | re.S)
        
        if m:
            text='Diablo 3 Server Status: Europe: %s | Americas: %s | Asia: %s' % (m.group(1).strip(), m.group(2).strip(), m.group(3).strip())
            text=text.replace("Available","up")
            text=text.replace("Unavailable","down")
            irc.reply(text)
        else:
            irc.reply('Error: could not get information from gstatus.de')
    diablo3 = wrap(diablo3)
    
    def leagueoflegends(self, irc, msg, args):
        """
        Get League of Legends server status from www.lolking.net
        """
        url = 'http://www.lolking.net/status' #the /status page is outdated; we're really just grabbing it from the header.
        try:
            html = utils.web.getUrl(url)
        except:
            irc.reply("Error: could not get a response from www.lolking.net")
            return
        m = re.search(r'<span id="online_servers".*?>(.*?)</span>.*?<span id="offline_servers".*?>(.*?)</span>.*?fallback: \'(.*?)\'', html, re.I | re.S)
        if m:
            irc.reply('%s %s | %s' % (m.group(1),m.group(3),m.group(2)))
        else:
            irc.reply("Error: could not get server status.")
    leagueoflegends = wrap(leagueoflegends)


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

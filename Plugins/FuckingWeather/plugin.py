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
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("Beautiful Soup 4 is required for this plugin: get it"
                      " at http://www.crummy.com/software/BeautifulSoup/bs4"
                      "/doc/#installing-beautiful-soup")

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Privmsg):

    def fuckingweather(self, irc, msg, args, text):
        """
        <zip code>: Displays the weather from http://www.thefuckingweather.com/
        """
        url = 'http://www.thefuckingweather.com/Where/%s' % text
        try:
            soup = BeautifulSoup(utils.web.getUrl(url))
            
            temperature = [element.text for element in soup.find_all("span", {'class': 'temperature jsMainTemp'})][0]
            remark = [element.text for element in soup.find_all("p", {'class': 'remark'})][0]
            flavor = [element.text for element in soup.find_all("p", {'class': 'flavor'})][0]
            location = [element.text for element in soup.find_all("span", {'id': 'locationDisplay'})][0]
            
            res = "%s\u00B0 in %s?! %s.  %s." % (temperature, location, remark, flavor)
            irc.reply(res, prefixNick=True)
        except:
            irc.reply("ERROR, FUCKING BROKEN.", prefixNick=True)

    fuckingweather = wrap(fuckingweather, ['text'])

_Plugin.__name__=PluginName
Class = _Plugin

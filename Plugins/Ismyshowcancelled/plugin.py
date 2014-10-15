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
import urllib, urllib2
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
    def ismyshowcancelled(self, irc, msg, args, text):
        """
        find the status of a tv show from http://www.ismyshowcancelled.com
        """
        url = 'http://www.ismyshowcancelled.com/shows/search/page/1/'
        
        # set up post values
        values = {'Search': text
                  }
        
        # create handler
        redirectionHandler = urllib2.HTTPRedirectHandler() 

        # apply the handler to an opener
        opener = urllib2.build_opener(redirectionHandler)

        # install the openers
        urllib2.install_opener(opener)

        request = urllib2.Request(url, data=urllib.urlencode(values))
        
        try:
            response = urllib2.urlopen(request)
        
            html = response.read()
        except:
            irc.reply("Error: couldn't get information from the site.")
            return
        
        m = re.search(r'No shows were found that matched your criteria. Please try searching again.', html, re.I | re.S)
        # if the response url is the same as the one we gave, assume there's no match
        if m or (url == response.geturl()):
            irc.reply('Error: Show not found.')
            return
        
        m = re.search(r"<div class='Post-Can-Name'><h2.*?>(.*?)</h2></div>.*?<div class='Post-Can-Status'><span.*?>(.*?)</span></div>", html, re.I | re.S)
        if m:
            text='%s : %s' % (m.group(1),m.group(2))
            irc.reply(text)
        else:
            irc.reply('Error :(')
    ismyshowcancelled = wrap(ismyshowcancelled, ['text'])
    
_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

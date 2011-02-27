###
# plugins/Pastebin.py by SpiderDave
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os
import urllib, urllib2

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """This plugin contains a command to upload text to pastebin.com."""
    threaded = True

    def pastebin (self, irc, msg, args, text):
        """<text>
        
        post <text> to pastebin.com.  Expires in 1 month.
        """
        threaded=True
        api_url = 'http://pastebin.com/api_public.php'
        #valid_paste_expire_dates = ('N', '10M', '1H', '1D', '1M')
        
        values = {'paste_code' : text,
                  'paste_name' : irc.nick,
                  #'paste_subdomain':'test',
                  'paste_format':'text',
                  'paste_private':1,
                  'paste_expire_date' : '1M'
                  }

        data = urllib.urlencode(values)
        req = urllib2.Request(api_url, data)
        response = urllib2.urlopen(req)
        the_page = response.read()
        irc.reply(the_page)

    pastebin = wrap(pastebin, ['text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

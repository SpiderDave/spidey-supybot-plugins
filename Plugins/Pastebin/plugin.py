###
# plugins/Pastebin.py by SpiderDave
###

import supybot.utils as utils
import supybot.conf as conf
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
        api_url = 'http://pastebin.com/api/api_post.php'
        
        try:
            f = open('%s%spastebin.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            api_dev_key=f.read().strip()
            f.close()
        except:
            irc.reply('Error: missing or invalid api dev key.  Check pastebin.dat file in your data folder.')
            return
        
        #valid_paste_expire_dates = ('N', '10M', '1H', '1D', '1M')
        
        values = {'api_option' : 'paste',
                  'api_dev_key' : api_dev_key,
                  'api_paste_code' : text,
                  'api_paste_private':'1',
                  'api_paste_name' : irc.nick,
                  'api_paste_expire_date' : '1M',
                  'api_paste_format':'text',
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

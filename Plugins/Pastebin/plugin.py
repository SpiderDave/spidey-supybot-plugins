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
#import urllib, urllib2
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse
from time import gmtime, strftime

# documentation from: http://pastebin.com/api

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """This plugin contains a command to upload text to pastebin.com."""
    threaded = True

    def pastebin (self, irc, msg, args, opts, text):
        """[--visibility public|unlisted|private] [--title name] [--expire never|10min|1hour|1day|1month] <text>
        
        post <text> to pastebin.com.
        Default visibility is unlisted. Default expiration is never.
        """
        
        api_key = self.registryValue('pastebinAPIkey')

        if api_key == '':
            irc.reply('Error: Pastebin API key must be set. See plugins.pastebinAPIkey value.')
            return
        
        api_url = 'https://pastebin.com/api/api_post.php'
        
        # default args.
        visibility = self.registryValue('visibility').lower()
        expire = self.registryValue('expire').lower()
        title = msg.nick + "@" + msg.args[0] + "@" + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        
        # input options
        for (key, value) in opts:
            if key == 'visibility':
                visibility = value
            if key == 'title' or key == "pastename":
                title = value
            if key == 'expire':
                expire = value
        
        # map visibility and expire to proper values via key
        visibility_map = {'public': '0', 'unlisted': '1', 'private': '2'}
        visibility = visibility_map[visibility]
        expire_map = {'never': 'N', '10min': '10M', '1hour': '1H', '1day': '1D', '1month': '1M'}
        expire = expire_map[expire]

        # post values
        values = {'api_paste_code': text,
                  'api_paste_name': title,
                  'api_paste_format':'text',
                  'api_paste_private': visibility,
                  'api_paste_expire_date': expire,
                  'api_option': 'paste',
                  'api_dev_key': api_key
                  }
        
        data = urllib.parse.urlencode(values).encode('utf-8') 
        req = urllib.request.Request(api_url, data)
        response = urllib.request.urlopen(req)
        the_page = response.read().decode('utf-8')
        
        # print return data or url
        irc.reply(the_page)

    pastebin = wrap(pastebin, [getopts({'visibility': ('literal',
                                                        ('public',
                                                        'unlisted',
                                                        'private')),
                                         'pastename': ('something'),
                                         'title': ('something'),
                                         'expire': ('literal',
                                                    ('never',
                                                    '10min',
                                                    '1hour',
                                                    '1day',
                                                    '1month'))
                                                        }), ('text')])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

###
# Copyright (c) 2014, SpiderDave
# All rights reserved.
#
#
###

import re
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import datetime
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
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True
    _googlevRe = re.compile(r'"titleNoFormatting":"(.*?)",.*?"Url":"(.*?)".*?"duration":"(.*?)"', re.I | re.S)
    def googlev(self, irc, msg, args, text):
        """<text>
        
        Searches for a video of <text> using Google Video.  Youtube embeds will give youtube links.
        """
        #text = utils.web.urlquote(text+' -VEVO') # i hate vevo >.<
        text = utils.web.urlquote(text)
        
        debug=0
        if '--debug' in text:
            text=text.replace('--debug', '')
            debug=1
        
        text=utils.str.normalizeWhitespace(text)
        url=format("""http://ajax.googleapis.com/ajax/services/search/video?v=1.0&q=%s""",text)
        if debug==1:
            irc.reply('debug: %s' % url)
        html = utils.web.htmlToText(utils.web.getUrl(url))
        m = self._googlevRe.search(html)
        if m:
            title=m.group(1)
            duration=str(datetime.timedelta(seconds=int(m.group(3))))
            link=(m.group(2).encode())
            link=link.decode('unicode_escape')
            link=str(link)
            s='%s (%s) %s' % (ircutils.bold(title), duration, link)
            s = utils.str.normalizeWhitespace(s)
            s=s.replace('http://www.youtube.com/watch?v=','http://youtu.be/')
            s=s.replace('https://www.youtube.com/watch?v=','https://youtu.be/')
            irc.reply('%s' % s)
        else:
            if '{"results":[]' in html:
                irc.reply('Not found.')
            else:
                irc.reply("Error. (onoes)")
    googlev = wrap(googlev, ['text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

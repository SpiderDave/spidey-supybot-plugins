###
# by SpiderDave
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os
import re

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
    
    def cleanup(self, t):
        t = re.sub(r'&#39;',"'",t)
        t = re.sub(r'<sup>(.*)</sup>&#8260;<sub>(.*)</sub>', r' \1/\2', t)
        t = re.sub(r'<sup>(.*)</sup>', r'^\1', t)
        t = utils.web.htmlToText(t)
        t = utils.str.normalizeWhitespace(t)
        return t
    
    _blastRe = re.compile(r'<url><!\[CDATA\[(.*?)\]\]></url>', re.I)
    _blast_titleRe = re.compile(r'<title><!\[CDATA\[(.*?)\]\]></title>', re.I)
    _blast_errorRe = re.compile(r'<error.*?>(.*?)</error>', re.I)    
    def blast(self, irc, msg, args, text):
        """<text>
        
        Searches for <text> on Gigablast.
        """
        if not text:
            irc.reply("You have to search for something, silly.")
        else:
            text = utils.web.urlquote(text)
            url = 'http://www.gigablast.com/search?q=%s&raw=9&n=1' % text
            s = utils.web.getUrl(url)
            err = self._blast_errorRe.search(s)
            if err:
                irc.reply(utils.str.normalizeWhitespace(err.group(1)))
            else:
                m = self._blastRe.search(s)
                t = self._blast_titleRe.search(s)
                if m:
                    title = self.cleanup(t.group(1))
                    result = self.cleanup(m.group(1))
                    irc.reply('%s - %s' % (ircutils.bold(title), result))
                else:
                    irc.reply("""Fail :(""")
    blast = wrap(blast, [('text')])



_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

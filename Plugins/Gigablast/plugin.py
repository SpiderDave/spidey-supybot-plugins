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
    
    _blast_resultsRe = re.compile(r'"moreResultsFollow":(.*?),', re.S | re.I)
    _blastRe = re.compile(r'"results":.*?"title":"(.*?)".*?"url":"(.*?)"', re.S | re.I)
    _blast_errorRe = re.compile(r'<error.*?>(.*?)</error>', re.I)
    
    #http://www.gigablast.com/api.html?c=main#/search
    
    def blast(self, irc, msg, args, text):
        """<text>
        
        Searches for <text> on Gigablast.
        """
        if not text:
            irc.reply("You have to search for something, silly.")
        else:
            text = utils.web.urlquote(text)
            url = 'http://www.gigablast.com/search?c=main&q=%s&format=json&dsrt=0&n=1' % text
            s = utils.web.getUrl(url)
            err = self._blast_errorRe.search(s)
            if err:
                irc.reply(utils.str.normalizeWhitespace(err.group(1)))
            else:
                m = self._blast_resultsRe.search(s)
                if m:
                    nResults = int(m.group(1))
                    if nResults == 0:
                        irc.reply('No results. :(')
                    else:
                        m = self._blastRe.search(s)
                        if m:
                            irc.reply('%s - %s' % (ircutils.bold(m.group(2)), m.group(1)))
                        else:
                            # results were found, but couldn't get the information; format may have changed
                            irc.reply("""Fail :(""")
                else:
                    # couldn't find number of results, site could be unavailable
                    irc.reply("""Fail :(""")
    blast = wrap(blast, [('text')])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

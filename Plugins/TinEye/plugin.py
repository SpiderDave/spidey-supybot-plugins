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
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True
    def tin(self, irc, msg, args, opts, stuff):
        """[--sort biggest|best|mostchanged|newest|oldest] <image>

        Runs a search for <image> on <http://tineye.com>
        """
        
        sortBy = dict(opts).get('sort', self.registryValue('sort').lower())
        
        if sortBy=='biggest':
            url='http://tineye.com/search?url=%s&sort=size&order=desc' % utils.web.urlquote(stuff)
        elif sortBy=='best':
            url='http://tineye.com/search?url=%s&sort=score&order=desc' % utils.web.urlquote(stuff)
        elif sortBy=='mostchanged':
            url='http://tineye.com/search?url=%s&sort=score&order=asc' % utils.web.urlquote(stuff)
        elif sortBy=='newest':
            url='http://tineye.com/search?url=%s&sort=crawl_date&order=desc' % utils.web.urlquote(stuff)
        elif sortBy=='oldest':
            url='http://tineye.com/search?url=%s&sort=crawl_date&order=asc' % utils.web.urlquote(stuff)
        else:
            irc.reply('Error: invalid sort option "%s"' % sortBy)
            return
        
        try:
            html = utils.web.getUrl(url)
        except:
            irc.reply('Error: Could not get a response from TinEye.')
            return

        if re.search(r'<h2><span>0</span> Results</h2>', html, re.I|re.S):
            irc.reply("No results.")
            return
        
        m = re.search(r'<div id="search_results_results">.*?(?:<div class="search-results-item contributer-all clearfix">.*?</div>)?.*?<div class="search-results-location">.*?<a href="([^"]*?\.(?:jpg|jpeg|gif|png|bmp))".*?</a>', html, re.I|re.S)
        if m:
            s = m.group(1)
            irc.reply(s)
        else:
            irc.reply("Error. (onoes)")

    tin = wrap(tin, [getopts({'sort':('literal',('biggest','best','mostchanged','newest','oldest'))}), 'text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

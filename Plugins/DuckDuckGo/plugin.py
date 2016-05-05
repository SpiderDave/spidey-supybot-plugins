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
from HTMLParser import HTMLParser
try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
except:
    PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Plugin):
    """This is a plugin to search DuckDuckGo.
    """
    threaded = True

    def _strip_tags(self, html):
        result = []
        parser = HTMLParser()
        parser.handle_data = result.append
        parser.feed(html)
        parser.close()
        return ''.join(result)
    
    def search(self, irc, msg, args, opts, text):
        """[--nresults <value>] <text>
        
        Search for <text> on duckduckgo.com.  If option --nresults is used, returns the specified number of results.
        """
        url = 'https://duckduckgo.com/lite?q=%s' % utils.web.urlquote(text)
        html = utils.web.getUrl(url)
        
        showTitle = self.registryValue('showTitle')
        showSnippet = self.registryValue('showSnippet')
        nResults = self.registryValue('nResults')
        separator = ' %s ' % self.registryValue('separator')
        for (key, value) in opts:
            if key == 'nresults':
                nResults = value
        
        notFound = re.search("""<span class='no-results'>(.*?)</span>""", html, re.I | re.S)
        if notFound:
            # We'll try to use the site's "not found" message.  Not sure if it ever changes.
            out=''
            if notFound.group(1):
                out = utils.str.normalizeWhitespace(self._strip_tags(notFound.group(1)))
            else:
                out = 'No results.'
            irc.reply(out)
            return
        
        output = []
        results = re.findall("""<td valign="top">.*?</td>.*?<a .*? href="(.*?)".*?>(.*?)</a>.*?<tr>.*?<td.*?class='result-snippet'.*?>(.*?)</td>""", html, re.I | re.S)
        for result in results:
            title = ircutils.bold(utils.str.normalizeWhitespace(  self._strip_tags(result[1])  ))
            resultUrl = result[0]
            snippet = utils.str.normalizeWhitespace(  self._strip_tags(result[2])  )
            
            s = '<%s>' % resultUrl
            if showTitle:
                s = '%s - %s' % (title, s)
            if showSnippet:
                s = '%s %s' % (s, snippet)
            output.append(s)
        irc.reply(separator.join(output[:nResults]))
    search = wrap(search, [getopts({'nresults': 'positiveInt'}), 'text'])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

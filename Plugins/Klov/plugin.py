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
    """Contains a command to search for information on arcade games."""
    threaded = True

    def _strip_tags(self, html):
        result = []
        parser = HTMLParser()
        parser.handle_data = result.append
        parser.feed(html)
        parser.close()
        return ''.join(result)

    def klov(self, irc, msg, args, text):
        """<game>
        
        video game information on <game> from http://www.arcade-museum.com
        """
        text = utils.web.urlquote(text)
        url = format("""http://www.arcade-museum.com/results.php?boolean=AND&type=Videogame&q=%s""", text)
        html = utils.web.getUrl(url)
        notfound = re.search("""Number of Search Results: 0""", html, re.I | re.S)
        if notfound:
            irc.reply('Not found')
            self.log.info(url)
        else:
            m = re.search("""<TH>Name</TH>.*?<A HREF="game_detail.php\?game_id=(.*?)">(.*?)</A></TD><TD>(.*?)</TD><TD>(.*?)</TD>""", html, re.I | re.S)
            if m:
                s = ircutils.bold(utils.str.normalizeWhitespace(m.group(2))) + " // "+utils.str.normalizeWhitespace(m.group(3)) + " // " +utils.str.normalizeWhitespace(m.group(4)) + " // " + "http://www.arcade-museum.com/game_detail.php?game_id=" +utils.str.normalizeWhitespace(m.group(1))
                s = self._strip_tags(s)
                irc.reply(s)
            else:
                irc.reply("Error")
    klov = wrap(klov, ['text'])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

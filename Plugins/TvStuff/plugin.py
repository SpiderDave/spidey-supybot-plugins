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
#import urllib, urllib2
import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse

try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
except:
    PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Plugin):
    """Contains commands for checking the status of tv shows."""
    threaded = True
    def ismyshowcancelled(self, irc, msg, args, text):
        """
        find the status of a tv show from http://www.ismyshowcancelled.com
        """
        
        url = 'http://www.ismyshowcancelled.com/shows/search/page/1/?' + urllib.parse.urlencode({'Search': text})
        
        try:
            response = urllib.request.urlopen(url)
        except:
            irc.reply('Error: Could not get information.')
            return
        
        html = response.read()
        
        m = re.search(b'<div class="pg-title-bar"><h2>(.*?)</h2></div>.*?<div class="status"><span.*?>(.*?)</span></div>', html, re.I | re.S)
        m2 = re.search(b"<div><h3>(.*?)</h3><span.*?>(.*?)</span></div>", html, re.I | re.S)
        if m:
            text='%s : %s' % (m.group(1).decode("utf-8"),m.group(2).decode("utf-8"))
            irc.reply(text)
        elif m2:
            text='%s : %s' % (m2.group(1).decode("utf-8"),m2.group(2).decode("utf-8"))
            irc.reply(text)
        else:
            irc.reply('Error: Show not found.')
    ismyshowcancelled = wrap(ismyshowcancelled, ['text'])
    
    _reNext = re.compile(r'<div id="next_episode".*?>.*?<div class="subheadline"><h3>Date:</h3></div>(.*?)<div></div>.*?Season:</h3></div>(.*?)<div></div>.*?Episode:</div><div.*?>(.*?)</div></div>', re.I | re.S)
    _reStatus = re.compile(r'<div id="middle_section".*?>.*?<div class="subheadline"><h3>Status:</h3></div>(.*?)<div></div>', re.I | re.S)
    def nextepisode(self, irc, msg, args, text):
        """
        get next episode information from http://next-episode.net/
        """
        show = text.lower().replace(" ","-")
        nextEpisode = False
        nextEp = False
        status = False
        url= 'http://next-episode.net/' + utils.web.urlquote(show)
        try:
            html = utils.web.getUrl(url).decode("utf-8")
        except:
            #404
            irc.reply("Series not found.")
            return
        m = self._reNext.search(html)
        if m:
            nextEp = utils.str.normalizeWhitespace(m.group(1)).strip()
            season = m.group(2)
            episodeNum = m.group(3)
            episodeNum=episodeNum.split(',')
        m = self._reStatus.search(html)
        if m:
            status = utils.str.normalizeWhitespace(m.group(1)).strip()
        if nextEp or status:
            out = ""
            if status: out = out + "Status: %s" % status
            if status and nextEp: out = out + " | "
            if nextEp: 
                out = out + "Next Episode: "
                for i in range(0,len(episodeNum)):
                    out = out + "s%02de%02d " % (int(season), int(episodeNum[i]))
                out = out + " %s" % (nextEp)
            irc.reply(out)
        else:
            irc.reply("Error: could not get information for that series.")
    nextepisode = wrap(nextepisode, ['text'])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

###
# Copyright (c) 2015, SpiderDave
# All rights reserved.
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
    """
    threaded = True
    
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
            html = utils.web.getUrl(url)
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

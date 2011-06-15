###
# Copyright (c) 2005, Jeremiah Fincher
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import re

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class NameDecoder(callbacks.Plugin):
    """Returns a acronyms for a specified name from <http://www.NameDecoder.com/>.  Ex. @Cyborg John"""

    threaded = True
    def callCommand(self, command, irc, msg, *args, **kwargs):
        try:
            super(NameDecoder, self).callCommand(command,irc,msg,*args,**kwargs)
        except utils.web.Error, e:
            irc.error(str(e))

    _cyborgRe = re.compile(r'<div class="mediumheader">(.*?)</div>', re.I)
    def cyborg(self, irc, msg, args, name):
        """[<name>]

        Returns a cyborg acronym for <name> from <http://www.NameDecoder.com/>.
        If <name> is not specified, uses that of the user.
        """
        if not name:
            name = msg.nick
        name = utils.web.urlquote(name)
        # url = 'http://www.NameDecoder.com/cyborger.cgi?acronym=' + name
        url= 'http://cyborg.namedecoder.com/index.php?acronym=' + name
        html = utils.web.getUrl(url)
        m = self._cyborgRe.search(html)
        if m:
            s = m.group(1)
            s = utils.str.normalizeWhitespace(s)
            irc.reply(s)
        else:
            irc.errorPossibleBug('No cyborg name returned.')
    cyborg = wrap(cyborg, [additional('somethingWithoutSpaces')])

    _monsterRe = re.compile(r'<div class="mediumheader">(.*?)</div>', re.I)
    def monster(self, irc, msg, args, name):
        """[<name>]

        Returns a monster acronym for <name> from <http://www.NameDecoder.com/>.
        If <name> is not specified, uses that of the user.
        """
        if not name:
            name = msg.nick
        name = utils.web.urlquote(name)
        url= 'http://monster.namedecoder.com/index.php?acronym=' + name
        html = utils.web.getUrl(url)
        m = self._monsterRe.search(html)
        if m:
            s = m.group(1)
            s = utils.str.normalizeWhitespace(s)
            irc.reply(s)
        else:
            irc.errorPossibleBug('No monster name returned.')
    monster = wrap(monster, [additional('somethingWithoutSpaces')])

    _sexyRe = re.compile(r'<div class="mediumheader">(.*?)</div>', re.I)
    def sexy(self, irc, msg, args, gender, name):
        """[<gender>] [<name>]

        Returns a sexy acronym for <name> from <http://www.NameDecoder.com/>.
        <gender> can be 'm', 'f', 'male', or 'female'.  If <gender> is not specified, male is used.
        If <name> is not specified, uses that of the user.
        """
        # It's a little sloppy atm, but works
        if gender:
            if not name:
                name=gender
                gender='m'
            else:
                gender=gender.lower().strip().replace('male','m').replace('female','f')
                if gender not in ['m','f']:
                    irc.reply('Invalid gender.')
                    return
        else:
            gender='m'
        if not name:
            name = msg.nick
        name = utils.web.urlquote(name)
        url= 'http://sexy.namedecoder.com/index.php?acronym={0}&otherflag={1}'.format(name,gender)
        html = utils.web.getUrl(url)
        m = self._sexyRe.search(html)
        if m:
            s = m.group(1)
            s = utils.str.normalizeWhitespace(s)
            irc.reply(s)
        else:
            irc.errorPossibleBug('No sexy name returned.')
    sexy = wrap(sexy, [optional('somethingWithoutSpaces'), additional('somethingWithoutSpaces')])

Class = NameDecoder


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

###
# by SpiderDave
###

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """This plugin generates a random superhero description for the given nick."""
    threaded = True
    # **********************************************************************
    # Note: the superhero text is saved in a text file so that each nick gives 
    # the same unique power.  I think it's more fun this way.
    def superhero(self, irc, msg, args, name):
        """[<name>]
        
        Random Superhero Generator from http://www.rps.net/cgi-bin/stone/randpower.pl
        """
        if not name:
            name = msg.nick


        filename = conf.supybot.directories.data.dirize("superhero.txt")
        f=open(filename,'a+b')
        f.close()
        f=open(filename,'r+b')
        superhero=f.readlines()



        try:
            filename = conf.supybot.directories.data.dirize("superhero.txt")
            f=open(filename,'a+b')
            f.close()
            f=open(filename,'r+b')
            superhero=f.readlines()
        except:
            irc.reply('error :(')
            return

        power=[t.split(':',1)[1] for t in superhero if t.lower().startswith('%s:' % (name.lower()))]
        if power:
            power=power[0].strip().replace('_name_',name)
            irc.reply('%s' % power, prefixNick=False)
        else:
            url = 'http://www.rps.net/cgi-bin/stone/randpower.pl?sex=0&weakness=0&numpowers=2&name=_name_'
            html = utils.web.getUrl(url)
            txt=html.split('<H1>Random Superhero Generator!</H1>',1)[1].split('<P>',1)[0].strip()
            f.write('%s:%s\n' % (name, txt))
            irc.reply(txt.replace('_name_',name), prefixNick=False)
        f.close()
    superhero = wrap(superhero, [additional('somethingWithoutSpaces')])


_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

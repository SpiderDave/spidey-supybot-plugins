###
# Slap/plugin.py
# by SpiderDave
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import random, os

def capability(msg, c):
    try:
        u = ircdb.users.getUser(msg.prefix)
        if u._checkCapability(c):
            return True
    except:
        return False

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """This plugin is for slapping people with random things.  Joy!"""
    pluginpath=os.path.dirname( __file__ ) + os.sep
    validgenders=['male','female', 'none']

    # **********************************************************************
    def slap( self, irc, msg, args, stuff ):
        """ [[--]add <an object>]|[<someone>]

        Slaps <someone> with a random silly object.  Slap add <an object> will add an item to the slaplist.
        """
        f=open('%sslap.txt' % self.pluginpath, 'a+b')
        l=open('%sslap.txt' % self.pluginpath, 'a+b').readlines()
        t=l[random.randint(0,len(l)-1)]
        t = t.replace("\'", "'").replace("\r", "").replace("\n", "")
        if not stuff:
            stuff="someone"
        if (stuff.lower() == irc.nick.lower()) or (stuff.lower() == 'yourself'):
            try:
                fmeta=open('%sbot_meta.txt' % self.pluginpath, 'a+b')
                gender=fmeta.read().split('gender=')[1].splitlines()[0].strip().lower()
                if gender=='male':
                    stuff="himself"
                elif gender=='female':
                    stuff="herself"
                else:
                    stuff="itself"
            except:
                stuff="itself"
        if stuff.lower() == 'me':
            stuff=msg.nick
        if stuff.split(' ',1)[0].lower()=="--add" or stuff.split(' ',1)[0].lower()=="add":
            stuff=stuff.split(' ',1)[1]
            f.write(stuff + "\n")
            irc.reply(format("puts %s away for a special occasion.  (#%s)",stuff, str(len(l)+1) ), action=True)
        elif stuff.split(' ',1)[0].lower()=="--plain":
            t = utils.str.normalizeWhitespace(t)
            irc.reply(t)
        elif stuff.split(' ',1)[0].lower()=="--plain2":
            if stuff.split(' ',1)[1]:
                stuff=stuff.split(' ',1)[1]
                irc.reply(format("slaps %s",stuff) +".", action=True)
        elif stuff.split(' ',1)[0].lower()=="list" or stuff.split(' ',1)[0].lower()=="--list":
            irc.reply("Yo dawg.  I herd you like slaplists, so we put a slap in your list so you get slapped while you list.", prefixNick=False)
            irc.reply(format("slaps %s around a bit with SpiderDave's slaplist",msg.nick) +".", action=True)
        elif stuff.split(' ',1)[0].lower()=="--setgender":
            if not capability(msg, 'owner'):
                irc.error("Only my owner can make me do that.  It's a painful process you know!")
                return
            stuff=stuff.split(' ',1)[1]
            stuff=stuff.strip().lower()
            if stuff not in self.validgenders:
                irc.error('Error: valid genders are ' + '/'.join(self.validgenders) + '.')
                return
            fmeta=open('%sbot_meta.txt' % self.pluginpath, 'w+b') #wipes file
            fmeta.write('gender=' + stuff + "\n")
            irc.reply("Gender set to %s" % stuff)
        else:
            irc.reply(format("slaps %s around a bit with ",stuff) + t +".", action=True)
    slap = wrap(slap, [additional('text')])

    # **********************************************************************
    def attack( self, irc, msg, args, stuff ):
        """ [[--]add <attack>]|[<someone>]

        Attacks <someone> with a random message.  When adding attacks, use _ in place of the nick.  Ex. "Attack add bitch-slaps _".
        """
        f=open('%sattack.txt' % self.pluginpath, 'a+b')
        l=open('%sattack.txt' % self.pluginpath, 'a+b').readlines()
        t=l[random.randint(0,len(l)-1)]
        t = t.replace("\'", "'").replace("\r", "").replace("\n", "")
        if not stuff:
            stuff="someone"
        if (stuff.lower() == irc.nick.lower()) or (stuff.lower() == 'yourself'):
            try:
                fmeta=open('%sbot_meta.txt' % self.pluginpath, 'a+b')
                gender=fmeta.read().split('gender=')[1].splitlines()[0].strip().lower()
                if gender=='male':
                    stuff="himself"
                elif gender=='female':
                    stuff="herself"
                else:
                    stuff="itself"
            except:
                stuff="itself"
        if stuff.lower() == 'me':
            stuff=msgs.nick
        if stuff.split(' ',1)[0].lower()=="--add" or stuff.split(' ',1)[0].lower()=="add":
            stuff=stuff.split(' ',1)[1]
            t=stuff
            if '_' not in stuff:
                irc.reply("You must have a _ to use as a target ex: attack add punches _ in the solar plexus")
                return
            if t.endswith('.'):
                t=t[:-1]
            f.write(t + "\n")
            irc.reply(format("Attack #%s added.",str(len(l)+1) ))
        elif stuff.split(' ',1)[0].lower()=="--plain":
            t = utils.str.normalizeWhitespace(t).replace('_',stuff)
            t=t.replace("s's","s'")
            
            irc.reply(t)
        elif stuff.split(' ',1)[0].lower()=="list" or stuff.split(' ',1)[0].lower()=="--list":
            irc.reply("Allow me to demonstrate:", prefixNick=False)
            irc.reply(t.replace('_',msgs.nick) + "... Twice.", action=True)
        elif stuff.split(' ',1)[0].lower()=="--setgender":
            if not capability(msg, 'owner'):
                irc.error("Only my owner can make me do that.  It's a painful process you know!")
                return
            stuff=stuff.split(' ',1)[1]
            stuff=stuff.strip().lower()
            if stuff not in self.validgenders:
                irc.error('Error: valid genders are ' + '/'.join(self.validgenders) + '.')
                return
            fmeta=open('%sbot_meta.txt' % self.pluginpath, 'w+b') #wipes file
            fmeta.write('gender=' + stuff + "\n")
            irc.reply("Gender set to %s" % stuff)
        else:
            t=t.replace('_',stuff) + "."
            t=t.replace("s's","s'")
            if t.endswith('..'):
                t=t[:-1]
            irc.reply(t, action=True)
#    attack = wrap(attack, [additional('text')])
    # **********************************************************************

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

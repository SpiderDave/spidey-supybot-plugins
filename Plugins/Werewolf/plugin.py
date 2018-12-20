###
# Copyright (c) 2010, Julian Aloofi
# All rights reserved.
#
#    This file is part of supybot-werewolf.
#
#    supybot-werewolf is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    supybot-werewolf is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with supybot-werewolf.  If not, see <http://www.gnu.org/licenses/>.
#
#
#
###
###
# ****************************** Heavily modified by SpiderDave ***********************
###

import json

import supybot.world as world
import supybot.utils as utils
import supybot.conf as conf
import supybot.ircdb as ircdb
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import random, threading, pickle, os

import supybot.irclib as irclib
import importlib

try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
    _ = PluginInternationalization('Werewolf')
except:
    _, PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x, lambda x:x

from . import site_settings as site
# I don't remember the exact reasoning here, but it was some dumb cache workaround a particular case.
site=importlib.reload(site)

try:
    from . import werewolf_db as db
except:
    db=False

#from . import werewolf_db as db

#TODO: don't allow to kill other werewolves via config value
#TODO: tellwolves to communicate with all wolves
#TODO: private discussion votekill

class WerewolfDB(plugins.ChannelUserDB):
    def serialize(self, v):
        return [json.dumps(v)]

    def deserialize(self, channel, id, L):
        if len(L) != 1:
            raise ValueError
        return json.loads(L[0])

@internationalizeDocstring
class Werewolf(callbacks.Plugin):
    """This plugin lets you play the werewolf game also known as mafia.
    To start a game use the 'startgame' command. Now the minimum number
    of players (default 4) needs to join the game with 'joingame'.
    You can use 'tellrules' to let the bot give users a link
    to the game rules.
    """
    threaded = True
    
    def __init__(self, irc):
        self.__parent = super(Werewolf, self)
        self.__parent.__init__(irc)


        filename = conf.supybot.directories.data.dirize('Werewolf.db')
        self.db = WerewolfDB(filename)
        world.flushers.append(self.db.flush)
        self._get_default_options()
        self._cleanup()
        self.irc = irc

    def die(self):
        if self.db.flush in world.flushers:
            world.flushers.remove(self.db.flush)
        self.db.close()
        self.__parent.die()
        
    def _preCheck(self, irc, msg, user):
        capability = self.registryValue('requireCapability')

#        try:
#            capability=self.registryValue('requireCapability')
#        except registry.NonExistentRegistryEntry:
#            conf.registerGlobalValue(conf.supybot.plugins.get(self.name), 'requireCapability', registry.String("admin", """Determines what capability (if any) is required to change game keys or other settings of another user."""))
        
        capability=self.registryValue('requireCapability')

        if capability:
            try:
                u = ircdb.users.getUser(msg.prefix)
            except KeyError:
                irc.errorNotRegistered(Raise=True)
            else:
                if u != user:
                    if not ircdb.checkCapability(msg.prefix, capability):
                        irc.errorNoCapability(capability, Raise=True)

    join_started = False
    game_started = False
    #includes all players
    players={}
    #who owns the current game?
    gameowner = ''
    
    #what phase are we currently in? 'morning', 'discussion' or 'night'?
    game_phase = ''
    #in which channel is the game running?
    gamechannel = ''
    #how many votes does a kill
    list_of_death = []
    #who voted yet?
    already_voted = []
    # a thread to move on
    move_on = False
    
    intro={}
    intro['seer'] = ("You are a seer. After every night you can find out "+
            "what the real identitiy of a player is. Try to keep your "+
            "own identity secret or the werewolves will most likely "+
            "kill you in the night. You can try to lead the discussion into "+
            "the right direction though. Apart from your abilities to "+
            "reveal other players identities you're a normal villager and will "+
            "only win if the villagers win.")
    
    intro['werewolf'] = ("You are a werewolf! Don't tell anybody! "+
            "You have to kill all villagers. Hide your identity in "+
            "the public votings and act like a normal villager. "+
            "In the night you will get an opportunity to kill villagers "+
            "together with other werewolves in a private voting. "+
             "Currently werewolves are: ")
    
    intro['villager'] = ("You are a villager. You will have to discuss "+
            "with the other villagers during the daytime and try to find "+
            "out who the werewolves are. After each discussion period "+
            "you and the other players will democratically select "+
            "a player who will be killed. Try to find out who the "+
            "werewolves are without making yourself suspect.")
    
    intro['hunter'] = ("You are a hunter. You will have to discuss "+
            "with the other villagers during the daytime and try to find "+
            "out who the werewolves are. After each discussion you and "+
            "the other players will select a player who will be killed. "+
            "Try to find out who the werewolves are without making yourself "+
            "suspect.  Your skill as a hunter will allow you to finish off "+
            "the werewolf if you are the last two remaining.")
    
    intro['sorcerer'] = ("You are a sorcerer, siding with the werewolves. "+
            "Each night, you may use your magic to find out if a player is "+
            "the seer or not.  The seer will not be able to tell you apart "+
            "from a normal villager. Try to aid the werewolves in their "+
            "feast, but be careful you don't become a victim yourself.  You "+
            "will only win if the werewolves win.")
    
    intro['apprenticeseer'] = ("You are an apprentice seer.  If the seer is "+
            "killed, you will become the new seer. Until then, you will vote "+
            "with the rest of the villagers and try to find out who the "+
            "werewolves are.")
    
    intro['prince'] = ("You are the prince. Your royal blood is a delicacy "+
            "to werewolves, so you've chosen to hide among the villagers.  "+
            "Try to find out who the werewolves are, but be careful not to "+
            "reveal your bloodline (Werewolves get an extra point for "+
            "killing the prince).  If you are chosen to be killed by the village, "+
            "your nobility will be revealed and save you one time.")
    
    intro['toughguy'] = ("You are a tough guy. During the day, you and the other "+
            "other villagers will try to find out who the werewolves are, and select "+
            "a player who will be killed. Try to find out who the "+
            "werewolves are without making yourself suspect.  Your strength allows "+
            "you to survive an extra day if attacked by werewolves at night.")
    
    intro['cobbler'] = ("You are a cobbler. You hate your job, and your miserable "+
            "life. This werewolf situation may give you a means to release yourself "+
            "from this mortal coil.  You will only win points if you are killed (the "+
            "game will continue afterwards).")
    
    intro['lycan'] = ("You are a lycan. You have werewolf blood in your veins, though "+
            "you are not a werewolf, and want to live a normal life. Vote with the rest "+
            "of the villagers and try to find out who the werewolves are. If you're "+
            "revealed by the seer, you will show as a werewolf.")
    
    intro['priest'] = ("You are a priest. You will have to discuss "+
            "with the other villagers during the daytime and try to find "+
            "out who the werewolves are. Once during the game, you may choose a player "+
            "to protect with the '.protect' command.  The next attempt to kill that player will fail.")
    
    intro['diseased'] = ("You are a diseased villager. You will have to discuss "+
            "with the other villagers during the daytime and try to find "+
            "out who the werewolves are. If you are killed by wolves, they will "+
            "skip feeding the next night.")
    
    def _cleanup(self):
        """cleans all variables up"""
        self.join_started = False
        self.game_started = False
        self.players={}
        self.gameowner = ""
        self.game_phase = ""
        self.gamechannel = ""
        self.list_of_death = []
        self.already_voted = []
        try:
            self.move_on.cancel()
        except:
            pass
        self.move_on = False
    
    def _getirc(self, irc):
        return irc
    
    def _nickToHostmask(self, nick):
        return self.irc.state.nickToHostmask(nick)
    
    def _write_scores(self):
        channel=self.gamechannel
        for player in self.players:
            role=self.players[player]['class']
            if role=='cobbler':
                points=0
            if role=='werewolf':
                points=3
                if self.players[player].get('killed_prince'): points+=1
            if role=='sorcerer':
                points=2
            if role=='hunter':
                points=1
                if len(self.players)==1: points=3
            else:
                points=0
            
            self.updatescore(player, points, 1, channel)
        
    def _read_options(self, channel):
        f="%s%swerewolf_%s.options" % (conf.supybot.directories.data(),os.sep, channel)
        if os.path.isfile(f):
            inputfile = open(f, "rb")
            self.channeloptions = pickle.load(inputfile)
            inputfile.close()
        else:
            self._get_default_options()

    def _write_options(self, channel):
        f="%s%swerewolf_%s.options" % (conf.supybot.directories.data(),os.sep, channel)
        outputfile = open(f, "wb")
        pickle.dump(self.channeloptions, outputfile)
        outputfile.close()

    def _get_default_options(self):
        self.channeloptions = {}
        self.channeloptions['show_seer_result']=False
        self.channeloptions['moderate']=False
        self.channeloptions['voice']=True
        self.channeloptions['self_vote']=False
        self.channeloptions['allow_game']=False
        self.channeloptions['anon_vote']=False
        self.channeloptions['use_queue']=True
        self.channeloptions['no_owner']=False
        self.channeloptions['enable_sorcerer']=False
        self.channeloptions['enable_hunter']=False
        self.channeloptions['enable_prince']=False
        self.channeloptions['enable_toughguy']=False
        self.channeloptions['enable_apprenticeseer']=False
        self.channeloptions['enable_cobbler']=False
        self.channeloptions['enable_lycan']=False
        self.channeloptions['enable_priest']=False
        self.channeloptions['enable_diseased']=False
        self.channeloptions['debug']=False
        self.channeloptions['basic']=False


    def listscores(self, irc, msg, args):
        """takes no arguments
        
        Lists the werewolf game scores"""
        irc.reply('%s' % site.score_url)
    listscores = wrap(listscores)
    
    def startgame(self, irc, msg, args):
        """takes no arguments
        
        Starts the game and allows other players to join with 'joingame'.
        """
        nick=msg.nick
        try:
            self._read_options(msg.args[0])
        except:
            pass
        if 'allow_game' not in list(self.channeloptions.keys()):
            self.channeloptions['allow_game']=False

        if not db:
            self.reply(irc, 'Error: werewolf database was not loaded.')
            return

        if self.channeloptions['allow_game']==False:
            self.reply(irc, 'Error: allow_game=False')
            return
        if not self.join_started and not self.game_started:
            #clear the player list
            self.players={}
            #remember the game channel
            self.gamechannel = msg.args[0]
            self.gameid=random.randint(1, 1000000)
            self.reply(irc,
            "A new game of werewolf has started! To join use "+
            "the 'joingame' command.", prefixNick=False, private=False,
            to=self.gamechannel)
            # add command caller to the player list
            self.add_player(nick)
            if self.channeloptions['no_owner']==False:
                # make him game owner
                self.gameowner = nick
                self.reply(irc, "%s: " % nick +"You are the game owner now. "+
                "Use 'begingame' once enough players have joined the game to "+
                "start the game", prefixNick=False)
            else:
                # no game owner
                self.gameowner = ''
                self.reply(irc, "Use 'begingame' once enough players have joined the game to "+
                "start the game", prefixNick=False)
            try:
                self._voice(irc, [nick])
            except:
                pass
            self.reply(irc, "added " + nick + " to the player list", action=True
            ,private=False, to=self.gamechannel)
            #join_started is there to track the current state of joining
            self.join_started = True
        else:
            self.reply(irc, "A game has already been started or is running!")

    startgame = wrap(startgame, ['public'])

    def leavegame(self, irc, msg, args, text):
        """takes no arguments
        
        allows the caller to leave the game"""
        nick=[p for p in self.players if self.players[p].get('kicked')]
        if nick:
            nick=nick[0]
        else:
            nick=msg.nick
            if text and self.channeloptions['debug']:
                nick=text
        if not self.join_started and not self.game_started:
            self.reply(irc, 'There is no game to leave')
            return
        if nick in self.players:
            try:
                self._devoice(irc, [nick])
            except:
                pass
            if nick==self.gameowner:
                self.gameowner=""
            #if in joining phase
            if not self.game_started and self.join_started:
                #self.players.remove(msg.nick)
                if nick in self.players:
                    del self.players[nick]
                self.reply(irc, nick+" has left the game.",
                to=self.gamechannel, prefixNick=False)
                if len(self.players) ==0:
                    self.reply(irc, "There are no more players.  The game has been cancelled.",
                    to=self.gamechannel, prefixNick=False)
                    try:
                        self._unmoderate(irc, msg, args)
                    except:
                        pass
                    self._cleanup()
                return
            
            self.reply(irc, "%s has left the game.  He was a %s." % (nick,self.players[nick]['class']),
            to=self.gamechannel, prefixNick=False)
            del self.players[nick]
            self._check_continue(irc, msg, args)
    leavegame=wrap(leavegame, [optional('something')])
    
    # "You're not channel operator"
#    def do482(self, irc, msg):
#        self.log.info('do482!!!!!')
    
    def doError(self, msg):
        self.log.info('doError: %s' % msg.args[0])
        irc.noReply()
    
    def doPart(self, irc, msg):
        if msg.args[0] == self.gamechannel:
            if msg.nick in self.players:
                self.leavegame(irc, msg, [])

    def doKick(self, irc, msg):
        if msg.args[0] == self.gamechannel:
            (channel, users) = msg.args[:2]
            users=users.split(',')
            for u in users:
                if u in self.players:
                    self.players[u]['kicked']=True # leavegame will find the kicked user
                    self.leavegame(irc, msg, [])

    def doNick(self, irc, msg):
        if msg.nick in self.players:
            oldNick = msg.nick
            newNick = msg.args[0]
            self.players[newNick]=self.players[oldNick]
            del self.players[oldNick]
            if self.gameowner==oldNick: self.gameowner=newNick
            if oldNick in self.list_of_death:
                self.list_of_death[self.list_of_death.index(oldNick)]=newNick
            if oldNick in self.already_voted:
                self.already_voted[self.already_voted.index(oldNick)]=newNick

    def doQuit(self, irc, msg):
        if msg.nick in self.players:
            self.leavegame(irc, msg, [])
    
    def tellrules(self, irc, msg, args):
        """takes no arguments
        
        Tells the caller the rules"""
        self.reply(irc, 
        "You can find the rules at http://www.eblong.com/zarf/werewolf.html")
        
    tellrules = wrap(tellrules)
    
    def joingame(self, irc, msg, args, text, debugopt):
        """takes no arguments
        
        Allows players to join the game."""
        nick=msg.nick
        fake=False
        fakerole=False
        if text and self.channeloptions['debug']:
            fake=True
            nick=text
            if debugopt:
                debugopt=debugopt.replace(' =','=').replace('= ','=')
                debugopt=debugopt.split()
                for item in debugopt:
                    if '=' in item:
                        keyword=item.split('=')[0].lower()
                        data=item.split('=')[1]
                        if keyword=='role': fakerole=data.lower()

        if not self.game_started and self.join_started:
            if not nick in self.players:
                #add command caller to the player list
                self.add_player(nick, fake)
                if fakerole:
                    self.players[nick]['setclass']=fakerole
                try:
                    self._voice(irc, [nick])
                except:
                    pass
                #and tell that to the IRC
                self.reply(irc, "added " + nick + " to the player list"
                ,action=True, private=False, to=self.gamechannel)
                 
            else:
                self.reply(irc, "You already joined the game!")
        elif self.game_started and not self.join_started:
            self.reply(irc, "The game already started. Please wait until "+
            "a new round starts")
        else:
            self.reply(irc, "Nobody started a round yet. Use the 'startgame' "+
            "command to start a new round!")
    
    joingame = wrap(joingame, ['public', optional('something'), optional('something')])
    
    def listplayers(self, irc, msg, args):
        """takes no arguments
        
        Lists all players still playing"""
        if self.game_started or self.join_started:
            msgstring = "Current players (%s): %s." % (len(self.players), self._get_playerlist())
            self.reply(irc, msgstring)
        else:
            self.reply(irc, 'Current players: none.  Use .startgame to start a game.')
        
    listplayers = wrap(listplayers)
    
    def _get_playerlist(self, show_roles=False):
        if show_roles:
            txt=list(map(str, self.players))
            txt=[p + ' (' + self.players[p]['class'] + ')' for p in self.players]
            txt=", ".join(txt)
            txt=txt.replace('toughguy', 'tough guy')
            txt=txt.replace('apprenticeseer', 'apprentice seer')
            return txt
        return ", ".join(map(str, self.players))


    def whatami(self, irc, msg, args, text):
        """takes no arguments
        
        Tells the caller what he is."""
        nick=msg.nick
        if text and self.channeloptions['debug']:
            nick=text

        if not nick in self.players:
            self.reply(irc, "You're not participating in the game.")
            return
        if not self.game_started:
            self.reply(irc, "Someone needs to start a game using 'startgame' first")
            return True

        c = self.players[nick]['class']
        
        if c=='werewolf':
            wolflist=[p for p in self.players if self.players[p]['class']=='werewolf']
            self.reply(irc, self.intro[c]+
            " ".join(map(str, wolflist)), private=True, to=msg.nick)
        else:
            self.reply(irc, self.intro[c], private=True, to=msg.nick)

    whatami = wrap(whatami, [optional('text')])
    
    def begingame(self, irc, msg, args, text):
        """takes no arguments
        
        Begins the round after a 'startgame'"""
        threaded=True

        nick=msg.nick
        if text and self.channeloptions['debug']:
            nick=text

        if not self.join_started and not self.game_started:
            self.reply(irc, "You need to start a game using 'startgame' first")
            return

        if self.gamechannel:
            if msg.args[0] != self.gamechannel:
                if self.game_started:
                    self.reply(irc, 'Game already started in another channel!')
                else:
                    self.reply(irc, 'This command must be used in the same channel the game was started in.')
                return
        if self.game_started:
            self.reply(irc, "Game already started!")
            return

        if self.gameowner:
            # if gameowner is blank then the owner probably left after
            # creating the game. In that case, just let anyone start it.
            if nick != self.gameowner:
                self.reply(irc, "You haven't started the game. Please ask " + 
                self.gameowner +
                " to start the game")
                return

        if len(self.players) < 3:
            self.reply(irc, "There are not enough players to start the game. "+
            "You need at least 3 players to start the game")
            return
        else:
            try:
                self._moderate(irc, msg, args)
            except:
                pass
            #join phase is over
            self.join_started = False
            self.game_started = True
            #tell everyone the game is starting
            self.reply(irc, ircutils.bold("Night is falling, "+
            "and the game is starting! "+
            "I am telling everyone their roles now. ")
            +"Whenever I'm asking you to do something "+
            ircutils.bold("*privately*")+" /msg me "+
            "to issue the command.",
            prefixNick=False, private=False, to=self.gamechannel)
            ##assign the roles##
            
            # 3-7   players: 1 seer, 1 wolf
            # 8-10  players: 1 seer, 2 wolves
            # 11-14 players: 1 seer, 3 wolves
            # 15-19 players: 1 seer, 4 wolves

            for p in self.players:
                if self.players[p].get('setclass'):
                    self.players[p]['class']=self.players[p]['setclass']

            # Wolves
            if len(self.players) < 7:
                self.choose_role('werewolf', 1)
            elif len(self.players) < 11:
                self.choose_role('werewolf', 2)
            elif len(self.players) < 15:
                self.choose_role('werewolf', 3)
            elif len(self.players) < 20:
                self.choose_role('werewolf', 4)

            # Seer
            self.choose_role('seer', 1)
            # Make sure there's at least x normal villagers
            self.choose_role('villager', 2)

            if self.channeloptions['basic']:
                # basic means no special roles
                pass
            else:

                specialroles=['hunter','sorcerer','prince','toughguy','apprenticeseer','cobbler','lycan','priest','diseased']
                if len(self.players) < 11:
                    # limit apprentice seer to games of 11 or more (3 wolves)
                    specialroles=[r for r in specialroles if r != 'apprenticeseer']

                specialroles=[r for r in specialroles if self.channeloptions['enable_'+r]]
                random.shuffle(specialroles)
                
                for r in specialroles:
                    self.choose_role(r,1)

            # make the rest villagers
            self.choose_role('villager')

            #tell everyone what he is
            for player in self.players:
                c=self.players[player]['class']
                if c=='werewolf':
                    wolflist=[p for p in self.players if self.players[p]['class']=='werewolf']
                    self.reply(irc, self.intro['werewolf']+
                    " ".join(map(str, wolflist)), private=True, to=player, fast=True)
                else:
                    self.reply(irc, self.intro[c], private=True, to=player, fast=True)

            self.reply(irc, "All players know their roles now, and the game has started!",
            prefixNick=False, private=False, to=self.gamechannel, fast=True)
            self.reply(irc, "Welcome to a new round of werewolf! "
            +"This game is a "+
            "game of accusations, lying, bluffing, second-guessing, "+
            "assassination, and mob hysteria. All players seem to be normal "+
            "villagers, but we have "+self.list_roles()+'.  '+
            "Try to find out who the werewolves are, or get eaten in the "+
            "night.", to=self.gamechannel, prefixNick=False)
            self._phase_morning(irc, msg, args)

    begingame = wrap(begingame, ['public', optional('text')])

    def _game_over(self, irc, msg, args):
        try:
            self._devoice(irc, self.players)
        except:
            pass
        gameovertxt='The game is over!'
        if self.count_class('werewolf') == 0:
            for player in self.players:
                c=self.players[player]['class']
                if c=='sorcerer':
                    self.players[player]['class']='dead_'+c
            self.remove_dead()
            gameovertxt+=' The villagers have won!'
        else:
            hunterwin=0
            for player in self.players:
                c=self.players[player]['class']
                if c=='villager':
                    self.players[player]['class']='dead_'+c
                elif c=='seer':
                    self.players[player]['class']='dead_'+c
                elif c=='hunter':
                    if self.count_class('werewolf')==1 and self.count_class('hunter')==1:
                        self.players[self.list_from_class('werewolf')[0]]['class']='dead_werewolf'
                        hunterwin=1
                    else:
                        self.players[player]['class']='dead_'+c
                elif c=='werewolf':
                    pass
                elif c=='sorcerer':
                    pass
                else:
                    self.players[player]['class']='dead_'+c
            self.remove_dead()
            if hunterwin==1:
                gameovertxt+=' The hunter has killed the werewolf!  The hunter has won!'
            else:
                gameovertxt+=' The werewolves have won!'

        self.reply(irc, gameovertxt, to=self.gamechannel,
        prefixNick=False, fast=True)

        self.reply(irc, "Players still alive: " + self._get_playerlist(show_roles=True) + '.',
        to=self.gamechannel, prefixNick=False, fast=True)
        self._write_scores()
        try:
            self._unmoderate(irc, msg, args)
        except:
            pass
        self._cleanup()
        
    def _phase_discuss(self, irc, msg, args):
        self.game_phase = "discussion"
        try:
            self.move_on.cancel()
        except:
            pass
        self.move_on = False
        self.reply(irc, "It is time to discuss now! "+
        "Who could the werewolves be? If you have a suspicion, use the "+
        ircutils.bold("'votekill'")+
        " command to vote for the death of your suspect",
        to=self.gamechannel, private=False)
        self.list_of_death = []
        self.already_voted = []
        
    def votes(self, irc, msg, args):
        """<takes no arguments
        
        Show current votes for the werewolf game.
        """
        nick=msg.nick
        if not nick in self.players:
            self.reply(irc, "You're not participating in the game.")
            return
        if not self.game_started:
            self.reply(irc, "Someone needs to start a game using 'startgame' first")
            return True
        if self.game_phase != "discussion":
            self.reply(irc, "This command can't be used right now")
            return

        tally= ''
        if not self.list_of_death:
            self.reply(irc, "Votes: none.")
            return
        lodplayers=[p for p in self.list_of_death if p in self.players]
        for player in lodplayers:
            tally+='%s(%s) ' % (player, self.list_of_death[self.list_of_death.index(player)+1])
        
        self.reply(irc, "Votes: %s" % tally,
        to=self.gamechannel, private=False)
        
    votes = wrap(votes)

    def votekill(self, irc, msg, args, nickname, text):
        """<nickname>
        
        Votes to kill <nickname>"""
        nick=msg.nick
        channel=msg.args[0]
        if text and self.channeloptions['debug']:
            nick=text
        if not nick in self.players:
            self.reply(irc, "You're not participating in the game.")
            return
        if not self.game_started:
            self.reply(irc, "Someone needs to start a game using 'startgame' first")
            return True

        if self.channeloptions['anon_vote']==True and msg.args[0] ==self.gamechannel:
            self.reply(irc, 'Votes must be anonymous.')
            return
        
        if self.game_phase != "discussion" and self.game_phase != "night":
            self.reply(irc, "This command can't be used right now")
            return
    
        nickname=self.fixnick(nickname) # For case-insensitivity
        if ircutils.strEqual(nickname.lower(), irc.nick.lower()):
            self.reply(irc, "I'm narrating this story!")
            return

        if self.channeloptions['self_vote']==False:
            if nick.lower()==nickname.lower():
                self.reply(irc, "You cannot vote for yourself.")
                return
        
        if nick in self.already_voted:
            self.reply(irc, "You already gave a vote for the current voting")
            return
        if not nickname in self.players:
            self.reply(irc, nickname+" is not participating in this round")
            return
        #discussion mode:
        if self.game_phase == "discussion":
            self.already_voted.append(nick)
            if not nickname in self.list_of_death:
                self.list_of_death.append(nickname)
                self.list_of_death.append(1)
            else:
                self.list_of_death[self.list_of_death.index(nickname)+1] =(
                self.list_of_death[self.list_of_death.index(nickname)+1] + 1)
            if len(self.already_voted) == len(self.players):
                self._phase_night(irc, msg, args)
                return
            else:
                n_votes_missing = len(self.players)-len(self.already_voted)
                
                vote_message=nick+" voted to kill "+nickname+'.  '
                if self.channeloptions['anon_vote']==True:
                    vote_message='Someone has voted to kill '+nickname+'.  '
                if n_votes_missing>3 or self.channeloptions['anon_vote']==True:
                    self.reply(irc, vote_message +"There still are "+str(len(self.players)-
                    len(self.already_voted))+" votes missing.",
                     to=self.gamechannel,
                    prefixNick=False, fast=True)
                else:
                    self.reply(irc, vote_message +"There still are "+str(len(self.players)-
                    len(self.already_voted))+" votes missing ("+
                    ', '.join([p for p in self.players if p not in self.already_voted])+')',
                     to=self.gamechannel,
                    prefixNick=False, fast=True)

                lod=[self.list_of_death[self.list_of_death.index(p)+1] for p in self.list_of_death if p in self.players]
                lod2=dict([[p,0] for p in self.players])
                for p in self.players:
                    if p in lod:
                        lod2[p]=lod[lod.index(p)+1]
                
                enoughvotes=True
                missingvotes= len(self.players)-len(self.already_voted)
                nothighest=[p for p in lod if p !=max(lod+[0])]
                
                if len(lod)-len(nothighest)>1:
                    # there is a tie for the most votes, not enough to skip ahead.
                    enoughvotes=False
                if max(nothighest+[0])+missingvotes >= max(lod+[0]):
                    # If everyone votes for the next highest,
                    # it will tie or win.  Not enough to skip ahead.
                    enoughvotes=False

                if enoughvotes==True:
                    self.reply(irc, "There is a clear majority of votes.", to=self.gamechannel,
                    private=False, prefixNick=False, fast=True)
                    self._phase_night(irc, msg, args)
                    return
                else:
                    # majority of votes, but not enough to skip the rest.
                    if len(self.players)/2.0 < len(self.already_voted) and (self.move_on == False):
                        self.reply(irc, "The majority of votes are in! "+
                        "You have two minutes left to vote!", to=self.gamechannel,
                        private=False, prefixNick=False)
                        self.move_on = threading.Timer(120, self._vote_countdown,
                        [irc, msg, args])
                        self.move_on.start()
                        return
        #night mode:
        if self.game_phase == "night":
            if self.players[nick]['class'] !='werewolf' or ('#' in channel):
                return
            self.already_voted.append(nick)
            if not nickname in self.list_of_death:
                self.list_of_death.append(nickname)
                self.list_of_death.append(1)
            else:
                self.list_of_death[self.list_of_death.index(nickname)+1] =(
                self.list_of_death[self.list_of_death.index(nickname)+1] + 1)
            for wolf in self.list_from_class('werewolf'):
                if msg.nick != wolf: 
                    self.reply(irc, ircutils.bold(nick+" voted to kill "
                    +nickname+"."), to=wolf, private=True, fast=True)
            if len(self.already_voted) == self.count_class('werewolf'):
                self._wolf_poll_finished(irc, msg, args)
                return
                     
    votekill = wrap(votekill, ['something', optional('something')])
    
    def _vote_countdown(self, irc, msg, args):
        #to be used as threaded function
        if self.game_phase == "discussion":
            self._phase_night(irc, msg, args)

    def _seer_countdown(self, irc, msg, args):
        #to be used as threaded function
        if self.game_phase == "morning":
            self._phase_discuss(irc, msg, args)
            
    def _wolf_poll_finished(self, irc, msg, args):
        if self.game_phase=="night":
            self.game_phase="nightannounce"
            try:
                self.move_on.cancel()
            except:
                pass
            self.move_on = False
            self.reply(irc, "All werewolf votes are in!"
            ,to=self.gamechannel, prefixNick=False, fast=True)
            if len(self.list_of_death) > 0:
                self._kill_someone_now(irc, msg, args)
            
            self.list_of_death = []
            self.already_voted = []
            
            self._phase_morning(irc, msg, args)
    
    def _phase_night(self, irc, msg, args):
        self.game_phase="voteannounce"
        if self.move_on != False:
            try:
                self.move_on.cancel()
            except:
                pass
            self.move_on = False
        self.reply(irc, "Voting has finished!"
        ,to=self.gamechannel, prefixNick=False, fast=True)
        self._kill_someone_now(irc, msg, args)
        self.list_of_death = []
        self.already_voted = []
        
        for player in self.players:
            if self.players[player].get('wounded'):
                txt="%s has died from werewolf wounds.  %s was a tough guy." % (player, player)
                self.reply(irc, txt, to=self.gamechannel, prefixNick=False)
                self.players[player]['class']='dead_'+self.players[player]['class']
                try:
                    self._devoice(irc, [player])
                except:
                    pass
        self.remove_dead()


        if self._check_continue(irc, msg, args) == True:
            return
        
        self.game_phase="night"

        if self.players[self.list_from_class('werewolf')[0]].get('sick')==True:
            for wolf in self.list_from_class('werewolf'):
                self.players[wolf]['sick']=False
                self.reply(irc, "You are ill from the last feeding, and cannot kill tonight.", private=True, to=wolf, fast=True)
            self.list_of_death = []
            self.already_voted = []
            self.reply(irc, "Night is falling, but the wolves are recovering from a case of indigestion and will not feed tonight.  The village is safe... for now.", to=self.gamechannel, prefixNick=False, fast=True)
            self._phase_morning(irc, msg, args)
            return
        else:
            self.reply(irc, "Night is falling! Watch out, because the werewolves "+
            "have the opportunity to kill one of you now! ", to=self.gamechannel,
            prefixNick=False, private=False)

            
        for wolf in self.list_from_class('werewolf'):
            self.reply(irc, "You and the other wolves "+
            "can kill someone now. Vote to kill someone by "+
            ircutils.bold("*privately*")+" telling me your victim with "+
            "the 'votekill' command. You only have "+
            "two minutes.", private=True, to=wolf)
            
        if self.move_on == False:
            self.move_on = threading.Timer(120, self._wolf_poll_finished,
            [irc, msg, args])
            self.move_on.start()
    
    def _kill_someone_now(self, irc, msg, args):
        highestcount = 0
        deathplayer = ""
        is_draw = False
        for item in self.list_of_death:
            if isinstance(item, int):
                if item > highestcount:
                    highestcount = item
                    deathplayer = (
                    self.list_of_death[self.list_of_death.index(item)-1])
                    is_draw = False
                elif item == highestcount:
                    is_draw = True
        if self.game_phase == "voteannounce":
            if is_draw == True:
                self.reply(irc, "There was a draw in the election! Nobody will be "
                "killed.",
                to=self.gamechannel, prefixNick=False, fast=True)
                return
            else:
                self.reply(irc, "The villagers have "+
                ircutils.bold("decided to kill "+deathplayer)+
                " with "+str(highestcount)+" votes.", to=self.gamechannel, 
                prefixNick = False, fast=True)
                if not deathplayer in self.players:
                    self.reply(irc, deathplayer+" left before the "+
                    "election finished.",
                    to=self.gamechannel, prefixNick=False, fast=True)
                    return
        elif self.game_phase == "nightannounce":
            if is_draw == True:
                self.reply(irc, "The werewolves couldn't decide on a player to kill"+
                ". Everyone is still alive.",to=self.gamechannel,
                prefixNick=False, fast=True)
                return
            else:
                self.reply(irc, "The werewolves have "+
                ircutils.bold("decided to kill "+deathplayer)+
                " with "+str(highestcount)+" votes.", to=self.gamechannel, 
                prefixNick = False, fast=True)
                if not deathplayer in self.players:
                    self.reply(irc, deathplayer+" ran away before the "+
                    "werewolves could get him.",
                    to=self.gamechannel, prefixNick=False, fast=True)
                    return

        if self.players[deathplayer].get('protected') == True:
            self.players[deathplayer]['protected']=False
            self.reply(irc, ircutils.bold(deathplayer+" has been spared with the priest's blessing!"), to=self.gamechannel,
            prefixNick=False, fast=True)
            self.list_of_death = []
            self.already_voted = []
            return

        c=self.players[deathplayer]['class']
        if c=='villager':
            self.reply(irc, ircutils.bold(deathplayer+" was a villager."), to=self.gamechannel,
            prefixNick=False, fast=True)
        elif c=='werewolf':
            self.reply(irc, "Congratulations! "+ircutils.bold(deathplayer+" was a werewolf!"),
             to=self.gamechannel,
            prefixNick=False, fast=True)
        elif c=='seer':
            messagetxt="Oh no! "+ircutils.bold(deathplayer+" was the seer!")
            if self.count_class('apprenticeseer')>0:
                messagetxt+="  The apprentice seer is now the seer."
                newseer=self.list_from_class('apprenticeseer')[0]
                self.players[newseer]['class']='seer'
            self.reply(irc, messagetxt, to=self.gamechannel, prefixNick=False, fast=True)
        elif c=='apprenticeseer':
            self.reply(irc, ircutils.bold(deathplayer+" was the apprentice seer!"), 
            to=self.gamechannel,
            prefixNick=False, fast=True)
        elif c=='sorcerer':
            self.reply(irc, ircutils.bold(deathplayer+" was a %s!" % c),
             to=self.gamechannel,
            prefixNick=False, fast=True)
        elif c=='prince':
            if self.game_phase == "nightannounce":
                self.reply(irc, ircutils.bold("%s was a %s!" % (deathplayer, c)),
                 to=self.gamechannel,
                prefixNick=False, fast=True)
                for wolf in self.list_from_class('werewolf'):
                    self.players[wolf]['killed_prince']=True
            else:
                self.reply(irc, ircutils.bold(deathplayer+" is the prince, and will be spared!"), 
                to=self.gamechannel,
                prefixNick=False, fast=True)
                self.list_of_death = []
                self.already_voted = []
                return
        elif c=='toughguy':
            if self.game_phase == "nightannounce":
                self.reply(irc, ircutils.bold(deathplayer+" managed to fight off the werewolves")+", sustaining heavy wounds.", 
                to=self.gamechannel,
                prefixNick=False, fast=True)
                self.players[deathplayer]['class']='villager'
                self.players[deathplayer]['wounded']=True
                self.list_of_death = []
                self.already_voted = []
                return
            else:
                self.reply(irc, ""+ircutils.bold("%s was a tough guy." % deathplayer),
                 to=self.gamechannel,
                prefixNick=False, fast=True)
        elif c=='cobbler':
            self.reply(irc, ircutils.bold(deathplayer+" was a %s.  He seemed oddly content." % c),
             to=self.gamechannel,
            prefixNick=False, fast=True)

        elif c=='diseased':
            self.reply(irc, ircutils.bold(deathplayer+" was %s!" % c),
             to=self.gamechannel,
            prefixNick=False, fast=True)
            if self.game_phase == "nightannounce":
                for wolf in self.list_from_class('werewolf'):
                    self.players[wolf]['sick']=True
        else:
            self.reply(irc, ""+ircutils.bold("%s was a %s." % (deathplayer, c)),
             to=self.gamechannel,
            prefixNick=False, fast=True)
        if c=='cobbler':
            messagetxt="Congratulations! You are dead now.  Please do not attempt to communicate with the living."
        else:
            messagetxt="You are dead now, sorry.  Please do not attempt to communicate with the living."
        self.reply(irc, messagetxt, to=deathplayer, private=True, fast=True)
        try:
            self._devoice(irc, [deathplayer])
        except:
            pass
        self.players[deathplayer]['class']='dead_'+self.players[deathplayer]['class']
        self.remove_dead()
        self.list_of_death = []
        self.already_voted = []


    def _check_start(self, irc, msg, args):
        """checks whether a user is allowed to issue commands"""
        if not msg.nick in self.players:
            self.reply(irc, "You're not participating in the game.")
            return True
        if not self.game_started:
            self.reply(irc, "Someone needs to start a game using 'startgame' first")
            return True
        return False
        
    def _phase_morning(self, irc, msg, args):
        self.game_phase = "morning"
        #just to be sure.. :D
        self.list_of_death = []
        self.already_voted = []
        l=self.list_from_class('seer')+self.list_from_class('sorcerer')
        for player in l:
            self.players[player]['used_reveal']=False
        seerval = 0
        if self.count_class('seer')>0:
            seerval = 1
        self._check_continue(irc, msg, args)
        if seerval == 0:
            self.reply(irc, "The sun is rising and a new day "
            +"begins. "+
            "Unfortunately the seer is dead.",
            prefixNick=False, to=self.gamechannel)
            self._phase_discuss(irc, msg, args)
            return
        else:
            self.move_on = threading.Timer(90, 
            self._seer_countdown, [irc, msg, args])
            self.move_on.start()

        if self.count_class('sorcerer')>0:
            c='sorcerer'
            self.reply(irc, "The sun is rising and a new day begins. The seer has "+
            "the opportunity to reveal another players identity now.  The "+
            "%s may also use magic to check if a player is the seer." % c, 
            prefixNick=False, to=self.gamechannel)
        else:
            self.reply(irc, "The sun is rising and a new day begins. The seer has "+
            "the opportunity to reveal another players identity now.", 
            prefixNick=False, to=self.gamechannel)

        msgstring = "Current players (%s): %s." % (len(self.players), self._get_playerlist())
        self.reply(irc, msgstring,prefixNick=False, to=self.gamechannel)

        # there should only be one, but whatever
        for seer in self.list_from_class('seer'):
            self.reply(irc, "You can reveal the identity of another player now. "+
            "To do that, "+ircutils.bold("*privately*")+
            " tell me which player you'd like "+
            "to identify with 'reveal NAME_OF_PLAYER', e.g. 'reveal sabdfl' "+
            "to reveal 'sabdfl's identity", private=True, to=seer, fast=True)

        for sorc in self.list_from_class('sorcerer'):
            self.reply(irc, "You can use your magic to check if a player is the seer now. "+
            "To do that, "+ircutils.bold("*privately*")+
            " tell me which player you'd like "+
            "to check with 'reveal NAME_OF_PLAYER', e.g. 'reveal sabdfl' "+
            "to check if 'sabdfl's is the seer.", private=True, to=sorc, fast=True)

    def _check_continue(self, irc, msg, args):
        """Checks whether the game is over"""
        seerval = 0
        if self.count_class('seer')>0:
            seerval = 1
        # check parity
        if self.count_class('villager')+self.count_class('seer')+self.count_class('hunter')+self.count_class('sorcerer')+self.count_class('apprenticeseer')+self.count_class('prince')+self.count_class('toughguy')+self.count_class('cobbler')+self.count_class('lycan')+self.count_class('priest')+self.count_class('diseased') <= self.count_class('werewolf') or self.count_class('werewolf')==0:
            self._game_over(irc, msg, args)
            return True
        return False
        
    def reveal(self, irc, msg, args, nickname, text):
        """<nickname>
        
        Reveals the identity of <nickname> to the seer"""
        nick=msg.nick
        
        nickname=self.fixnick(nickname) #for case-insensitivity
        
        if text and self.channeloptions['debug']:
            nick=text

        if not nick in self.players:
            self.reply(irc, "You're not participating in the game.")
            return
        if not self.game_started:
            self.reply(irc, "Someone needs to start a game using 'startgame' first")
            return True

        if (self.game_phase=='morning' and self.players[nick]['class']=='seer') or (self.game_phase=='morning' and self.players[nick]['class']=='sorcerer'):
            pass
        else:
            return
        if self.players[nick]['used_reveal']==True:
            self.reply(irc, "You have already used your ability.", private=True,
            to=nick)
            return
        if not nickname in self.players:
            self.reply(irc, nickname+" is not playing in this round.",
            to=nick, private=True)
            return
        if nickname == nick:
            self.reply(irc, "You can't reveal your own identity!", private=True,
            to=nick)
            return
        c=self.players[nickname]['class']
        if self.players[nick]['class']=='sorcerer':
            self.players[nick]['used_reveal']=True
            if c=='seer':
                self.reply(irc, nickname+" is the seer!", private=True
                , to=nick)
            else:
                self.reply(irc, nickname+" is not the seer.", private=True
                , to=nick)
            m='The %s used magic to determine if a player is the seer or not.' % self.players[nick]['class']
            self.reply(irc, m, private=False, prefixNick=False, 
            to=self.gamechannel)
        else:
            self.players[nick]['used_reveal']=True
            if c=='werewolf' or c=='lycan':
                self.reply(irc, nickname+" is a werewolf! ", private=True
                , to=nick)
                if self.channeloptions['show_seer_result']:
                    m='The seer has revealed the identity of a '+ircutils.bold(c)+'!'
                else:
                    m='The seer has revealed the identity of a player.'
                self.reply(irc, m, private=False, prefixNick=False, 
                to=self.gamechannel)
            elif c=='sorcerer':
                self.reply(irc, nickname+" is a villager.", private=True
                , to=nick)
                if self.channeloptions['show_seer_result']:
                    m='The seer has revealed the identity of a '+ircutils.bold('villager')+'.'
                else:
                    m='The seer has revealed the identity of a player.'
                self.reply(irc, m, private=False, prefixNick=False, 
                to=self.gamechannel)
            else:
                #villager, hunter
                self.reply(irc, "%s is a villager." % (nickname) , private=True
                , to=nick)
                if self.channeloptions['show_seer_result']:
                    m='The seer has revealed the identity of a '+ircutils.bold('villager')+'.'
                else:
                    m='The seer has revealed the identity of a player.'
                self.reply(irc, m, private=False, prefixNick=False, 
                to=self.gamechannel)
        l=self.list_from_class('seer')+self.list_from_class('sorcerer')
        for player in l:
            if self.players[player]['used_reveal']==False:
                return
        self._phase_discuss(irc, msg, args)

    reveal = wrap(reveal, ['private', 'something', optional('something')])

    def protect(self, irc, msg, args, nickname, text):
        """<nickname>
        
        (Werewolf) Choose a player to protect and the next attempt to kill them will fail."""
        nick=msg.nick
        
        nickname=self.fixnick(nickname) #for case-insensitivity
        
        if text and self.channeloptions['debug']:
            nick=text

        if not nick in self.players:
            self.reply(irc, "You're not participating in the game.")
            return
        if not self.game_started:
            self.reply(irc, "Someone needs to start a game using 'startgame' first")
            return True

        if ((self.game_phase=='morning' or self.game_phase=='discussion') and self.players[nick]['class']=='priest'):
            pass
        else:
            return

        if self.players[nick].get('used_protect')==True:
            self.reply(irc, "You have already used your ability.", private=True,
            to=nick)
            return
        if not nickname in self.players:
            self.reply(irc, nickname+" is not playing in this round.",
            to=nick, private=True)
            return
        if nickname == nick:
            self.reply(irc, "You can't choose to protect yourself!", private=True,
            to=nick)
            return
        c=self.players[nickname]['class']
        self.players[nick]['used_protect']=True
        self.players[nickname]['protected']=True
        self.reply(irc, 'May the light shine upon %s.' % nickname, private=True,to=nick)
    protect = wrap(protect, ['private', 'something', optional('something')])

    def fixnick(self, nickname):
        fix=''.join([item for item in self.players if item.lower()==nickname.lower()])
        if fix:
            nickname=fix
        return nickname

    def _voice(self, irc, nicks):
        if not self.gamechannel:
            return
        if self.channeloptions['voice']:
            playing=[n for n in nicks if n in self.players]
            fake=[n for n in playing if self.players[n].get('fake')]
            nicks=[n for n in nicks if n not in fake]
            self._sendMsg(irc, ircmsgs.voices(self.gamechannel, nicks))
                
    def _devoice(self, irc, nicks):
        if not self.gamechannel:
            return
        if self.channeloptions['voice']:
            playing=[n for n in nicks if n in self.players]
            fake=[n for n in playing if self.players[n].get('fake')]
            nicks=[n for n in nicks if n not in fake]
            self._sendMsg(irc, ircmsgs.devoices(self.gamechannel, nicks))

    def _moderate(self, irc, msg, args):
        if self.channeloptions['moderate']:
            channel=self.gamechannel
            self._sendMsg(irc, ircmsgs.mode(channel, ['+m']))

    def _unmoderate(self, irc, msg, args):
        if self.channeloptions['moderate']:
            channel=self.gamechannel
            self._sendMsg(irc, ircmsgs.mode(channel, ['-m']))

    def _sendMsg(self, irc, msg):
        if self.channeloptions['use_queue']:
            irc.queueMsg(msg)
        else:
            irc.sendMsg(msg)
        irc.noReply()

    def setoption(self, irc, msg, args, channel, text, value):
        """<option> <value>
        
        Changes an option for the Werewolf game.  You can view the 
        options for the current channel with the showoptions command."""
        try:
            self._read_options(msg.args[0])
        except:
            pass
        if value.lower()=='true':
            value=True
        elif value.lower()=='false':
            value=False
        elif value.lower()=='unset':
            if text in self.channeloptions:
                self.reply(irc, 'Set %s %s-->(unset)' % (text, self.channeloptions[text]))
                del self.channeloptions[text]
                try:
                    self._write_options(msg.args[0])
                except:
                    self.reply(irc, 'Failed to write options to file. :(')
            else:
                self.reply(irc, '%s was already unset.' % text)
            return
        if text in self.channeloptions:
            self.reply(irc, 'Set %s %s-->%s' % (text, self.channeloptions[text], value))
            self.channeloptions[text]=value
        else:
            self.reply(irc, 'Set %s (unset)-->%s' % (text, value))
            self.channeloptions[text]=value
        try:
            self._write_options(msg.args[0])
        except:
            self.reply(irc, 'Failed to write options to file. :(')
    setoption = wrap(setoption, [('checkChannelCapability', 'op'), 'something', 'something'])

    def showoptions(self, irc, msg, args):
        """(takes no arguments)
        
        Shows options for the Werewolf game for the current channel."""
        try:
            self._read_options(msg.args[0])
        except:
            pass
        txt=', '.join(['='.join([str(i) for i in item]) for item in list(self.channeloptions.items())])
        self.reply(irc, txt)
    showoptions = wrap(showoptions)

    def choose_role(self, role, n=999):
        p=random.choice(list(self.players.keys()))

        for i in range(n):
            #list of players with unset classes
            plist=[p for p in self.players if self.players[p]['class']=='']
            if len(plist)==0:
                break
            player=random.choice(plist)
            self.players[player]['class']=role
        return

    def count_class(self, role):
        return len([p for p in self.players if self.players[p]['class']==role])

    def list_from_class(self, role):
        return [p for p in self.players if self.players[p]['class']==role]

    def add_player(self, n, fake=False):
        if fake:
            self.players[n]={'class':'','fake':True}
        else:
            self.players[n]={'class':''}

    def remove_dead(self):
        l=[p for p in self.players if self.players[p]['class'].startswith('dead_')]
        for player in l:
            if self.players[player]['class']=='cobbler':
                self.updatescore(player, 1, 1, self.gamechannel) # points+=1, games+=1
            else:
                self.updatescore(player, 0, 1, self.gamechannel) # games+=1
            del self.players[player]
        return

    def list_roles(self):
        t=''
        roles=['villager','hunter','seer','werewolf','sorcerer', 'prince', 'toughguy', 'apprenticeseer', 'cobbler','lycan','priest', 'diseased']
        for role in roles:
            n=self.count_class(role)
            if n>0:
                if n==1:
                    t=t+'%s %s, ' % (self.count_class(role), role)
                else:
                    t=t+'%s %ss, ' % (self.count_class(role), role)
        t=t.rsplit(', ',1)[0]
        t=t.rsplit(', ',1)[0]+', and '+t.rsplit(', ',1)[1]
        t=t.replace('werewolfs', 'werewolves')
        return t

    def reply(self, irc, text, action=False, private=False, prefixNick=False, to=gamechannel, fast=False):
        if to in self.players:
            if self.players[to].get('fake'):
                text='(to %s): %s' % (to, text)
                text=ircutils.mircColor(text, fg=14)
                to=self.gamechannel
        
        if action==True or fast==False:
            irc.reply(text, action=action, private=private, prefixNick=prefixNick, to=to)
        else:
            if (prefixNick) and ('#' not in to):
                text='%s: %s' % (to, text)
            m=ircmsgs.privmsg(to, text)
            self._sendMsg(irc, m)

    def myscore(self, irc, msg, args):
        """wip
        
        """
        nick=msg.nick
#        nRows, result = db.doQuery("select id, nick, points, gamesplayed, lastgame from werewolf where nick = '%s' limit 1" %
#                         db.escapeString( nick ) )

        try:
            nRows, result = db.doQuery("select id, nick, points, gamesplayed, lastgame from werewolf where nick = '%s' limit 1" %
                             db.escapeString( nick ) )
        except Exception as e:
            irc.error("Sorry, I can't seem to get that information :(")
            return

        if len(result) == 0:
            irc.reply("Not found.")
            return

        row = result[0]
        (db_id,db_nick,db_points,db_gamesplayed,db_lastgame)=(row[0],row[1],row[2],row[3],row[4])
        
        irc.reply("%s // %s points // %s games played // last game %s" % (db_nick, db_points, db_gamesplayed, db_lastgame))
    myscore = wrap(myscore, [('checkCapability', 'admin')])

    def updatescore(self, nick, points_add, games_played_add, channel):
        """<nick> <points to add> <games played to add> <channel>
        
        """
        
        siteid = self._siteidfromnick(nick)
        # If a siteid is set, use current season, otherwise, use season 0
        
        try:
            if siteid:
                nRows, result = db.doQuery("select count(*) from werewolf where userid=%s and channel='%s' and season=%s" %
                                 (siteid, db.escapeString(channel), site.season))
            else:
                nRows, result = db.doQuery("select count(*) from werewolf where nick='%s' and channel='%s' and season=0" %
                                 (db.escapeString(nick), db.escapeString(channel)))
        except Exception as e:
            self.log.info('Error in "updatescore (select count)"; Something went wrong with the query.')
            return
        
        #self.log.info('rows = %s' % repr(rows))
        #self.log.info('rows[0] = %s' % repr(rows[0]))
        
        c=result[0][0]
        
        #self.log.info('%s instances.' % c)
        
        if c==0:
            try:
                if siteid:
                    nRows, result = db.doQuery("insert into werewolf (nick,userid, points,gamesplayed,lastgame,channel,season) values ('%s', %s, %s, %s, now(), '%s', %s)" %
                                     (db.escapeString(nick), siteid, points_add, games_played_add, db.escapeString(channel),site.season))
                else:
                    nRows, result = db.doQuery("insert into werewolf (nick,points,gamesplayed,lastgame,channel,season) values ('%s', %s, %s, now(), '%s', 0)" %
                                     (db.escapeString(nick), points_add, games_played_add, db.escapeString(channel)))
            except Exception as e:
                self.log.info('Error in "updatescore (insert)"; Something went wrong with the query.')
                return
        else:
            try:
                if siteid:
                    q="update werewolf set nick='%s', points=points+%s, gamesplayed=gamesplayed+%s, lastgame=now() where userid=%s and channel='%s' and season=%s" % (db.escapeString(nick), points_add, games_played_add, siteid, db.escapeString(channel), site.season)
                    self.log.info('Attempting query: for updatescore (update): %s ' % q)
                    nRows, result = db.doQuery("update werewolf set nick='%s', points=points+%s, gamesplayed=gamesplayed+%s, lastgame=now() where userid=%s and channel='%s' and season=%s" %
                                     (db.escapeString(nick), points_add, games_played_add, siteid, db.escapeString(channel), site.season ))
                else:
                    q="update werewolf set points=points+%s, gamesplayed=gamesplayed+%s, lastgame=now() where nick='%s' and channel='%s' and season=0" % (points_add, games_played_add, db.escapeString(nick), db.escapeString(channel) )
                    self.log.info('Attempting query: for updatescore (update): %s ' % q)
                    nRows, result = db.doQuery("update werewolf set points=points+%s, gamesplayed=gamesplayed+%s, lastgame=now() where nick='%s' and channel='%s' and season=0" %
                                     (points_add, games_played_add, db.escapeString(nick), db.escapeString(channel) ))
            except Exception as e:
                self.log.info('Error in "updatescore (update)"; Something went wrong with the query.')
                return

    def _siteidfromnick(self, nick):
        """takes no arguments

        Returns the site id from a nick.  Requires the user to register with the bot.
        """
        
        irc=self.irc
        
        try:
            user = ircdb.users.getUser(self._nickToHostmask(nick))
        except KeyError:
            # The bot doesn't recognize the user.  They need to register or add a hostmask or identify, etc.
            return
        channel = "werewolf"
        channeluser = (channel, user.id)
        if channeluser not in self.db:
            return
        data = self.db[channeluser]
        if 'id' not in data:
            return
        else:
            siteid = data['id']
        
        return siteid
    
#    def myid(self, irc, msg, args):
#        """
#        Display your site id for the Werewolf game.
#        """
#        nick=msg.nick
        
#        siteid = self._siteidfromnick(msg.nick)
#        if siteid:
#            irc.reply(siteid)
#        else:
#            irc.error("Could not get a valid site id.")
#    myid = wrap(myid)


#    def debug(self, irc, msg, args):
#        """Game be debuggin' yo.
#        """
        
#        self.updatescore('SpiderDave', 1, 1, site.game_channel) # points+=1, games+=1

#    debug = wrap(debug, [('checkCapability', 'admin')])


    def setkey(self, irc, msg, args, user, txt):
        """[<username>] <gamekey>

        Sets game key for the <username>."""
        
        key=txt
        self._preCheck(irc, msg, user)
        # I'm using "channel" here for other purposes because I don't want it channel specific.
        channel="werewolf"
        channeluser = (channel, user.id)
        
        # ToDo: Add time limit to using keys
        nRows, result = db.doQuery("select `userid` from `gamekeys` where `gamekey`='%s'" %
                         (db.escapeString(key)))
        if not result:
            irc.error('nope')
            return
        
        siteid = result[0][0]
        
        # remove gamekey
        nRows, result = db.doQuery("delete from `gamekeys` where `gamekey`='%s'" % (db.escapeString(key)) )
        if nRows == 0:
            irc.error('Error: Could not remove gamekey.')
            return
        
        if channeluser not in self.db:
            self.db[channeluser] = {}
        self.db[channeluser].update({'id': siteid})
        irc.replySuccess()
    setkey = wrap(setkey, ['user','text'])
    
    
    def query(self, irc, msg, args, txt):
        """
        Run a query on the werewolf database.
        """
        nRows, result = db.doQuery(txt)
        irc.reply(repr(result))
    query = wrap(query, [('checkCapability', 'admin'),'text'])
Class = Werewolf

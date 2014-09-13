###
# by SpiderDave
###

import supybot.utils as utils
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os
import json


# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True

    def movie(self, irc, msg, args, text):
        """<film>

        Get information on <film> from TMDb
        """
        
        try:
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            key=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return
        base_url = "https://api.themoviedb.org/3/search/movie"
        base_url2 = "https://api.themoviedb.org/3/movie/"
        try:
            url=base_url+"?api_key="+key+"&query="+utils.web.urlquote(text)
            res=utils.web.htmlToText(utils.web.getUrl(url))
            res=json.loads(res)
        except:
            irc.reply("Error: I couldn't get a response from TMDb.")
            return
        if len(res['results'])==0:
            irc.reply("Sorry, I couldn't find anything on that one.")
            return
        res=res['results'][0] #just use the first one found
        res_title = ircutils.bold(res['title'])
        res_date = res['release_date']
        res_avg = str(res['vote_average'])
        res_id = str(res['id'])
        res_adult = str(res['adult'])
        try:
            url=base_url2+res_id+"?api_key="+key
            res2=utils.web.htmlToText(utils.web.getUrl(url))
            res2=json.loads(res2)
            res2_ov=res2['overview']
        except:
            res2_ov="unable to obtain description"
        text = ('%s (%s) %s/10 http://www.themoviedb.org/movie/%s %s' % (res_title, res_date, res_avg, res_id, res2_ov))
        text = text.replace("\n", " ")  # results may contain new lines which need to be stripped
        irc.reply(text)
    movie = wrap(movie, ['text'])

    def tv(self, irc, msg, args, text):
        """<show>

        Get information on <show> from TMDb
        """
        
        try:
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            key=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return
        base_url = "https://api.themoviedb.org/3/search/tv"
        base_url2 = "https://api.themoviedb.org/3/tv/"
        try:
            url=base_url+"?api_key="+key+"&query="+utils.web.urlquote(text)
            res=utils.web.htmlToText(utils.web.getUrl(url))
            res=json.loads(res)
        except:
            irc.reply("Error: I couldn't get a response from TMDb.")
            return
        if len(res['results'])==0:
            irc.reply("Sorry, I couldn't find anything on that one.")
            return
        res=res['results'][0] #just use the first one found
        res_title = ircutils.bold(res['name'])
        res_date = res['first_air_date']
        res_avg = str(res['vote_average'])
        res_id = str(res['id'])
        try:
            url=base_url2+res_id+"?api_key="+key
            res2=utils.web.htmlToText(utils.web.getUrl(url))
            res2=json.loads(res2)
            res2_ov=res2['overview']
        except:
            res2_ov="unable to obtain description"
        text = ('%s (%s) %s/10 http://www.themoviedb.org/tv/%s %s' % (res_title, res_date, res_avg, res_id, res2_ov))
        text = text.replace("\n", " ")  # results may contain new lines which need to be stripped
        irc.reply(text)
    tv = wrap(tv, ['text'])


    def person(self, irc, msg, args, text):
        """<person>

        Get information on <person> from TMDb
        """
        
        try:
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            key=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return
        base_url = "https://api.themoviedb.org/3/search/person"
        base_url2 = "https://api.themoviedb.org/3/person/"
        try:
            url=base_url+"?api_key="+key+"&query="+utils.web.urlquote(text)
            res=utils.web.htmlToText(utils.web.getUrl(url))
            res=json.loads(res)
        except:
            irc.reply("Error: I couldn't get a response from TMDb.")
            return
        if len(res['results'])==0:
            irc.reply("Sorry, I couldn't find anything on that one.")
            return
        res=res['results'][0] #just use the first one found
        res_name = ircutils.bold(res['name'])
        res_id = str(res['id'])
        try:
            url=base_url2+res_id+"?api_key="+key
            res2=utils.web.htmlToText(utils.web.getUrl(url))
            res2=json.loads(res2)
            res2_bio=res2['biography']
            res2_aka=res2['also_known_as']
            res2_bd=res2['birthday']
            res2_dd=res2['deathday']
            res2_hp=res2['homepage']
            res2_bp=res2['place_of_birth']
        except:
            res2_bio="unable to obtain biographical data from website"
            res2_aka=""
            res2_bd=""
            res2_dd=""
            res2_hp=""
            res2_bp=""
        text = res_name
        if res2_aka: 
            text = ('%s AKA %s' % (text, res2_aka))
        if res2_bd and res2_dd:
            text = ('%s (%s-%s)' % (text, res2_bd, res2_dd))
        elif res2_bd:
            text = ('%s (%s- )' % (text, res2_bd))
        if res2_bp:
            text = ('%s %s' % (text, res2_bp))
        text = ('%s http://www.themoviedb.org/person/%s' % (text, res_id))
        if res2_hp:
            text = ('%s Homepage %s' % (text, res2_hp))
        if res2_bio:
            text = ('%s %s' % (text, res2_bio))
        else:
            text = ('%s no biography available' % text)
        text = text.replace("\n", " ")  # results may contain new lines which need to be stripped
        irc.reply(text)
    person = wrap(person, ['text'])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

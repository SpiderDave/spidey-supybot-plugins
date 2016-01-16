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

try:
    # Python 3
    import urllib.request as urllib2
except ImportError:
    # Python 2
    import urllib2

try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
except:
    PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)
@internationalizeDocstring
class _Plugin(callbacks.Plugin):
    """Contains commands for checking movie and tv information from themoviedb.org.
    """
    threaded = True

    def _get_redirected_url(self, url):
        opener = urllib2.build_opener(urllib2.HTTPRedirectHandler)
        request = opener.open(url)
        return request.url

    def movie(self, irc, msg, args, opts, text):
        """[--language <language>] <film>

        Get information on <film> from TMDb
        """
        
        try:
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            apiKey=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return

        # input options
        language=None
        for (k, value) in opts:
            if k == 'language':
                language=value

        base_url = "https://api.themoviedb.org/3/search/movie"
        base_url2 = "https://api.themoviedb.org/3/movie/"
        try:
            url=base_url+"?api_key="+apiKey+"&query="+utils.web.urlquote(text)
            res=utils.web.htmlToText(utils.web.getUrl(url))
            res=json.loads(res)
        except:
            # need better error handling here
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
            url=base_url2+res_id+"?api_key="+apiKey
            if language:
                url=url+'&language='+language
            res2=utils.web.htmlToText(utils.web.getUrl(url))
            res2=json.loads(res2)
            res2_ov=res2['overview']
        except:
            res2_ov="unable to obtain description"
        
        newUrl='http://www.themoviedb.org/movie/%s' % (res_id)
        if language:
            newUrl=self._get_redirected_url(newUrl) + '?language=' + language

        out = ('%s (%s) %s/10 %s %s' % (res_title, res_date, res_avg, newUrl, res2_ov))
        out = out.replace("\n", " ")  # results may contain new lines which need to be stripped
        irc.reply(out)
        
    movie = wrap(movie, [getopts({'language':'somethingWithoutSpaces'}), 'text'])

    def tv(self, irc, msg, args, opts, text):
        """[--language <language>] <show>

        Get information on <show> from TMDb
        """
        
        try:
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            apiKey=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return

        # input options
        language=None
        for (k, value) in opts:
            if k == 'language':
                language=value

        base_url = "https://api.themoviedb.org/3/search/tv"
        base_url2 = "https://api.themoviedb.org/3/tv/"
        try:
            url=base_url+"?api_key="+apiKey+"&query="+utils.web.urlquote(text)
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
            url=base_url2+res_id+"?api_key="+apiKey
            if language:
                url=url+'&language='+language
            res2=utils.web.htmlToText(utils.web.getUrl(url))
            res2=json.loads(res2)
            res2_ov=res2['overview']
        except:
            res2_ov="unable to obtain description"

        newUrl='http://www.themoviedb.org/tv/%s' % (res_id)
        if language:
            newUrl=self._get_redirected_url(newUrl) + '?language=' + language

        text = ('%s (%s) %s/10 %s %s' % (res_title, res_date, res_avg, newUrl, res2_ov))
        text = text.replace("\n", " ")  # results may contain new lines which need to be stripped
        irc.reply(text)
    tv = wrap(tv, [getopts({'language':'somethingWithoutSpaces'}), 'text'])

    def person(self, irc, msg, args, opts, text):
        """[--language <language>] <person>

        Get information on <person> from TMDb
        """
        
        try:
            f = open('%s%stmdbkey.dat' % (conf.supybot.directories.data(), os.sep), 'r')
            apiKey=f.read().strip()
            f.close
        except:
            irc.reply('Error: missing or key.  Check tmdbkey.dat file in your data folder.')
            return

        # input options
        language=None
        for (k, value) in opts:
            if k == 'language':
                language=value

        base_url = "https://api.themoviedb.org/3/search/person"
        base_url2 = "https://api.themoviedb.org/3/person/"
        try:
            url=base_url+"?api_key="+apiKey+"&query="+utils.web.urlquote(text)
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
            url=base_url2+res_id+"?api_key="+apiKey
            if language:
                url=url+'&language='+language
            res2=utils.web.htmlToText(utils.web.getUrl(url))
            res2=json.loads(res2)
            res2_bio=res2['biography']
            res2_name=res2['name']
            res2_aka=res2['also_known_as'][0]
            res2_bd=res2['birthday']
            res2_dd=res2['deathday']
            res2_hp=res2['homepage']
            res2_bp=res2['place_of_birth']
        except:
            res2_bio="unable to obtain biographical data from website"
            res2_name=""
            res2_aka=""
            res2_bd=""
            res2_dd=""
            res2_hp=""
            res2_bp=""
        
        text = res2_name
        if res2_aka: 
            text = ('%s AKA %s' % (text, res2_aka))
        
        if res2_bd and res2_dd:
            text = ('%s (%s-%s)' % (text, res2_bd, res2_dd))
        elif res2_bd:
            text = ('%s (%s- )' % (text, res2_bd))
        
        if res2_bp:
            text = ('%s %s' % (text, res2_bp))

        newUrl='http://www.themoviedb.org/person/%s' % (res_id)
        if language:
            newUrl=self._get_redirected_url(newUrl) + '?language=' + language
        
        text = ('%s %s' % (text, newUrl))
        if res2_hp:
            text = ('%s Homepage %s' % (text, res2_hp))
        if res2_bio:
            text = ('%s %s' % (text, res2_bio))
        else:
            text = ('%s no biography available' % text)
        text = text.replace("\n", " ")  # results may contain new lines which need to be stripped
        irc.reply(text)
    person = wrap(person, [getopts({'language':'somethingWithoutSpaces'}), 'text'])

_Plugin.__name__=PluginName
Class = _Plugin


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

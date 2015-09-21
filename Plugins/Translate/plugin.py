###
# Copyright (c) 2013, SpiderDave
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import os, urllib, urllib2, re

# This will be used to change the name of the class to the folder name
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]
class _Plugin(callbacks.Plugin):
    """Add the help for "@plugin help <Plugin Name>" here
    This should describe *how* to use this plugin."""
    threaded = True

    # **********************************************************************
    _transRe = re.compile(r"TRANSLATED_TEXT='(.*?)';",re.I)
    _transdetectRe = re.compile(r'&sl=(.*?)&tl=.*?&q=.*?"', re.I)
    
#    Examples:
#    translate from english to french hello "bonjour"
#    translate english to french hello "bonjour"
#    translate to french from english hello "bonjour"
#    translate to french hello "bonjour"
#    translate from french bonjour "hello"
#    translate bonjour "(from french) hello"
#    translate from en to fr hello "bonjour"
#    translate from english to fr hello "bonjour"
#    translate to fr hello (from english) "bonjour"
#    translate en fr hello (from english) "bonjour"


    def translate(self, irc, msg, args, text):
        """[<fromlanguage>] [to] <tolanguage> <text>

        Translates text using Google Translate.  More syntax examples here: http://pastebin.com/raw.php?i=3yj4T1BM
        """
        text=text.split()
        
        validlanguages = {
        'AFRIKAANS' : 'af',
        'ALBANIAN' : 'sq',
        'AMHARIC' : 'am',
        'ARABIC' : 'ar',
        'ARMENIAN' : 'hy',
        'AZERBAIJANI' : 'az',
        'BASQUE' : 'eu',
        'BELARUSIAN' : 'be',
        'BENGALI' : 'bn',
        'BIHARI' : 'bh',
        'BULGARIAN' : 'bg',
        'BURMESE' : 'my',
        'CATALAN' : 'ca',
        'CHEROKEE' : 'chr',
        'CHINESE' : 'zh',
        'CHINESE_SIMPLIFIED' : 'zh-CN',
        'CHINESE_TRADITIONAL' : 'zh-TW',
        'CROATIAN' : 'hr',
        'CZECH' : 'cs',
        'DANISH' : 'da',
        'DHIVEHI' : 'dv',
        'DUTCH': 'nl',  
        'ENGLISH' : 'en',
        'ESPERANTO' : 'eo',
        'ESTONIAN' : 'et',
        'FILIPINO' : 'tl',
        'FINNISH' : 'fi',
        'FRENCH' : 'fr',
        'GALICIAN' : 'gl',
        'GEORGIAN' : 'ka',
        'GERMAN' : 'de',
        'GREEK' : 'el',
        'GUARANI' : 'gn',
        'GUJARATI' : 'gu',
        'HEBREW' : 'iw',
        'HINDI' : 'hi',
        'HUNGARIAN' : 'hu',
        'ICELANDIC' : 'is',
        'INDONESIAN' : 'id',
        'INUKTITUT' : 'iu',
        'IRISH' : 'ga',
        'ITALIAN' : 'it',
        'JAPANESE' : 'ja',
        'KANNADA' : 'kn',
        'KAZAKH' : 'kk',
        'KHMER' : 'km',
        'KOREAN' : 'ko',
        'KURDISH': 'ku',
        'KYRGYZ': 'ky',
        'LAOTHIAN': 'lo',
        'LATVIAN' : 'lv',
        'LITHUANIAN' : 'lt',
        'MACEDONIAN' : 'mk',
        'MALAY' : 'ms',
        'MALAYALAM' : 'ml',
        'MALTESE' : 'mt',
        'MARATHI' : 'mr',
        'MONGOLIAN' : 'mn',
        'NEPALI' : 'ne',
        'NORWEGIAN' : 'no',
        'ORIYA' : 'or',
        'PASHTO' : 'ps',
        'PERSIAN' : 'fa',
        'POLISH' : 'pl',
        'PORTUGUESE' : 'pt-PT',
        'PUNJABI' : 'pa',
        'ROMANIAN' : 'ro',
        'RUSSIAN' : 'ru',
        'SANSKRIT' : 'sa',
        'SERBIAN' : 'sr',
        'SINDHI' : 'sd',
        'SINHALESE' : 'si',
        'SLOVAK' : 'sk',
        'SLOVENIAN' : 'sl',
        'SPANISH' : 'es',
        'SWAHILI' : 'sw',
        'SWEDISH' : 'sv',
        'TAJIK' : 'tg',
        'TAMIL' : 'ta',
        'TAGALOG' : 'tl',
        'TELUGU' : 'te',
        'THAI' : 'th',
        'TIBETAN' : 'bo',
        'TURKISH' : 'tr',
        'UKRAINIAN' : 'uk',
        'URDU' : 'ur',
        'UZBEK' : 'uz',
        'UIGHUR' : 'ug',
        'VIETNAMESE' : 'vi',
        'WELSH' : 'cy',
        'YIDDISH' : 'yi',
        'UNKNOWN' : ''
        }
        
        def _isvalidlanguage(l):
            l=l.strip().lower()
            for key in validlanguages:
                if key.lower()==l or validlanguages[key].lower()==l:
                    return True
            return False
        
        # translate from _ text || translate from _ to _ text
        if len(text)>=3 and text[0].strip().lower()=='from':
            fromlang=text[1].strip().lower()
            if len(text)>=5 and text[2].strip().lower()=='to':
                tolang=text[3].strip().lower()
                text=text[4:]
            else:
                tolang="english"
                text=text[2:]
        # translate to _ text || translate to _ from __ text
        elif len(text)>=3 and text[0].strip().lower()=='to':
            tolang=text[1].strip().lower()
            if len(text)>=5 and text[2].strip().lower()=='from':
                fromlang=text[3].strip().lower()
                text=text[4:]
            else:
                fromlang="unknown"
                text=text[2:]
        # translate _ from _ text
        elif len(text)>=4 and text[1].strip().lower()=='from':
            tolang=text[0].strip().lower()
            fromlang=text[2].strip().lower()
            text=text[3:]
        # translate _ to _ text
        elif len(text)>=4 and text[1].strip().lower()=='to':
            fromlang=text[0].strip().lower()
            tolang=text[2].strip().lower()
            text=text[3:]
        # translate _ _ text
        elif _isvalidlanguage(text[0]) and _isvalidlanguage(text[1]):
            fromlang=text[0].strip().lower()
            tolang=text[1].strip().lower()
            text=text[2:]
        # translate text
        # Just assume it's autodetect --> english
        else:
            fromlang=''
            tolang='en'
        
        # Somewhere along the way, we got invalid languages.  Best to just assume autodetect again.
        if not _isvalidlanguage(fromlang) or not _isvalidlanguage(tolang):
            fromlang=''
            tolang='en'
        
        text=' '.join(text)
        text = utils.web.urlquote(text)

        for key in validlanguages:
            fromlang = fromlang.replace(key.lower(), validlanguages[key])
            tolang = tolang.replace(key.lower(), validlanguages[key])
        fromlang = fromlang.replace('?', '')
        tolang = tolang.replace('?', '')
        fromlang = fromlang.replace('unknown', '')
        tolang = tolang.replace('unknown', '')
        url= 'https://translate.google.com/?sl=%s&tl=%s&q=%s' % (fromlang.lower(),tolang.lower(), text)
        html = utils.web.getUrl(url)
        
        m = self._transRe.search(html)
        if m:
            s = m.group(1)
            if fromlang=='':
              m2=self._transdetectRe.search(html)
              if m2:
                  detectedlanguage=m2.group(1).lower()
                  for key in validlanguages:
                      if detectedlanguage.lower()==validlanguages[key].lower():
                        detectedlanguage=detectedlanguage.replace('chinese_simplified','Chinese (simplified)')
                        detectedlanguage=detectedlanguage.replace('chinese_traditional','Chinese (traditional)')
                        detectedlanguage=key.capitalize()
                        break
                  s='(from ' + detectedlanguage+") "+s
            s=s.replace("\u0026", "&")
            s=s.replace(r'\x26#39;',"'")
            s=s.replace(r'\x26gt;',">")
            s=s.replace(r'\x26lt;',"<")
            s=re.sub(r'&#(1?\d\d);', lambda match: chr(int(match.group(1))), s)
            irc.reply(s)
        else:
            irc.reply("Error. (onoes)")
    translate = wrap(translate, ['text'])

_Plugin.__name__=PluginName
Class = _Plugin

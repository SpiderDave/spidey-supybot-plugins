###
# Copyright (c) 2014, SpiderDave
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
import os
try:
    from supybot.i18n import PluginInternationalization, internationalizeDocstring
except:
    PluginInternationalization, internationalizeDocstring = lambda x:x, lambda x:x

#The plugin name will be based on the plugin's folder.
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

_ = PluginInternationalization(PluginName)

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin(PluginName, True)

P = conf.registerPlugin(PluginName)
P.__name__ = PluginName

conf.registerGlobalValue(P, 'riotAPIKey', registry.String('', ("""Your riot API key."""), private=True))
conf.registerGlobalValue(P, 'lolValidRegions', registry.String('RU KR PBE1 BR1 OC1 JP1 NA1 EUN1 EUW1 TR1 LA1 LA2', ("""Valid Regions for LoL.""")))
conf.registerGlobalValue(P, 'lolDefaultRegion', registry.String('NA1', ("""Default Region for LoL.""")))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

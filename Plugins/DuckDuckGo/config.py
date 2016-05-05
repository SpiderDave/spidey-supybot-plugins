###
# Copyright (c) 2016, SpiderDave
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

conf.registerGlobalValue(P, 'showTitle', registry.Boolean(True, """Show title with results."""))
conf.registerGlobalValue(P, 'showSnippet', registry.Boolean(False, """Show snippet with results."""))
conf.registerGlobalValue(P, 'nResults', registry.PositiveInteger(3, """Maximum number of results to display."""))
conf.registerGlobalValue(P, 'separator', registry.StringSurroundedBySpaces('||', """Determines what string is used to separate results."""))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

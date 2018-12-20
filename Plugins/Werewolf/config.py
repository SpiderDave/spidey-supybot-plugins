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

import supybot.conf as conf
import supybot.registry as registry
import os
PluginName=os.path.dirname( __file__ ).split(os.sep)[-1]

try:
    from supybot.i18n import PluginInternationalization
    from supybot.i18n import internationalizeDocstring
    _ = PluginInternationalization(PluginName)
except:
    _, internationalizeDocstring = lambda x:x, lambda x:x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin(PluginName, True)

P = conf.registerPlugin(PluginName)
P.__name__ = PluginName
conf.registerGlobalValue(P, 'requireCapability',
    registry.String('admin', _("""Determines what capability (if any) is required to
    change game keys or other settings of another user.""")))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

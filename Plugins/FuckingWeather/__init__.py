###
# Copyright (c) 2018, SpiderDave
# All rights reserved.
#
###

"""
Displays the weather from http://www.thefuckingweather.com
"""

import supybot
import supybot.world as world
import importlib

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you're keeping the plugin in CVS or some similar system.
__version__ = ""

# XXX Replace this with an appropriate author or supybot.Author instance.
__author__ = 'SpiderDave'

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = { }

# This is a url where the most recent plugin package can be downloaded.
__url__ = 'https://github.com/SpiderDave/spidey-supybot-plugins'

from . import config
from . import plugin
importlib.reload(plugin) # In case we're being reloaded.
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    import test

Class = plugin.Class
configure = config.configure

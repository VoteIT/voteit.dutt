""" Fanstatic lib"""
from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

from voteit.core.fanstaticlib import voteit_common_js
from voteit.core.fanstaticlib import voteit_main_css


voteit_dutt_lib = Library('voteit_dutt', 'static')

voteit_dutt_css = Resource(voteit_dutt_lib, 'voteit_dutt.css', depends=(voteit_main_css,))
voteit_dutt = Group((voteit_dutt_css,))


def includeme(config):
    """ Include fanstatic resources. """
    from voteit.core.models.interfaces import IFanstaticResources
    from voteit.core.fanstaticlib import is_votable_context
    util = config.registry.getUtility(IFanstaticResources)
    util.add('voteit_dutt', voteit_dutt, is_votable_context)

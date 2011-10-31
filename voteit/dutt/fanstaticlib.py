""" Fanstatic lib"""
from fanstatic import Group
from fanstatic import Library
from fanstatic import Resource

from voteit.core.fanstaticlib import voteit_common_js
from voteit.core.fanstaticlib import voteit_main_css


voteit_dutt_lib = Library('voteit_dutt', '')

voteit_dutt_js = Resource(voteit_dutt_lib, 'voteit_dutt.js', depends=(voteit_common_js,))
voteit_dutt_css = Resource(voteit_dutt_lib, 'voteit_dutt.css', depends=(voteit_main_css,))

voteit_dutt = Group((voteit_dutt_js, voteit_dutt_css))

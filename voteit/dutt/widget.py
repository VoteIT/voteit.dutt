from urllib import urlencode

import httplib2
from colander import null
from colander import Invalid
from deform.widget import CheckedInputWidget
from deform.widget import RadioChoiceWidget
from pyramid.threadlocal import get_current_request
from deform.widget import CheckboxChoiceWidget

import voteit.dutt.patches


class DuttWidget(CheckboxChoiceWidget):
    """ 
    """
    template = 'dutt'
    readonly_template = 'dutt_readonly'

    def __init__(self, **kw):
        super(DuttWidget, self).__init__(**kw)

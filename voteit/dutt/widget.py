from deform.widget import CheckboxChoiceWidget

from voteit.dutt.fanstaticlib import voteit_dutt


class DuttWidget(CheckboxChoiceWidget):
    """ 
    """
    template = 'templates/dutt'
    readonly_template = 'templates/dutt_readonly'

    def __init__(self, **kw):
        super(DuttWidget, self).__init__(**kw)
        voteit_dutt.need()

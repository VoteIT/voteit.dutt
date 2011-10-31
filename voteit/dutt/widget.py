from deform.widget import CheckboxChoiceWidget


class DuttWidget(CheckboxChoiceWidget):
    """ 
    """
    template = 'dutt'
    readonly_template = 'dutt_readonly'

    def __init__(self, **kw):
        super(DuttWidget, self).__init__(**kw)

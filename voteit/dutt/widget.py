from deform.widget import CheckboxChoiceWidget


class DuttWidget(CheckboxChoiceWidget):
    """ 
    """
    template = 'templates/dutt'
    readonly_template = 'templates/dutt_readonly'

    def __init__(self, **kw):
        super(DuttWidget, self).__init__(**kw)

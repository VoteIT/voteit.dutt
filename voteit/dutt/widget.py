from deform.widget import CheckboxChoiceWidget

from voteit.dutt.fanstaticlib import voteit_dutt


class DuttWidget(CheckboxChoiceWidget):
    """ A checkbox widget with counter
    """
    template = 'dutt'
    readonly_template = 'dutt_readonly'

import colander
import deform

from voteit.dutt import DuttMF as _
from voteit.dutt.widget import DuttWidget


class Tuple(deform.Set):
    """ A type representing a tuple. This inherits from the Set type,
        and simply deserializes as a tuple instead.
        Note that this means that order won't be preserved!

    This type constructor accepts one argument:

    ``allow_empty``
       Boolean representing whether an empty set input to
       deserialize will be considered valid.  Default: ``False``.
    """
    def deserialize(self, node, value):
        super(Tuple, self).deserialize(node, value)
        return tuple(value)


@colander.deferred
def deferred_proposal_title(node, kw):
    context = kw['context']
    if context.get_workflow_state() == 'ongoing':
        return _(u"Mark the ones you like")
    return _(u"You can't change your vote now.")


@colander.deferred
def deferred_proposal_widget(node, kw):
    context = kw['context']
    #Choices should be something iterable with the contents [(UID for proposal, Title of proposal), <etc...>, ]
    choices = set()
    proposals = context.get_proposal_objects()
    for prop in proposals:
        choices.add((prop.uid, prop.title))
    max_choices = context.poll_settings.get('max', 0)
    if max_choices >= len(choices):
        #Disable info text if max is more or the same as the maximum available
        max_choices = 0
    min_choices = context.poll_settings.get('min', 0)
    return DuttWidget(values = choices, css_class = 'dutt_proposals', max = max_choices, min = min_choices)


@colander.deferred
def deferred_dutts_validator(node, kw):
    context = kw['context']
    return DuttValidator(context)


class DuttSchema(colander.Schema):
    proposals = colander.SchemaNode(
                    Tuple(allow_empty = True),
                    widget = deferred_proposal_widget,
                    title = deferred_proposal_title,
                    validator = deferred_dutts_validator)


class DuttValidator(object):
    """ Check that a user hasn't selected more items than allowed. """

    def __init__(self, context):
        self.context = context

    def __call__(self, node, value):
        max_choices = self.context.poll_settings.get('max', 0)
        min_choices = self.context.poll_settings.get('min', 0)
        assert isinstance(max_choices, int)
        assert isinstance(min_choices, int)
        if max_choices:
            if len(value) > max_choices:
                raise colander.Invalid(node, _(u"too_many_selected_error",
                                       default = u"You can only select a maximum of ${max}.",
                                       mapping = {'max': max_choices}))
        if min_choices:
            if len(value) < min_choices:
                raise colander.Invalid(node, _(u"too_few_selected_error",
                                       default = u"You must select at least ${min}.",
                                       mapping = {'min': min_choices}))


class DuttSettingsSchema(colander.Schema):
    max = colander.SchemaNode(colander.Int(),
                              title = _(u"Maximum dutts"),
                              description = _(u"A '0' disables this setting."),
                              default = 0,
                              missing = 0)
    min = colander.SchemaNode(colander.Int(),
                              title = _(u"Minimum dutts"),
                              description = _(u"A '0' disables this setting."),
                              default = 0,
                              missing = 0)
#     mark_as_approved = colander.SchemaNode(colander.Bool(),
#                                            title = _(u"Mark proposals as approved if they receive over 50% of the votes."))

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
def deferred_max_value(node, kw):
    context = kw['context']
    return context.poll_settings['max']

@colander.deferred
def deferred_proposal_widget(node, kw):
    context = kw['context']
    #Choices should be something iterable with the contents [(UID for proposal, Title of proposal), <etc...>, ]
    choices = set()
    proposals = context.get_proposal_objects()
    for prop in proposals:
        choices.add((prop.uid, prop.title))
    return DuttWidget(values=choices, css_class='dutt_proposals')


class DuttSchema(colander.Schema):
    max = colander.SchemaNode(colander.Int(),
                              widget = deform.widget.HiddenWidget(css_class='dutt_max'),
                              title = _(u"Maximum dutts"),
                              default = deferred_max_value)
    proposals = colander.SchemaNode(
                    Tuple(allow_empty = True),
                    widget=deferred_proposal_widget,
                    title=deferred_proposal_title,)


class DuttFormValidator(object):
    """ Check that a user hasn't selected more items than allowed. """

    def __init__(self, context):
        self.context = context
        self.max = context.poll_settings['max']
        assert isinstance(self.max, int)

    def __call__(self, form, value):
        if len(value['proposals']) > self.max:
            exc = colander.Invalid(form, 'Too many selected')
            exc['proposals'] = _(u"too_many_selected_error",
                                 default = u"You can only select a maximum of ${max}.",
                                 mapping = {'max': self.max})
            raise exc


class DuttSettingsSchema(colander.Schema):
    max = colander.SchemaNode(colander.Int(),
                              title = _(u"Maximum dutts"),)

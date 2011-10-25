import colander
import deform

from voteit.dutt import DuttMF as _


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
    return deform.widget.CheckboxChoiceWidget(values=choices)


class DuttSchema(colander.Schema):
    proposals = colander.SchemaNode(
                    Tuple(allow_empty = True),
                    widget=deferred_proposal_widget,
                    title=deferred_proposal_title,)


def poll_form_validator(form, value):
    #FIXME: implement
    pass



class DuttSettingsSchema(colander.Schema):
    max = colander.SchemaNode(colander.Int(),
                              title = _(u"Maximum dutts"),)

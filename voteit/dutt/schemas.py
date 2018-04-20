import colander
import deform

from voteit.dutt import _


@colander.deferred
def deferred_proposal_title(node, kw):
    context = kw['context']
    if context.get_workflow_state() == 'ongoing':
        return _(u"Mark the proposals you wish to vote for")
    return _(u"You can't change your vote now.")


@colander.deferred
def deferred_proposal_description(node, kw):
    context = kw['context']
    max_choices = context.poll_settings.get('max', len(context.proposals))
    min_choices = context.poll_settings.get('min', 0)
    if min_choices:
        return _("proposal_description_min",
                 default="Check at least ${min} and at most ${max} proposal(s).",
                 mapping={'min': min_choices, 'max': max_choices})
    return _("proposal_description_without_min",
             default="Check at most ${max} proposal(s).",
             mapping={'max': max_choices})


@colander.deferred
def deferred_proposal_widget(node, kw):
    context = kw['context']
    # Choices should be something iterable with the contents [(UID for proposal, Title of proposal), <etc...>, ]
    choices = []
    proposals = context.get_proposal_objects()
    for prop in proposals:
        choices.append((prop.uid, prop.title))
    max_choices = context.poll_settings.get('max', 0)
    if max_choices >= len(choices):
        # Disable info text if max is more or the same as the maximum available
        max_choices = 0
    min_choices = context.poll_settings.get('min', 0)
    return deform.widget.CheckboxChoiceWidget(
        values=choices,
        css_class='dutt_proposals',
        max=max_choices,
        min=min_choices,
    )


@colander.deferred
def deferred_dutts_validator(node, kw):
    context = kw['context']
    return DuttValidator(context)


class DuttSchema(colander.Schema):
    widget = deform.widget.FormWidget(
        template='form_modal',
        readonly_template='readonly/form_modal'
    )
    proposals = colander.SchemaNode(
        colander.List(),
        widget=deferred_proposal_widget,
        title=deferred_proposal_title,
        description=deferred_proposal_description,
        validator=deferred_dutts_validator
    )


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
                raise colander.Invalid(
                    node, _(u"too_many_selected_error",
                            default=u"You can only select a maximum of ${max}.",
                            mapping={'max': max_choices})
                )
        if min_choices:
            if len(value) < min_choices:
                raise colander.Invalid(
                    node, _(u"too_few_selected_error",
                            default=u"You must select at least ${min}.",
                            mapping={'min': min_choices})
                )


class DuttSettingsSchema(colander.Schema):
    max = colander.SchemaNode(
        colander.Int(),
        title=_(u"Maximum dutts"),
        description=_(u"A '0' disables this setting."),
        default=0,
        missing=0
    )
    min = colander.SchemaNode(
        colander.Int(),
        title=_(u"Minimum dutts"),
        description=_(u"A '0' disables this setting."),
        default=0,
        missing=0
    )

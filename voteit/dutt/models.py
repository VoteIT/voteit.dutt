from decimal import Decimal

from pyramid.renderers import render
from voteit.core.exceptions import BadPollMethodError
from voteit.core.models import poll_plugin

from voteit.dutt import _
from voteit.dutt.schemas import DuttSettingsSchema
from voteit.dutt.schemas import DuttSchema


class DuttPoll(poll_plugin.PollPlugin):
    name = "dutt_poll"
    title = _("Dutt poll")
    description = _(
        "dutt_poll_description",
        default="Tick proposals you like. There's a max amount, but you can add less if you want. "
        "This method is ment for time budgets or for preliminary checks. "
        "It should never be used to approve or deny proposals.",
    )
    proposals_min = 3
    recommended_for = _(
        "recommended_for",
        default="Preliminary checks or time budgets, never for actual decisions. "
        "This is almost always the wrong choice for board elections for instance.",
    )
    criteria = (
        poll_plugin.MajorityWinner(
            poll_plugin.CRITERIA_DEPENDS, comment=_("If every winner is above 50%")
        ),
        poll_plugin.MajorityLooser(
            poll_plugin.CRITERIA_DEPENDS, comment=_("If every looser is below 50%")
        ),
        poll_plugin.MutialMajority(False),
        poll_plugin.CondorcetWinner(False),
        poll_plugin.CondorcetLooser(False),
        poll_plugin.CloneProof(False),
        poll_plugin.Proportional(False),
    )

    def get_settings_schema(self):
        return DuttSettingsSchema()

    def get_vote_schema(self):
        """ Get an instance of the schema that this poll uses.
        """
        return DuttSchema()

    def handle_start(self, request):
        settings = self.context.poll_settings
        max_choices = settings.get("max")
        if max_choices:
            if len(self.context.proposals) / max_choices >= 2:
                msg = _(
                    "bad_quota_dutt",
                    default="You're using a very unsafe poll method that can easily be "
                    "manipulated. Even without tactical voting, "
                    "it's very likely to give the wrong result. "
                    "If you're simply distributing points for something that isn't actually "
                    "approved or denied (like a time budget) it's perfectly fine to use this. ",
                )
                raise BadPollMethodError(
                    msg,
                    self.context,
                    request,
                    recommendation=_(
                        "recommendation_bad_poll",
                        default="If your goal is to have a usable poll result, "
                        "use Sorted Schulze or Scottish STV. "
                    ),
                )

    def handle_close(self):
        """ Get the calculated result of this ballot.
        """
        total_votes = self._total_votes()

        def _get_percentage(num):
            val = Decimal(num) / total_votes
            return u"%s%%" % (round(val * 100, 1))

        counter = Counter()
        for (ballot, factor) in self.context.ballots:
            for uid in ballot["proposals"]:
                counter.add(uid, factor)
        result = counter.sorted_results()
        # Add percentage
        for item in result:
            item["percent"] = _get_percentage(item["num"])
        self.context.poll_result = result

    def render_result(self, view):
        votes = [x["uid"] for x in self.context.poll_result]
        novotes = set(self.context.proposal_uids) - set(votes)
        translate = view.request.localizer.translate
        total_votes = self._total_votes()
        results = []
        # Adjust result layout
        def _get_percentage(num):
            val = Decimal(num) / total_votes
            return round(val * 100, 0)

        for res in tuple(self.context.poll_result):
            results.append(
                {
                    "uid": res["uid"],
                    "num": res["num"],
                    "perc": res["percent"],
                    "perc_int": _get_percentage(res["num"]),
                }
            )
        for uid in novotes:
            results.append({"uid": uid, "num": 0, "perc": "0%", "perc_int": 0})

        vote_singular = translate(_("vote_singular", default="Vote"))
        vote_plural = translate(_("vote_plural", default="Votes"))

        def _vote_text(count):
            return view.request.localizer.pluralize(vote_singular, vote_plural, count)

        response = {
            "view": view,
            "context": self.context,
            "total_votes": total_votes,
            "results": results,
            "vote_text": _vote_text
        }
        proposals = {}
        for prop in self.context.get_proposal_objects():
            proposals[prop.uid] = prop
        response["proposals"] = proposals
        return render(
            "voteit.dutt:templates/results.pt", response, request=view.request
        )

    def _total_votes(self):
        return sum([x[1] for x in self.context.ballots])


class Counter(dict):
    """ To make counting easier """

    def add(self, uid, factor=1):
        if uid not in self:
            self[uid] = 0
        self[uid] += 1 * factor

    def sorted_results(self):
        results = []
        for (uid, num) in self.items():
            results.append({"uid": uid, "num": num})
        results = sorted(results, key=lambda x: x["num"], reverse=True)
        return tuple(results)


def includeme(config):
    config.registry.registerAdapter(DuttPoll, name=DuttPoll.name)

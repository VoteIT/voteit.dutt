from decimal import Decimal
from operator import itemgetter

from pyramid.renderers import render
from voteit.core.models.poll_plugin import PollPlugin

from voteit.dutt import _
from voteit.dutt.schemas import DuttSettingsSchema
from voteit.dutt.schemas import DuttSchema


class DuttPoll(PollPlugin):
    name = 'dutt_poll'
    title = _(u"Dutt poll")
    description = _(u"dutt_poll_description",
                    default = u"Tick proposals you like. There's a max amount, but you can add less if you want.")

    def get_settings_schema(self):
        return DuttSettingsSchema()
    
    def get_vote_schema(self):
        """ Get an instance of the schema that this poll uses.
        """
        return DuttSchema()

    def handle_close(self):
        """ Get the calculated result of this ballot.
        """
        total_votes = self._total_votes()

        def _get_percentage(num):
            val = Decimal(num) / total_votes
            return u"%s%%" % (round(val*100, 1))

        counter = Counter()
        for (ballot, factor) in self.context.ballots:
            for uid in ballot['proposals']:
                counter.add(uid, factor)
        result = counter.sorted_results()
        #Add percentage
        for item in result:
            item['percent'] = _get_percentage(item['num'])
        self.context.poll_result = result

    def render_result(self, view):
        votes = [x['uid'] for x in self.context.poll_result]
        novotes = set(self.context.proposal_uids) - set(votes)
        translate = view.request.localizer.translate
        total_votes = self._total_votes()
        results = []
        #Adjust result layout
        def _get_percentage(num):
            val = Decimal(num) / total_votes
            return round(val*100, 0)

        for res in tuple(self.context.poll_result):
            results.append({'uid': res['uid'],
                            'num': res['num'],
                            'perc': res['percent'],
                            'perc_int': _get_percentage(res['num'])})
        for uid in novotes:
            results.append({'uid': uid, 'num': 0, 'perc': '0%', 'perc_int': 0})
        
        vote_singular = translate(_("vote_singular", default = "Vote"))
        vote_plural = translate(_("vote_plural", default = "Votes"))
        def _vote_text(count):
            return view.request.localizer.pluralize(vote_singular, vote_plural, count)

        response = {}
        response['view'] = view
        response['context'] = self.context
        response['total_votes'] = total_votes
        response['results'] = results
        response['vote_text'] = _vote_text
        proposals = {}
        for prop in self.context.get_proposal_objects():
            proposals[prop.uid] = prop
        response['proposals'] = proposals
        return render('voteit.dutt:templates/results.pt', response, request = view.request)

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
            results.append({'uid': uid, 'num': num})
        results = sorted(results, key=lambda x: x['num'], reverse=True)
        return tuple(results)

def includeme(config):
    config.registry.registerAdapter(DuttPoll, name = DuttPoll.name)

from decimal import Decimal
from operator import itemgetter

from pyramid.renderers import render
from voteit.core.models.poll_plugin import PollPlugin

from voteit.dutt import DuttMF as _
from voteit.dutt.schemas import DuttSettingsSchema
from voteit.dutt.schemas import DuttSchema


class DuttPoll(PollPlugin):
    name = 'dutt_poll'
    title = _(u"Dutt poll")
    description = _(u"dutt_poll_description",
                    default = u"Tick proposals you like. There's a max amount, but you can add less if you want.")

    def __init__(self, context):
        super(DuttPoll, self).__init__(context)
        if not context.poll_settings:
            context.poll_settings = {'max': 5} #As default

    def get_settings_schema(self):
        return DuttSettingsSchema()
    
    def get_vote_schema(self, request=None, api=None):
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

    def render_result(self, request, api, complete=True):
        votes = [x['uid'] for x in self.context.poll_result]
        novotes = set(self.context.proposal_uids) - set(votes)
        response = {}
        response['api'] = api
        response['total_votes'] = self._total_votes()
        response['result'] = self.context.poll_result
        response['novotes'] = novotes
        response['get_proposal_by_uid'] = self.context.get_proposal_by_uid
        response['complete'] = complete
        response['vote_singular'] = api.translate(_(u"vote_singular", default = u"Vote"))
        response['vote_plural'] = api.translate(_(u"vote_plural", default = u"Votes"))
        return render('templates/results.pt', response, request = request)

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


from unittest import TestCase

from pyramid import testing
from voteit.core.models.agenda_item import AgendaItem
from voteit.core.models.poll import Poll
from voteit.core.models.proposal import Proposal
from voteit.core.models.interfaces import IPoll
from voteit.core.models.interfaces import IPollPlugin
from voteit.core.testing_helpers import active_poll_fixture
from zope.interface.verify import verifyClass
from zope.interface.verify import verifyObject


class DuttPollTests(TestCase):
    """ Dutt poll unit and integration tests """

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from voteit.dutt.plugin import DuttPoll
        return DuttPoll

    def _fixture(self):
        #register as adapter
        self.config.registry.registerAdapter(self._cut, (IPoll,), IPollPlugin, self._cut.name)

        #Enable workflows
        self.config.include('pyramid_zcml')
        self.config.load_zcml('voteit.core:configure.zcml')
        #Add agenda item - needed for lookups
        ai = AgendaItem()
        #Add a poll
        ai['poll'] = Poll()
        #Wrap in correct context
        poll = ai['poll']
        #Add proposals
        ai['p1'] = p1 = Proposal(title = 'p1', uid = 'p1uid')
        ai['p2'] = p2 = Proposal(title = 'p2', uid = 'p2uid')
        
        #Select proposals for this poll
        poll.proposal_uids = (p1.uid, p2.uid, )
        poll.set_field_value('poll_plugin', 'dutt_poll')
        return ai

    def _add_votes(self, poll):
        plugin = poll.get_poll_plugin()
        vote_cls = plugin.get_vote_class()
        ai = poll.__parent__
                
        v1 = vote_cls()
        v1.set_vote_data({'proposals':tuple([ai['p1'].uid])})
        poll['v1'] = v1
        
        v2 = vote_cls()
        v2.set_vote_data({'proposals':tuple([ai['p1'].uid])})
        poll['v2'] = v2
        
        v3 = vote_cls()
        v3.set_vote_data({'proposals':tuple([ai['p1'].uid, ai['p2'].uid])})
        poll['v3'] = v3

    def test_verify_class(self):
        verifyClass(IPollPlugin, self._cut)

    def test_verify_object(self):
        verifyObject(IPollPlugin, self._cut(Poll()))

    def test_handle_close(self):
        ai = self._fixture()
        poll = ai['poll']
        self._add_votes(poll)
        poll.close_poll()
        expected = ({'num': 1, 'percent': u'33.3%', 'uid': 'p2uid'}, {'num': 3, 'percent': u'100.0%', 'uid': 'p1uid'})
        self.assertEqual(poll.poll_result, expected)

    def test_render_result(self):
        request = testing.DummyRequest()
        ai = self._fixture()
        poll = ai['poll']
        self._add_votes(poll)
        poll.close_poll()
        plugin = poll.get_poll_plugin()
        self.failUnless('p1' in plugin.render_result(request))

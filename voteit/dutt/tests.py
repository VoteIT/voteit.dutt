from unittest import TestCase

import colander
import deform
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
        from voteit.dutt.models import DuttPoll
        return DuttPoll

    def _fixture(self):
        #register as adapter
        self.config.registry.registerAdapter(self._cut, name = self._cut.name)
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
        self.failUnless(verifyClass(IPollPlugin, self._cut))

    def test_verify_object(self):
        self.failUnless(verifyObject(IPollPlugin, self._cut(Poll())))

    def test_handle_close(self):
        ai = self._fixture()
        poll = ai['poll']
        self._add_votes(poll)
        poll.close_poll()
        expected = ({'num': 3, 'percent': u'100.0%', 'uid': 'p1uid'}, {'num': 1, 'percent': u'33.3%', 'uid': 'p2uid'})
        self.assertEqual(poll.poll_result, expected)

    def test_render_result(self):
        request = testing.DummyRequest()
        ai = self._fixture()
        poll = ai['poll']
        self._add_votes(poll)
        poll.close_poll()
        plugin = poll.get_poll_plugin()
        from voteit.core.views.api import APIView
        api = APIView(poll, request)
        self.failUnless('p1' in plugin.render_result(request, api))


class TestDuttValidator(TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    @property
    def _cut(self):
        from voteit.dutt.schemas import DuttValidator
        return DuttValidator

    def _mock_context(self, max = 0, min = 0):
        class _MockContext(testing.DummyResource):
            poll_settings = {'max': max, 'min': min}
        return _MockContext()

    def test_validate_ok(self):
        context = self._mock_context(max = 5)
        obj = self._cut(context)
        self.assertEqual(obj(None, range(2)), None)

    def test_too_many_selected(self):
        context = self._mock_context(max = 5)
        obj = self._cut(context)
        self.assertRaises(colander.Invalid, obj, None, range(6))

    def test_too_few_selected(self):
        context = self._mock_context(min = 5)
        obj = self._cut(context)
        self.assertRaises(colander.Invalid, obj, range(1), [1])
 
    def test_disabled_max_min(self):
        context = self._mock_context(max = 0, min = 0)
        obj = self._cut(context)
        for i in range(9):
            self.assertFalse(obj(None, range(i)))
         

class IntegrationTests(TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.include('voteit.core')
        self.config.include('voteit.dutt')

    def tearDown(self):
        testing.tearDown()

    def test_poll_plugin(self):
        poll = Poll()
        self.failUnless(self.config.registry.queryAdapter(poll, IPollPlugin, name = u'dutt_poll'))


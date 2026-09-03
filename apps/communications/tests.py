from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.accounts.models import User
from apps.communications.models import SocietyPoll, PollOption, PollVote, Notice, LostAndFoundItem, SocietyDocument

class CommunicationsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin_comm', password='Password123!', role=User.Role.ADMIN)
        self.resident = User.objects.create_user(username='res_comm', password='Password123!', role=User.Role.RESIDENT)

    def test_poll_voting(self):
        poll = SocietyPoll.objects.create(
            question='Install Gym Mirrors?',
            created_by=self.admin,
            end_date=timezone.now().date() + timedelta(days=5)
        )
        opt1 = PollOption.objects.create(poll=poll, option_text='Yes')
        opt2 = PollOption.objects.create(poll=poll, option_text='No')

        self.client.login(username='res_comm', password='Password123!')
        response = self.client.post(f'/communications/polls/{poll.pk}/vote/', {
            'option_id': opt1.id
        })
        self.assertEqual(response.status_code, 302)

        self.assertEqual(poll.total_votes, 1)
        self.assertEqual(opt1.percentage, 100.0)
        self.assertTrue(poll.user_has_voted(self.resident))

    def test_lost_and_found_flow(self):
        self.client.login(username='res_comm', password='Password123!')
        response = self.client.post('/communications/lost-found/', {
            'item_name': 'Keychain with 2 silver keys',
            'category': 'KEYS',
            'status': 'FOUND',
            'location': 'Clubhouse Foyer',
            'description': 'Silver ring keychain.',
            'contact_phone': '+1 555 1122'
        })
        self.assertEqual(response.status_code, 302)
        item = LostAndFoundItem.objects.filter(item_name='Keychain with 2 silver keys').first()
        self.assertIsNotNone(item)

        # Claim item
        response_claim = self.client.post(f'/communications/lost-found/{item.pk}/claim/')
        self.assertEqual(response_claim.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.status, LostAndFoundItem.ItemStatus.CLAIMED)

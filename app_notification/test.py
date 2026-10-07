from django.test import TestCase
from rest_framework.test import APIClient

from app_notification.models import Notification
from app_user.models import User


class NotificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='n@example.com', password='pass12345', phone='09134000000'
        )
        self.client.force_authenticate(user=self.user)

    def test_list_only_unread_active(self):
        Notification.objects.create(user=self.user, title='A', body='b', icon='i')
        Notification.objects.create(user=self.user, title='B', body='b', icon='i', is_read=True)
        Notification.objects.create(user=self.user, title='C', body='b', icon='i', is_active=False)
        resp = self.client.get('/notification/')
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(len(resp.data['notifications']), 1)

    def test_mark_read(self):
        n = Notification.objects.create(user=self.user, title='A', body='b', icon='i')
        resp = self.client.put(f'/notification/read/{n.pk}/')
        self.assertEqual(resp.status_code, 200, resp.data)
        n.refresh_from_db()
        self.assertTrue(n.is_read)

    def test_cannot_mark_other_users_notification(self):
        other = User.objects.create_user(email='o@example.com', password='x', phone='09135000000')
        n = Notification.objects.create(user=other, title='A', body='b', icon='i')
        resp = self.client.put(f'/notification/read/{n.pk}/')
        self.assertEqual(resp.status_code, 404)

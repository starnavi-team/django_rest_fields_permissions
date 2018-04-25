from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from rest_framework.test import APITestCase
from rest_framework import status

from .models import Project


class BaseTestingClass(APITestCase):
    def setUp(self):
        self.team_lead = User.objects.create(username='team_lead', password=make_password('qwerty123'),
                                             is_superuser=True, is_staff=True)
        self.team_member = User.objects.create(username='team_member', password=make_password('qwerty123'),
                                               is_staff=True)
        self.customer = User.objects.create(username='customer', password=make_password('qwerty123'))

        self.project = Project.objects.create(
            name='Test Project',
            status=1,
            description='Project description',
            team_lead_user=self.team_lead
        )


class ShowOnlyFieldPermissionTest(BaseTestingClass):

    def test_showing_field_for_team_lead(self):
        self.client.force_login(user=self.team_lead)
        response = self.client.get('/api/projects/')
        team_lead_user = response.data[0].get('team_lead_user')
        self.assertIsNotNone(team_lead_user)

    def test_showing_field_for_team_member(self):
        self.client.force_login(user=self.team_member)
        response = self.client.get('/api/projects/')
        team_lead_user = response.data[0].get('team_lead_user')
        self.assertIsNotNone(team_lead_user)

    def test_showing_field_for_customer(self):
        self.client.force_login(self.customer)
        response = self.client.get('/api/projects/')
        team_lead_user = response.data[0].get('team_lead_user')
        self.assertIsNone(team_lead_user)


class FieldPermissionTest(BaseTestingClass):

    def test_edit_status_field_for_team_lead(self):
        self.client.force_login(user=self.team_lead)
        response = self.client.patch('/api/projects/1/', data={'status': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=1)
        self.assertEqual(project.status, 2)

    def test_edit_status_field_for_team_member(self):
        self.client.force_login(user=self.team_member)
        response = self.client.patch('/api/projects/1/', data={'status': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=1)
        self.assertEqual(project.status, 2)

    def test_edit_status_field_for_customer(self):
        self.client.force_login(user=self.customer)
        response = self.client.patch('/api/projects/1/', data={'status': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(id=1)
        # But the field was not changed
        self.assertEqual(project.status, 1)

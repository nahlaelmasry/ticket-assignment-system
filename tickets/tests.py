from tickets.models import Ticket
from django.urls import reverse
from rest_framework import status
from django.test import TestCase, Client, APIClient
from django.contrib.auth import user_model


User = user_model()

class MyAppTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_superuser(username='manager', password='1234', email='manager@example.com')
        cls.agent = User.objects.create_user(username='agent', password='1234', is_staff=True)
        cls.regular_user = User.objects.create_user(username='user', password='1234')
        cls.unassigned_tickets = Ticket.objects.bulk_create([Ticket(ticket_to=None, ticket_sold=False) for _ in range(30)])

    def setUp(self):
        self.client = Client()


     
    def test_manager_create_ticket(self):
        self.client.force_login(self.manager)
        url = reverse('manager-tickets')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    
    def test_agent_sell_ticket(self):
        self.client.force_login(self.agent)
        ticket = Ticket.objects.create(ticket_to=self.agent, ticket_sold=False)
        url = reverse('agent-sell-ticket', kwargs={'ticket_id': ticket.ticket_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ticket.refresh_from_db()
        self.assertTrue(ticket.ticket_sold)

    def test_assign_available_tickets(self):
        # Log in as agent
        self.client.force_login(self.agent)
        # Create 15 unassigned tickets
        Ticket.objects.bulk_create([Ticket(ticket_to=None, ticket_sold=False) for _ in range(15)])
        url = reverse('agent-assign-tickets') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 15)
        for ticket_data in response.data:
            self.assertEqual(ticket_data['ticket_to'], self.agent)

    def test_agent_already_has_max_tickets(self):
        # Create the maximum allowed tickets (15) already assigned to the agent
        Ticket.objects.bulk_create([
            Ticket(ticket_to=self.agent, ticket_sold=False) for _ in range(15)
        ])

        url = reverse('agent-assign-tickets') 
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('assigned_tickets', response.data)
        self.assertEqual(len(response.data['assigned_tickets']), 15)


   

    
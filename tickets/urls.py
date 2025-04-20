from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MangerTicket, AgentTicket

agent_urls = [
    path('agent/tickets/list/', AgentTicket.as_view({'get': 'tickets_list'}),name='agent-tickets-list'),
    path('agent/tickets/assign/', AgentTicket.as_view({'get': 'take_available_tickets'}), name='agent-assign-tickets'),
    path('agent/tickets/sell/<int:pk>/', AgentTicket.as_view({'put': 'sell_ticket'}), name='agent-sell-ticket'),
]

router = DefaultRouter()
router.register(r'manager/tickets', MangerTicket,basename='manager-tickets')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(agent_urls)),
]

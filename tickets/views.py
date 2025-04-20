from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsSuperAdminUser,IsAdminUser
from django.db import transaction
from .models import Ticket
from .serializers import TicketSerializer
from django.core.exceptions import ObjectDoesNotExist

class AgentTicket(viewsets.ViewSet):
    permission_classes = [IsAdminUser]
    
    # get the list of tickets assigned to the agent
    def tickets_list(self, request):
        user = request.user
        try:
            assigned_tickets = Ticket.objects.filter(ticket_to=user, ticket_sold=False).order_by('created_at')
            serializer = TicketSerializer(assigned_tickets, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "No tickets found assigned to this agent."
                }, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {
                    "detail": "An error occurred while retrieving tickets."
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def take_available_tickets(self, request):
        user = request.user
        try:
            with transaction.atomic():
                # Check count of assigned tickets for this agen
                tickets_assigned_to_user = Ticket.objects.filter(ticket_to=user, ticket_sold=False).count()

                # If less than 15, assign available tickets to the agent
                if tickets_assigned_to_user < 15:
                    unassigned_tickets = list(
                                            Ticket.objects.filter(
                                                ticket_to__isnull=True, ticket_sold=False
                                            ).order_by('created_at')[:(15 - tickets_assigned_to_user)]
                                        )

                    # If there are no unassigned tickets left, the response should be empty.
                    if not unassigned_tickets:
                        return Response([], status=status.HTTP_200_OK)
                    
                    # Assign the tickets to the user
                    for ticket in unassigned_tickets:
                        ticket.ticket_to = user
                    Ticket.objects.bulk_update(unassigned_tickets, ['ticket_to'])
    
                # Fetch the updated list of tickets assigned to the use
                available_tickets = Ticket.objects.filter(ticket_to=user, ticket_sold=False).order_by('created_at')[:15]
                serializer = TicketSerializer(available_tickets, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"detail": "An error occurred while fetching and assigning tickets."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    

    @action(detail=True, methods=['put'])
    def sell_ticket(self, request, pk=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            raise NotFound(detail="Ticket not found.")

        if ticket.ticket_to == request.user:
            ticket.ticket_sold = True
            ticket.save()
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied(detail="You are not assigned to this ticket.")
        

#ModelViewSet provides default implementations for the standard 
# Create, Retrieve, Update, Destroy, and List (CRUDL) operations 
class MangerTicket(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdminUser]
    queryset = Ticket.objects.all().order_by('created_at')
    serializer_class = TicketSerializer

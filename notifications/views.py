from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Notification


@extend_schema(
    summary='List my notifications (last 30)',
    tags=['Notifications'],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_notifications(request):
    notifs = Notification.objects.filter(user=request.user)[:30]
    data = [
        {
            'id': str(n.id),
            'title': n.title,
            'message': n.message,
            'link': n.link,
            'is_read': n.is_read,
            'created_at': n.created_at,
        }
        for n in notifs
    ]
    return Response(data)


@extend_schema(
    summary='Mark a notification as read',
    tags=['Notifications'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_read(request, notification_id):
    updated = Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)
    if not updated:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'message': 'Marked as read'})


@extend_schema(
    summary='Mark all notifications as read',
    tags=['Notifications'],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': 'All notifications marked as read'})

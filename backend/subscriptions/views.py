from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from users.models import User, Subscription
from subscriptions.serializers import SubscriptionSerializer
from foodgram_backend.pagination import CustomPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def subscriptions_list(request):
    """Получение списка подписок пользователя."""
    user = request.user
    subscriptions = Subscription.objects.filter(user=user)
    users = User.objects.filter(id__in=subscriptions.values('subscriber'))
    
    limit = request.query_params.get('limit')
    
    if limit:
        try:
            limit_value = int(limit)
            users = users[:limit_value]  
        except ValueError:
            pass
    
    paginator = CustomPagination()
    page = paginator.paginate_queryset(users, request)
    
    if page is not None:
        serializer = SubscriptionSerializer(
            page, 
            many=True,
            context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)
    
    serializer = SubscriptionSerializer(
        users, 
        many=True,
        context={'request': request}
    )
    return JsonResponse({
        'count': users.count(),
        'next': None,
        'previous': None,
        'results': serializer.data
    })
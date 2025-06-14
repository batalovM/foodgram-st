from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import User, Subscription
from .serializers import UserSerializer, AvatarSerializer
from subscriptions.serializers import SubscriptionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(
        detail=True, methods=["post", "delete"], permission_classes=[IsAuthenticated]
    )
    @csrf_exempt
    def subscribe(self, request, pk=None):
        user = request.user
        author = self.get_object()
        if request.method == "POST":
            if user == author:
                return Response(
                    {"error": "Нельзя подписаться на себя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            subscription, created = Subscription.objects.get_or_create(
                user=user, subscriber=author
            )
            if not created:
                return Response(
                    {"error": "Вы уже подписаны"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscriptionSerializer(author, context={"request": request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == "DELETE":
            subscription = user.subscriptions.filter(subscriber=author)
            if not subscription.exists():
                return Response(
                    {"error": "Вы не подписаны"}, status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["put", "delete"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    @csrf_exempt
    def avatar(self, request):
        user = request.user
        if request.method == "PUT":
            if "avatar" not in request.data:
                return Response(
                    {"avatar": ["This field is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = AvatarSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"error": "Аватар не установлен"}, status=status.HTTP_400_BAD_REQUEST
            )

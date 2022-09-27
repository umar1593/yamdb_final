from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .filters import TitlesFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (Admin, AdminOrReadOnly,
                          AuthorAdminModeratorOrReadOnly, SuperUser)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReadOnlyTitleSerializer,
                          ReviewSerializer, SendConfirmationCodeSerializer,
                          TitleSerializer, UserSelfSerializer, UserSerializer,
                          UserSignUpSerializer)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [Admin, SuperUser]
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def get_or_patch_self(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = UserSelfSerializer(user, many=False)
            return Response(serializer.data)
        serializer = UserSelfSerializer(user, partial=True, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    """
    Функция обрабатывает POST-запрос для регистрации нового пользователя и
    получаения кода подтверждения, который необходим для получения JWT-токена.
    """
    username = request.data.get('username')
    email = request.data.get('email')
    user = User.objects.filter(
        username=request.data.get('username'),
        email=request.data.get('email')
    ).first()
    if user is None:
        serializer = SendConfirmationCodeSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
    token = default_token_generator.make_token(user)
    User.objects.filter(email=email).update(confirmation_code=token)
    send_mail(
        subject='Ваш код подтверждения',
        message=f'Ваш код подтверждения: {token}',
        from_email=settings.EMAIL,
        recipient_list=[email],
    )

    return Response(
        {"username": username, "email": email}, status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_token(request):
    """
    Функция обрабатывает POST-запрос для получаения JWT-токена.
    """
    serializer = UserSignUpSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        user = get_object_or_404(User, username=request.data.get('username'))
        token = request.data.get('confirmation_code')
    if not default_token_generator.check_token(user, token):
        message = {'confirmation_code': 'Неверный код подтверждения'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    message = {'token': AccessToken.for_user(user)}
    return Response(message, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = (
        Title.objects.all().annotate(Avg("reviews__score"))
    )
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()


def send_email(email):
    user = get_object_or_404(User, email=email)
    confirmation_code = default_token_generator.make_token(user)
    User.objects.filter(email=email).update(
        confirmation_code=confirmation_code
    )
    send_mail(
        subject='Ваш код подтверждения',
        message=f'Ваш код подтверждения: {confirmation_code}',
        from_email=settings.EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

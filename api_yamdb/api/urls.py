from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    GenreViewSet,
    TitleViewSet,
    UsersViewSet,
    CommentViewSet,
    ReviewViewSet,
    send_token,
    sign_up,
)


v1_router = DefaultRouter()
v1_router.register('categories', CategoryViewSet)
v1_router.register('genres', GenreViewSet)
v1_router.register('titles', TitleViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
v1_router.register('users', UsersViewSet, basename='users')

authpatterns = [
    path('signup/', sign_up, name='sign_up'),
    path('token/', send_token, name='send_token')
]

urlpatterns = [
    path('v1/auth/', include(authpatterns)),
    path('v1/', include(v1_router.urls)),
]

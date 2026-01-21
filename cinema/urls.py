from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'movies', views.MovieViewSet)
router.register(r'cinemas', views.CinemaViewSet)
router.register(r'screenings', views.ScreeningViewSet)
router.register(r'tickets', views.TicketViewSet)
router.register(r'reviews', views.ReviewViewSet)
router.register(r'genres', views.GenreViewSet)
router.register(r'persons', views.PersonViewSet)
router.register(r'halls', views.HallViewSet)
router.register(r'user', views.UserViewSet)

# URL паттерны
urlpatterns = [
    path('', include(router.urls)),
    # Дополнительные URL для аутентификации
    path('auth/', include('rest_framework.urls')),
]

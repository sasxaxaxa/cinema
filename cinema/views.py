from django.shortcuts import render
from django.db.models import Q, Avg, Count, F, Sum
from django.utils import timezone
from datetime import timedelta

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import django_filters

from .models import (
    Cinema, Hall, Genre, Person, Movie, Screening,
    Ticket, Review, UserFavorite
)
from .permissions import IsAdminOrReadOnly, IsAdminUser
from .serializers import (
    CinemaSerializer, HallSerializer, GenreSerializer,
    PersonSerializer, MovieSerializer, ScreeningSerializer,
    TicketSerializer, ReviewSerializer, UserFavoriteSerializer,
    UserSerializer
)
from .filters import MovieFilter, ScreeningFilter, TicketFilter, ReviewFilter


# ============ READ OPERATIONS (GET) ============

class MovieViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для фильмов
    """
    queryset = Movie.objects.filter(is_active=True).order_by('-release_date')
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MovieFilter
    search_fields = ['title', 'original_title', 'description', 'country']
    ordering_fields = ['title', 'release_date', 'duration_minutes', 'imdb_rating', 'kinopoisk_rating']

    def get_queryset(self):
        """
        1. Фильтр по текущему аутентифицированному пользователю - автоматически в get_queryset
        2. Фильтр по именованным аргументам в URL - например, ?owner_id=1
        3. Фильтр по GET параметрам - например, ?name=пицца&min_price=100
        4. DjangoFilterBackend - через filterset_class
        5. SearchFilter - поиск по полям
        """
        queryset = Movie.objects.filter(is_active=True)

        # 1. Фильтр по текущему аутентифицированному пользователю (для избранных)
        if self.request.user.is_authenticated:
            # Можно добавить фильтр для фильмов в избранном пользователя
            pass

        # 2. Фильтр по именованным аргументам в URL
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)

        person_id = self.request.query_params.get('person_id')
        if person_id:
            queryset = queryset.filter(
                Q(persons__id=person_id) &
                Q(movieperson__role_in_movie__in=['actor', 'director'])
            ).distinct()

        # 3. Фильтр по GET параметрам
        title_contains = self.request.query_params.get('title_contains')
        if title_contains:
            queryset = queryset.filter(title__icontains=title_contains)

        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)

        # Сложные Q запросы для фильтрации
        # Фильмы с высоким рейтингом И недавнего выпуска И с субтитрами в сеансах
        if self.request.query_params.get('premium') == 'true':
            queryset = queryset.filter(
                Q(imdb_rating__gte=7.0) &
                Q(release_date__year__gte=2020) &
                Q(screening__has_subtitles=True)
            ).distinct()

        # Фильмы для семейного просмотра (низкий возрастной рейтинг И короткие)
        if self.request.query_params.get('family_friendly') == 'true':
            queryset = queryset.filter(
                Q(age_rating__in=['0+', '6+', '12+']) &
                Q(duration_minutes__lte=120)
            )

        return queryset.order_by('-release_date')

    @action(detail=True, methods=['get'])
    def screenings(self, request, pk=None):
        """Получить все сеансы для фильма"""
        movie = self.get_object()
        screenings = Screening.objects.filter(movie=movie, is_active=True)
        serializer = ScreeningSerializer(screenings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Получить все отзывы для фильма"""
        movie = self.get_object()
        reviews = Review.objects.filter(movie=movie, is_approved=True)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def top_rated(self, request):
        """Получить топ-рейтинговые фильмы"""
        queryset = self.get_queryset().annotate(
            avg_rating=(F('imdb_rating') + F('kinopoisk_rating')) / 2
        ).filter(avg_rating__gte=7.0).order_by('-avg_rating')[:10]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Получить недавно вышедшие фильмы"""
        queryset = self.get_queryset().filter(
            release_date__gte=timezone.now().date() - timedelta(days=365)
        ).order_by('-release_date')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CinemaViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для кинотеатров
    """
    queryset = Cinema.objects.filter(is_active=True)
    serializer_class = CinemaSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=['get'])
    def halls(self, request, pk=None):
        """Получить все залы кинотеатра"""
        cinema = self.get_object()
        halls = Hall.objects.filter(cinema=cinema)
        serializer = HallSerializer(halls, many=True)
        return Response(serializer.data)


class ScreeningViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для сеансов
    """
    queryset = Screening.objects.filter(is_active=True).order_by('start_time')
    serializer_class = ScreeningSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ScreeningFilter
    search_fields = ['movie__title', 'hall__name', 'hall__cinema__name']
    ordering_fields = ['start_time', 'end_time', 'base_price', 'movie__title']

    def get_queryset(self):
        """
        Реализация 5 видов фильтрации для сеансов
        """
        queryset = Screening.objects.filter(is_active=True)

        # 1. Фильтр по текущему аутентифицированному пользователю
        if self.request.user.is_authenticated:
            # Показывать только сеансы с доступными билетами
            pass

        # 2. Фильтр по именованным аргументам в URL
        cinema_id = self.request.query_params.get('cinema_id')
        if cinema_id:
            queryset = queryset.filter(hall__cinema__id=cinema_id)

        hall_id = self.request.query_params.get('hall_id')
        if hall_id:
            queryset = queryset.filter(hall__id=hall_id)

        # 3. Фильтр по GET параметрам
        today = self.request.query_params.get('today')
        if today == 'true':
            queryset = queryset.filter(
                start_time__date=timezone.now().date()
            )

        tomorrow = self.request.query_params.get('tomorrow')
        if tomorrow == 'true':
            queryset = queryset.filter(
                start_time__date=timezone.now().date() + timedelta(days=1)
            )

        weekend = self.request.query_params.get('weekend')
        if weekend == 'true':
            queryset = queryset.filter(
                start_time__week_day__in=[1, 7]  # Воскресенье=1, Суббота=7
            )

        # Сложные Q запросы
        # Доступные сеансы (не в прошлом И есть свободные места)
        if self.request.query_params.get('available') == 'true':
            queryset = queryset.filter(
                Q(start_time__gte=timezone.now()) &
                Q(ticket__isnull=True)  # Упрощенная проверка
            ).distinct()

        # Вечерние сеансы (после 18:00)
        if self.request.query_params.get('evening') == 'true':
            queryset = queryset.filter(
                Q(start_time__hour__gte=18)
            )

        return queryset.order_by('start_time')

    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Получить все билеты на сеанс"""
        screening = self.get_object()
        tickets = Ticket.objects.filter(screening=screening)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Получить предстоящие сеансы"""
        queryset = self.get_queryset().filter(
            start_time__gte=timezone.now()
        )[:20]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_movie(self, request):
        """Получить сеансы сгруппированные по фильмам"""
        movie_id = request.query_params.get('movie_id')
        if not movie_id:
            return Response({'error': 'movie_id parameter is required'}, status=400)

        screenings = self.get_queryset().filter(movie_id=movie_id)
        serializer = self.get_serializer(screenings, many=True)
        return Response(serializer.data)


# ============ CREATE/UPDATE/DELETE OPERATIONS ============

class ReviewViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для отзывов
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReviewFilter
    search_fields = ['title', 'text', 'movie__title', 'user__username']
    ordering_fields = ['created_at', 'rating', 'likes_count']

    def get_queryset(self):
        """
        Реализация 5 видов фильтрации для отзывов
        """
        queryset = Review.objects.all()

        # 1. Фильтр по текущему аутентифицированному пользователю
        if not self.request.user.is_staff:
            # Обычные пользователи видят только одобренные отзывы
            queryset = queryset.filter(is_approved=True)

        # 2. Фильтр по именованным аргументам в URL
        movie_id = self.request.query_params.get('movie_id')
        if movie_id:
            queryset = queryset.filter(movie__id=movie_id)

        # 3. Фильтр по GET параметрам
        approved_only = self.request.query_params.get('approved_only')
        if approved_only == 'true':
            queryset = queryset.filter(is_approved=True)

        my_reviews = self.request.query_params.get('my_reviews')
        if my_reviews == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        # Сложные Q запросы
        # Высокорейтинговые отзывы (рейтинг >= 8)
        if self.request.query_params.get('high_rated') == 'true':
            queryset = queryset.filter(
                Q(rating__gte=8) &
                Q(is_approved=True)
            )

        # Популярные отзывы (много лайков)
        if self.request.query_params.get('popular') == 'true':
            queryset = queryset.filter(
                Q(likes_count__gte=10) &
                Q(is_approved=True)
            )

        # Недавние отзывы (за последний месяц)
        if self.request.query_params.get('recent') == 'true':
            queryset = queryset.filter(
                Q(created_at__gte=timezone.now() - timedelta(days=30)) &
                Q(is_approved=True)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя при создании отзыва"""
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """Разрешаем редактирование только своим отзывам"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Вы не можете редактировать чужой отзыв'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Разрешаем удаление только своих отзывов"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'error': 'Вы не можете удалить чужой отзыв'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Одобрить отзыв (только для модераторов)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Недостаточно прав для одобрения отзыва'},
                status=status.HTTP_403_FORBIDDEN
            )

        review = self.get_object()
        review.is_approved = True
        review.save()

        return Response({'message': 'Отзыв одобрен'})

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Поставить лайк отзыву"""
        review = self.get_object()
        review.likes_count += 1
        review.save()

        return Response({'message': 'Лайк добавлен', 'likes_count': review.likes_count})


class TicketViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для билетов
    """
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TicketFilter
    search_fields = ['screening__movie__title', 'screening__hall__cinema__name', 'user__username']
    ordering_fields = ['created_at', 'final_price', 'purchased_at']

    def get_queryset(self):
        """
        Реализация 5 видов фильтрации для билетов
        """
        # 1. Фильтр по текущему аутентифицированному пользователю - автоматически
        queryset = Ticket.objects.filter(user=self.request.user)

        # 2. Фильтр по именованным аргументам в URL
        screening_id = self.request.query_params.get('screening_id')
        if screening_id:
            queryset = queryset.filter(screening__id=screening_id)

        # 3. Фильтр по GET параметрам
        status_filter = self.request.query_params.get('status_filter')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)

        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)

        # Сложные Q запросы
        # Активные билеты (не отменены и не использованы)
        if self.request.query_params.get('active') == 'true':
            queryset = queryset.filter(
                Q(status__in=['booked', 'paid'])
            )

        # Дорогие билеты (выше средней цены)
        if self.request.query_params.get('expensive') == 'true':
            avg_price = Ticket.objects.filter(user=self.request.user).aggregate(avg=Avg('final_price'))['avg']
            if avg_price:
                queryset = queryset.filter(final_price__gt=avg_price)

        # Билеты на сегодня
        if self.request.query_params.get('today') == 'true':
            queryset = queryset.filter(
                Q(screening__start_time__date=timezone.now().date())
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя при покупке билета"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Получить все билеты текущего пользователя (дублирует get_queryset)"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Получить статистику по билетам пользователя"""
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_tickets=Count('id'),
            total_spent=Sum('final_price'),
            avg_price=Avg('final_price')
        )
        return Response(stats)


class UserFavoriteViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для избранных фильмов
    """
    queryset = UserFavorite.objects.all()
    serializer_class = UserFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Пользователь видит только свои избранные"""
        return UserFavorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя"""
        serializer.save(user=self.request.user)


# ============ SIMPLE READ-ONLY VIEWSETS ============

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class PersonViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение персон"""
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class HallViewSet(viewsets.ReadOnlyModelViewSet):
    """Только чтение залов"""
    queryset = Hall.objects.all()
    serializer_class = HallSerializer


# ============ USER MANAGEMENT ============

class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD операции для пользователей (регистрация, профиль)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Регистрация нового пользователя"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Создаем пользователя
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            password=request.data.get('password')
        )

        return Response({
            'message': 'Пользователь успешно создан',
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Получить профиль текущего пользователя"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

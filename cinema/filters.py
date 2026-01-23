import django_filters
from django.db.models import Q
from .models import Movie, Screening, Ticket, Review


class MovieFilter(django_filters.FilterSet):
    """Фильтр для фильмов"""

    min_price = django_filters.NumberFilter(
        field_name='screening__base_price',
        lookup_expr='gte',
        distinct=True,
        label='Минимальная цена сеанса'
    )

    max_price = django_filters.NumberFilter(
        field_name='screening__base_price',
        lookup_expr='lte',
        distinct=True,
        label='Максимальная цена сеанса'
    )

    genre = django_filters.CharFilter(
        field_name='genres__name',
        lookup_expr='icontains',
        label='Жанры (название содержит)'
    )

    year = django_filters.NumberFilter(
        field_name='release_date',
        lookup_expr='year',
        label='Год выпуска'
    )

    age_rating = django_filters.CharFilter(
        field_name='age_rating',
        lookup_expr='icontains',
        label='Возрастной рейтинг содержит'
    )

    min_rating = django_filters.NumberFilter(
        field_name='imdb_rating',
        lookup_expr='gte',
        label='Рейтинг IMDb (от)'
    )

    max_rating = django_filters.NumberFilter(
        field_name='imdb_rating',
        lookup_expr='lte',
        label='Рейтинг IMDb (до)'
    )

    duration_minutes_gte = django_filters.NumberFilter(
        field_name='duration_minutes',
        lookup_expr='gte',
        label='Минимальная длительность (мин)'
    )

    duration_minutes_lte = django_filters.NumberFilter(
        field_name='duration_minutes',
        lookup_expr='lte',
        label='Максимальная длительность (мин)'
    )

    kinopoisk_rating_gte = django_filters.NumberFilter(
        field_name='kinopoisk_rating',
        lookup_expr='gte',
        label='Рейтинг Кинопоиска (от)'
    )

    kinopoisk_rating_lte = django_filters.NumberFilter(
        field_name='kinopoisk_rating',
        lookup_expr='lte',
        label='Рейтинг Кинопоиска (до)'
    )

    title = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Название содержит'
    )

    country = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Страна содержит'
    )

    class Meta:
        model = Movie
        fields = ['is_active']

class ScreeningFilter(django_filters.FilterSet):
    """Фильтр для сеансов"""
    movie_title = django_filters.CharFilter(field_name='movie__title', lookup_expr='icontains')
    hall_name = django_filters.CharFilter(field_name='hall__name', lookup_expr='icontains')
    cinema_city = django_filters.CharFilter(field_name='hall__cinema__city', lookup_expr='icontains')
    format = django_filters.CharFilter(field_name='format')
    language = django_filters.CharFilter(field_name='language')
    min_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='base_price', lookup_expr='lte')
    start_date = django_filters.DateFilter(field_name='start_time', lookup_expr='date__gte')
    end_date = django_filters.DateFilter(field_name='start_time', lookup_expr='date__lte')
    has_subtitles = django_filters.BooleanFilter(field_name='has_subtitles')

    class Meta:
        model = Screening
        fields = ['format', 'language', 'has_subtitles', 'is_active']


class TicketFilter(django_filters.FilterSet):
    """Фильтр для билетов"""
    movie_title = django_filters.CharFilter(field_name='screening__movie__title', lookup_expr='icontains')
    cinema_name = django_filters.CharFilter(field_name='screening__hall__cinema__name', lookup_expr='icontains')
    ticket_type = django_filters.CharFilter(field_name='ticket_type')
    status = django_filters.CharFilter(field_name='status')
    min_price = django_filters.NumberFilter(field_name='final_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='final_price', lookup_expr='lte')
    purchase_date = django_filters.DateFilter(field_name='purchased_at', lookup_expr='date')

    class Meta:
        model = Ticket
        fields = ['ticket_type', 'status']


class ReviewFilter(django_filters.FilterSet):
    """Фильтр для отзывов"""
    movie_title = django_filters.CharFilter(field_name='movie__title', lookup_expr='icontains')
    user_username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    rating = django_filters.NumberFilter(field_name='rating')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')
    is_approved = django_filters.BooleanFilter(field_name='is_approved')
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Review
        fields = ['rating', 'is_approved']

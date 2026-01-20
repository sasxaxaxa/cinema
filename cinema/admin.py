from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import (
    Cinema, Hall, Genre, Person, Movie, MovieGenre,
    MoviePerson, Screening, Ticket, Review, UserFavorite
)
from import_export.admin import ImportExportModelAdmin, ImportExportMixin
from import_export import resources, fields
from simple_history.admin import SimpleHistoryAdmin


class MovieResource(resources.ModelResource):
    """Ресурс экспорта фильмов (только с ценой >= 100)"""
    genres_list = fields.Field()
    duration_formatted = fields.Field()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'original_title', 'release_date', 'duration_minutes',
                  'age_rating', 'country', 'imdb_rating', 'kinopoisk_rating', 'is_active',
                  'genres_list', 'duration_formatted')

    def get_export_queryset(self):
        """Экспорт только фильмов с ценой >= 100 рублей в сеансах"""
        return Movie.objects.filter(
            Q(is_active=True) &
            Q(screening__base_price__gte=100)
        ).distinct()

    def dehydrate_genres_list(self, obj):
        """Форматирование списка жанров"""
        return ', '.join([genre.name for genre in obj.genres.all()])

    def dehydrate_duration_formatted(self, obj):
        """Форматирование длительности"""
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        return f'{hours}ч {minutes}мин'


class TicketResource(resources.ModelResource):
    """Ресурс экспорта билетов (только завершенные за последний месяц)"""
    movie_title = fields.Field()
    cinema_name = fields.Field()
    screening_date = fields.Field()
    status_display = fields.Field()

    class Meta:
        model = Ticket
        fields = ('id', 'user__username', 'final_price', 'ticket_type',
                 'status', 'seat_row', 'seat_number', 'created_at', 'purchased_at',
                 'movie_title', 'cinema_name', 'screening_date', 'status_display')

    def get_export_queryset(self):
        """Экспорт только завершенных билетов за последний месяц"""
        last_month = timezone.now() - timedelta(days=30)
        return Ticket.objects.filter(
            Q(status__in=['paid', 'used']) &
            Q(created_at__gte=last_month)
        )

    def dehydrate_movie_title(self, obj):
        """Название фильма"""
        return obj.screening.movie.title

    def dehydrate_cinema_name(self, obj):
        """Название кинотеатра"""
        return obj.screening.hall.cinema.name

    def dehydrate_screening_date(self, obj):
        """Дата и время сеанса"""
        return obj.screening.start_time.strftime('%d.%m.%Y %H:%M')

    def dehydrate_status_display(self, obj):
        """Человеко-читаемый статус"""
        status_map = {
            'booked': 'Забронирован',
            'paid': 'Оплачен',
            'cancelled': 'Отменен',
            'used': 'Использован'
        }
        return status_map.get(obj.status, obj.status)


# 1. HallInline для Cinema (уже есть)
class HallInline(admin.TabularInline):
    model = Hall
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


# 2. MovieGenreInline для Movie (уже есть)
class MovieGenreInline(admin.TabularInline):
    model = MovieGenre
    extra = 0
    raw_id_fields = ('genre',)


# 3. MoviePersonInline для Movie (уже есть)
class MoviePersonInline(admin.TabularInline):
    model = MoviePerson
    extra = 0
    raw_id_fields = ('person',)


# 4. ScreeningInline для Hall (НОВАЯ настройка)
class ScreeningInline(admin.TabularInline):
    model = Screening
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('movie',)


# 5. TicketInline для Screening (НОВАЯ настройка)
class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)


@admin.register(Cinema)
class CinemaAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('name', 'city', 'is_active', 'created_at', 'halls_count')
    list_filter = ('city', 'is_active', 'created_at')
    search_fields = ('name', 'city', 'address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [HallInline]
    list_display_links = ('name',)
    date_hierarchy = 'created_at'

    @admin.display(description='Кол-во залов', ordering='halls_count')
    def halls_count(self, obj):
        return obj.hall_set.count()


@admin.register(Hall)
class HallAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('name', 'cinema', 'hall_type', 'capacity', 'total_rows', 'total_seats_per_row', 'created_at')
    list_filter = ('hall_type', 'cinema__city', 'created_at')
    search_fields = ('name', 'cinema__name')
    raw_id_fields = ('cinema',)
    readonly_fields = ('created_at', 'updated_at')
    list_display_links = ('name',)
    inlines = [ScreeningInline]
    date_hierarchy = 'created_at'

    @admin.display(description='Вместимость', ordering='capacity')
    def capacity(self, obj):
        return obj.total_rows * obj.total_seats_per_row


@admin.register(Genre)
class GenreAdmin(ImportExportModelAdmin):
    list_display = ('name', 'movies_count', 'description_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    list_display_links = ('name',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    @admin.display(description='Кол-во фильмов')
    def movies_count(self, obj):
        return obj.movie_set.count()

    @admin.display(description='Описание (кратко)')
    def description_short(self, obj):
        if obj.description and len(obj.description) > 50:
            return f'{obj.description[:50]}...'
        return obj.description or '-'


@admin.register(Person)
class PersonAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('full_name', 'birth_date', 'movies_count', 'created_at')
    search_fields = ('full_name',)
    readonly_fields = ('created_at', 'updated_at')
    list_display_links = ('full_name',)
    date_hierarchy = 'created_at'

    @admin.display(description='Кол-во фильмов')
    def movies_count(self, obj):
        return obj.movie_set.count()


@admin.register(Movie)
class MovieAdmin(SimpleHistoryAdmin, ImportExportMixin, admin.ModelAdmin):
    resource_class = MovieResource
    list_display = ('title', 'release_date', 'duration_display', 'age_rating', 'is_active', 'created_at')
    list_filter = ('age_rating', 'is_active', 'release_date', 'created_at')
    search_fields = ('title', 'original_title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('genres', 'persons')
    date_hierarchy = 'release_date'
    inlines = [MovieGenreInline, MoviePersonInline]
    list_display_links = ('title',)
    raw_id_fields = ()

    @admin.display(description='Длительность', ordering='duration_minutes')
    def duration_display(self, obj):
        hours = obj.duration_minutes // 60
        minutes = obj.duration_minutes % 60
        return f'{hours}ч {minutes}мин'


@admin.register(Screening)
class ScreeningAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('movie', 'hall', 'start_time', 'end_time', 'duration', 'base_price', 'is_active')
    list_filter = ('format', 'language', 'is_active', 'start_time')
    search_fields = ('movie__title', 'hall__name')
    raw_id_fields = ('movie', 'hall')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_time'
    list_display_links = ('movie',)
    inlines = [TicketInline]

    @admin.display(description='Длительность сеанса')
    def duration(self, obj):
        duration = obj.end_time - obj.start_time
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        return f'{hours}ч {minutes}мин'


@admin.register(Ticket)
class TicketAdmin(SimpleHistoryAdmin, ImportExportMixin, admin.ModelAdmin):
    resource_class = TicketResource
    list_display = ('id', 'screening', 'user', 'seat_display', 'ticket_type', 'status', 'final_price', 'created_at')
    list_filter = ('status', 'ticket_type', 'created_at')
    search_fields = ('user__username', 'screening__movie__title')
    raw_id_fields = ('screening', 'user')
    readonly_fields = ('created_at', 'updated_at', 'purchased_at')
    list_display_links = ('id',)
    date_hierarchy = 'created_at'

    @admin.display(description='Место')
    def seat_display(self, obj):
        return f'Ряд {obj.seat_row}, Место {obj.seat_number}'


@admin.register(Review)
class ReviewAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
    list_display = ('title', 'movie', 'user', 'rating', 'is_approved', 'created_at', 'short_text')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('title', 'text', 'movie__title', 'user__username')
    raw_id_fields = ('movie', 'user')
    readonly_fields = ('created_at', 'updated_at', 'likes_count')
    list_display_links = ('title',)
    date_hierarchy = 'created_at'

    @admin.display(description='Текст (кратко)')
    def short_text(self, obj):
        if len(obj.text) > 50:
            return f'{obj.text[:50]}...'
        return obj.text


@admin.register(UserFavorite)
class UserFavoriteAdmin(ImportExportModelAdmin):
    list_display = ('user', 'movie', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'movie__title')
    raw_id_fields = ('user', 'movie')
    readonly_fields = ('created_at',)
    list_display_links = ('user',)
    date_hierarchy = 'created_at'


@admin.register(MovieGenre)
class MovieGenreAdmin(admin.ModelAdmin):
    list_display = ('movie', 'genre', 'created_at')
    list_filter = ('genre', 'created_at')
    search_fields = ('movie__title', 'genre__name')
    raw_id_fields = ('movie', 'genre')
    list_display_links = ('movie',)
    date_hierarchy = 'created_at'


@admin.register(MoviePerson)
class MoviePersonAdmin(ImportExportModelAdmin):
    list_display = ('movie', 'person', 'role_in_movie', 'character_name', 'created_at')
    list_filter = ('role_in_movie', 'created_at')
    search_fields = ('movie__title', 'person__full_name', 'character_name')
    raw_id_fields = ('movie', 'person')
    list_display_links = ('movie',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
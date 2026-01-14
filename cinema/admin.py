from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Cinema, Hall, Genre, Person, Movie, MovieGenre,
    MoviePerson, Screening, Ticket, Review, UserFavorite
)
from import_export.admin import ImportExportModelAdmin
from simple_history.admin import SimpleHistoryAdmin


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
    list_display = ('name', 'movies_count', 'created_at')
    search_fields = ('name',)
    list_display_links = ('name',)
    date_hierarchy = 'created_at'

    @admin.display(description='Кол-во фильмов')
    def movies_count(self, obj):
        return obj.movie_set.count()


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
class MovieAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
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
class TicketAdmin(SimpleHistoryAdmin, ImportExportModelAdmin):
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
class MoviePersonAdmin(admin.ModelAdmin):
    list_display = ('movie', 'person', 'role_in_movie', 'character_name', 'created_at')
    list_filter = ('role_in_movie', 'created_at')
    search_fields = ('movie__title', 'person__full_name', 'character_name')
    raw_id_fields = ('movie', 'person')
    list_display_links = ('movie',)
    date_hierarchy = 'created_at'
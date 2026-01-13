from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, default='user')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Cinema(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()
    description = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    contact_email = models.EmailField(blank=True)
    facilities = models.JSONField(default=dict)
    geo_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    geo_lon = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Кинотеатр'
        verbose_name_plural = 'Кинотеатры'

    def __str__(self):
        return f'{self.name} ({self.city})'


class Hall(models.Model):
    HALL_TYPES = [
        ('standard', 'Стандарт'),
        ('imax', 'IMAX'),
        ('vip', 'VIP'),
    ]

    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    hall_type = models.CharField(max_length=50, choises=HALL_TYPES, default='standard')
    total_rows = models.PositiveIntegerField()
    total_seats_per_row = models.PositiveIntegerField()
    schema_image_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = ''
        verbose_name_plural = ''

    def __str__(self):
        return f'{self.name} ({self.cinema.name})'


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=200)
    photo_url = models.CharField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Персона'
        verbose_name_plural = 'Персоны'

    def __str__(self):
        return self.full_name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    release_date = models.DateField()
    age_rating = models.CharField(max_length=10)
    country = models.CharField(max_length=100, blank=True)
    poster_url = models.CharField(max_length=500)
    trailer_url = models.CharField(max_length=500, blank=True)
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    kinopoisk_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    genres = models.ManyToManyField(Genre, through='MovieGenre')
    persons = models.ManyToManyField(Person, through='MoviePerson')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'

    def __str__(self):
        return self.title

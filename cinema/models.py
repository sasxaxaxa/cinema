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
    hall_type = models.CharField(max_length=50, choices=HALL_TYPES, default='standard')
    total_rows = models.PositiveIntegerField()
    total_seats_per_row = models.PositiveIntegerField()
    schema_image_path = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Зал'
        verbose_name_plural = 'Залы'

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


class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Жанр фильма'
        verbose_name_plural = 'Жанры фильма'
        unique_together = ['movie', 'genre']


class MoviePerson(models.Model):
    ROLES = [
        ('actor', 'Актер'),
        ('director', 'Режиссер'),
        ('producer', 'Продюсер'),
        ('screenwriter', 'Сценарист'),
        ('operator', 'Оператор'),
    ]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role_in_movie = models.CharField(max_length=100, choices=ROLES)
    character_name = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Персонаж фильма'
        verbose_name_plural = 'Персонажи фильма'
        unique_together = ['movie', 'person', 'role_in_movie']


class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    format = models.CharField(max_length=10, default='2D')
    language = models.CharField(max_length=50, default='RU')
    has_subtitles = models.BooleanField(default=False)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сеанс'
        verbose_name_plural = 'Сеансы'

        constraints = [
            models.UniqueConstraint(fields=['hall', 'start_time'], name='unique_screening_time'),
        ]

    def __str__(self):
        return f'{self.movie.title} - {self.start_time}'


class Ticket(models.Model):
    TICKET_TYPES = [
        ('adult', 'Взрослый'),
        ('child', 'Детский'),
        ('student', 'Студенческий'),
    ]

    STATUSES = [
        ('booked', 'Забронирован'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
        ('used', 'Использован'),
    ]

    screening = models.ForeignKey(Screening, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat_row = models.PositiveIntegerField()
    seat_number = models.PositiveIntegerField()
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES, default='adult')
    status = models.CharField(max_length=20, choices=STATUSES, default='booked')
    qr_code_path = models.CharField(max_length=500, blank=True)
    purchased_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Билет'
        verbose_name_plural = 'Билеты'
        unique_together = ['screening', 'seat_row', 'seat_number']

    def __str__(self):
        return f'Билет {self.id}'


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    text = models.TextField()
    is_approved = models.BooleanField(default=False)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рецензия'
        verbose_name_plural = 'Рецензии'
        unique_together = ['movie', 'user']

    def __str__(self):
        return f'{self.title} - {self.user.email}'


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        unique_together = ['user', 'movie']

    def __str__(self):
        return f'{self.user.email} - {self.movie.title}'

from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

from simple_history.models import HistoricalRecords


class Cinema(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    city = models.CharField(max_length=100, verbose_name="Город")
    address = models.TextField(verbose_name="Адрес")
    description = models.TextField(blank=True, verbose_name="Описание")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    contact_email = models.EmailField(blank=True, verbose_name="Email")
    facilities = models.JSONField(default=dict, verbose_name="Удобства")
    geo_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, verbose_name="Широта")
    geo_lon = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, verbose_name="Долгота")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Кинотеатр"
        verbose_name_plural = "Кинотеатры"
        ordering = ['city', 'name']

    def __str__(self):
        return f'{self.name} ({self.city})'


class Hall(models.Model):
    HALL_TYPES = [
        ('standard', 'Стандарт'),
        ('imax', 'IMAX'),
        ('vip', 'VIP'),
    ]

    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, verbose_name="Кинотеатр")
    name = models.CharField(max_length=100, verbose_name="Название")
    hall_type = models.CharField(max_length=50, choices=HALL_TYPES, default='standard', verbose_name="Тип зала")
    total_rows = models.PositiveIntegerField(verbose_name="Количество рядов")
    total_seats_per_row = models.PositiveIntegerField(verbose_name="Мест в ряду")
    schema_image_path = models.CharField(max_length=500, blank=True, verbose_name="Схема зала")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"
        ordering = ['cinema', 'name']

    def __str__(self):
        return f'{self.name} ({self.cinema.name})'


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        ordering = ['name']

    def __str__(self):
        return self.name


class Person(models.Model):
    full_name = models.CharField(max_length=200, verbose_name="Полное имя")
    photo_url = models.CharField(max_length=500, blank=True, verbose_name="Фото")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")
    biography = models.TextField(blank=True, verbose_name="Биография")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Персона"
        verbose_name_plural = "Персоны"
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Movie(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название")
    original_title = models.CharField(max_length=200, blank=True, verbose_name="Оригинальное название")
    description = models.TextField(blank=True, verbose_name="Описание")
    duration_minutes = models.PositiveIntegerField(verbose_name="Продолжительность (мин)")
    release_date = models.DateField(verbose_name="Дата выхода")
    age_rating = models.CharField(max_length=10, verbose_name="Возрастной рейтинг")
    country = models.CharField(max_length=100, blank=True, verbose_name="Страна")
    poster_url = models.CharField(max_length=500, verbose_name="Постер")
    trailer_url = models.CharField(max_length=500, blank=True, verbose_name="Трейлер")
    imdb_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Рейтинг IMDb")
    kinopoisk_rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name="Рейтинг Кинопоиск")
    genres = models.ManyToManyField(Genre, through='MovieGenre', verbose_name="Жанры")
    persons = models.ManyToManyField(Person, through='MoviePerson', verbose_name="Персоны")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Фильм"
        verbose_name_plural = "Фильмы"
        ordering = ['-release_date', 'title']

    def __str__(self):
        return self.title


class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name="Жанр")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Жанр фильма"
        verbose_name_plural = "Жанры фильма"
        unique_together = ['movie', 'genre']

    def __str__(self):
        return f'{self.movie.title} - {self.genre.name}'


class MoviePerson(models.Model):
    ROLES = [
        ('actor', 'Актер'),
        ('director', 'Режиссер'),
        ('producer', 'Продюсер'),
        ('screenwriter', 'Сценарист'),
        ('operator', 'Оператор'),
    ]

    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="Персона")
    role_in_movie = models.CharField(max_length=100, choices=ROLES, verbose_name="Роль в фильме")
    character_name = models.CharField(max_length=200, blank=True, verbose_name="Имя персонажа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Персонаж фильма"
        verbose_name_plural = "Персонажи фильма"
        unique_together = ['movie', 'person', 'role_in_movie']

    def __str__(self):
        return f'{self.person.full_name} ({self.role_in_movie}) в "{self.movie.title}"'


class Screening(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, verbose_name="Зал")
    start_time = models.DateTimeField(verbose_name="Время начала")
    end_time = models.DateTimeField(verbose_name="Время окончания")
    format = models.CharField(max_length=10, default='2D', verbose_name="Формат")
    language = models.CharField(max_length=50, default='RU', verbose_name="Язык")
    has_subtitles = models.BooleanField(default=False, verbose_name="Субтитры")
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Базовая цена")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('Время окончания сеанса должно быть позже времени начала')

    class Meta:
        verbose_name = "Сеанс"
        verbose_name_plural = "Сеансы"
        ordering = ['start_time']
        constraints = [
            models.UniqueConstraint(fields=['hall', 'start_time'], name='unique_screening_time'),
        ]

    def __str__(self):
        return f'{self.movie.title} - {self.start_time.strftime("%d.%m.%Y %H:%M")}'


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

    screening = models.ForeignKey(Screening, on_delete=models.CASCADE, verbose_name="Сеанс")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    seat_row = models.PositiveIntegerField(verbose_name="Ряд")
    seat_number = models.PositiveIntegerField(verbose_name="Место")
    final_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Итоговая цена")
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES, default='adult', verbose_name="Тип билета")
    status = models.CharField(max_length=20, choices=STATUSES, default='booked', verbose_name="Статус")
    qr_code_path = models.CharField(max_length=500, blank=True, verbose_name="QR-код")
    purchased_at = models.DateTimeField(null=True, blank=True, verbose_name="Время покупки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Билет"
        verbose_name_plural = "Билеты"
        ordering = ['-created_at']
        unique_together = ['screening', 'seat_row', 'seat_number']

    def __str__(self):
        return f'Билет #{self.id}'


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], verbose_name="Рейтинг")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрено")
    likes_count = models.IntegerField(default=0, verbose_name="Лайки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    history = HistoricalRecords()

    class Meta:
        verbose_name = "Рецензия"
        verbose_name_plural = "Рецензии"
        ordering = ['-created_at']
        unique_together = ['movie', 'user']

    def __str__(self):
        return f'{self.title} - {self.user.username}'


class UserFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, verbose_name="Фильм")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        ordering = ['-created_at']
        unique_together = ['user', 'movie']

    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'


class UserProfile(models.Model):
    USER_ROLES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=USER_ROLES,
        default='user',
        verbose_name="Роль"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон"
    )
    profile_picture = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Фото профиля"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def is_admin(self):
        return self.role == 'admin' or self.user.is_superuser

    def is_moderator(self):
        return self.role in ['moderator', 'admin'] or self.user.is_superuser


# Сигналы для автоматического создания профиля
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


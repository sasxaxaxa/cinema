from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cinema.models import (
    Cinema, Hall, Genre, Person, Movie,
    Screening, Ticket, Review, UserFavorite
)
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Создание тестовых данных для кинотеатра'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')

        # Создание жанров
        genres_data = [
            'Боевик', 'Комедия', 'Драма', 'Ужасы', 'Фантастика',
            'Триллер', 'Романтика', 'Анимация', 'Документальный', 'Биография'
        ]

        genres = []
        for genre_name in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=genre_name,
                defaults={'description': f'Описание жанра {genre_name}'}
            )
            genres.append(genre)
            if created:
                self.stdout.write(f'Создан жанр: {genre_name}')

        # Создание персон
        persons_data = [
            ('Леонардо ДиКаприо', 'Актер, продюсер', '1974-11-11'),
            ('Кристофер Нолан', 'Режиссер', '1970-07-30'),
            ('Марго Робби', 'Актриса', '1990-09-02'),
            ('Дени Вильнёв', 'Режиссер', '1967-10-03'),
            ('Скарлетт Йоханссон', 'Актриса', '1984-11-22'),
            ('Мартин Скорсезе', 'Режиссер', '1942-11-17'),
            ('Дженнифер Лоуренс', 'Актриса', '1990-08-15'),
            ('Гильермо дель Торо', 'Режиссер', '1964-10-09'),
        ]

        persons = []
        for name, bio, birth_date in persons_data:
            person, created = Person.objects.get_or_create(
                full_name=name,
                defaults={
                    'biography': bio,
                    'birth_date': birth_date
                }
            )
            persons.append(person)
            if created:
                self.stdout.write(f'Создан персонаж: {name}')

        # Создание кинотеатров
        cinemas_data = [
            ('Кинотеатр "Звезда"', 'Москва', 'ул. Тверская, 1'),
            ('Cinema Park', 'Санкт-Петербург', 'Невский проспект, 50'),
            ('Люкс Кино', 'Екатеринбург', 'ул. Ленина, 25'),
        ]

        cinemas = []
        for name, city, address in cinemas_data:
            cinema, created = Cinema.objects.get_or_create(
                name=name,
                defaults={
                    'city': city,
                    'address': address,
                    'description': f'Современный кинотеатр в {city}',
                    'contact_phone': '+7 999 123-45-67',
                    'contact_email': f'info@{name.lower().replace(" ", "").replace(chr(34), "")}.ru'
                }
            )
            cinemas.append(cinema)
            if created:
                self.stdout.write(f'Создан кинотеатр: {name}')

        # Создание залов
        halls = []
        for cinema in cinemas:
            for i in range(1, 4):  # 3 зала на кинотеатр
                hall, created = Hall.objects.get_or_create(
                    cinema=cinema,
                    name=f'Зал {i}',
                    defaults={
                        'hall_type': random.choice(['standard', 'imax', 'vip']),
                        'total_rows': random.randint(10, 15),
                        'total_seats_per_row': random.randint(15, 20)
                    }
                )
                halls.append(hall)
                if created:
                    self.stdout.write(f'Создан зал: {hall.name} в {cinema.name}')

        # Создание фильмов
        movies_data = [
            ('Дюна', 'Dune', 155, '2021-10-21', '16+', 'США', 8.0, 8.2),
            ('Оппенгеймер', 'Oppenheimer', 180, '2023-07-21', '16+', 'США', 8.3, 8.5),
            ('Барби', 'Barbie', 114, '2023-07-21', '12+', 'США', 6.9, 7.1),
            ('Человек-паук: Нет пути домой', 'Spider-Man: No Way Home', 148, '2021-12-17', '12+', 'США', 8.2, 8.4),
            ('Топ Ган: Мэверик', 'Top Gun: Maverick', 130, '2022-05-27', '12+', 'США', 8.3, 8.5),
        ]

        movies = []
        for title, orig_title, duration, release_date, age_rating, country, imdb, kp in movies_data:
            movie, created = Movie.objects.get_or_create(
                title=title,
                defaults={
                    'original_title': orig_title,
                    'description': f'Описание фильма {title}',
                    'duration_minutes': duration,
                    'release_date': release_date,
                    'age_rating': age_rating,
                    'country': country,
                    'imdb_rating': imdb,
                    'kinopoisk_rating': kp,
                    'poster_url': f'https://example.com/posters/{title.lower().replace(" ", "_")}.jpg',
                    'trailer_url': f'https://youtube.com/watch?v={title.lower().replace(" ", "_")}'
                }
            )
            # Добавляем случайные жанры
            movie.genres.set(random.sample(genres, random.randint(1, 3)))
            # Добавляем случайных персон
            movie.persons.set(random.sample(persons, random.randint(2, 4)))
            movies.append(movie)
            if created:
                self.stdout.write(f'Создан фильм: {title}')

        # Создание пользователей
        users = []
        for i in range(1, 6):
            user, created = User.objects.get_or_create(
                username=f'user{i}',
                defaults={
                    'email': f'user{i}@example.com',
                    'first_name': f'Пользователь{i}',
                    'last_name': f'Тестовый{i}'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
            if created:
                self.stdout.write(f'Создан пользователь: {user.username}')

        # Создание сеансов
        screenings = []
        base_date = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        for movie in movies:
            for hall in random.sample(halls, 2):  # 2 случайных зала
                for day_offset in range(7):  # На 7 дней вперед
                    start_time = base_date + timedelta(days=day_offset, hours=random.randint(10, 22))
                    end_time = start_time + timedelta(minutes=movie.duration_minutes + 15)  # +15 мин на рекламу

                    screening, created = Screening.objects.get_or_create(
                        movie=movie,
                        hall=hall,
                        start_time=start_time,
                        defaults={
                            'end_time': end_time,
                            'format': random.choice(['2D', '3D', 'IMAX']),
                            'language': random.choice(['RU', 'EN']),
                            'has_subtitles': random.choice([True, False]),
                            'base_price': random.randint(200, 800)
                        }
                    )
                    screenings.append(screening)
                    if created:
                        self.stdout.write(f'Создан сеанс: {movie.title} в {hall.name}')

        # Создание билетов
        for user in users:
            # Каждый пользователь покупает 2-5 билетов
            user_screenings = random.sample(screenings, random.randint(2, 5))
            for screening in user_screenings:
                # Выбираем случайное свободное место
                hall = screening.hall
                seat_row = random.randint(1, hall.total_rows)
                seat_number = random.randint(1, hall.total_seats_per_row)

                # Проверяем, что место свободно
                if not Ticket.objects.filter(
                    screening=screening,
                    seat_row=seat_row,
                    seat_number=seat_number
                ).exists():
                    ticket, created = Ticket.objects.get_or_create(
                        screening=screening,
                        user=user,
                        seat_row=seat_row,
                        seat_number=seat_number,
                        defaults={
                            'final_price': screening.base_price + random.randint(-50, 100),
                            'ticket_type': random.choice(['adult', 'child', 'student']),
                            'status': random.choice(['booked', 'paid', 'used'])
                        }
                    )
                    if created:
                        self.stdout.write(f'Создан билет: {user.username} на {screening.movie.title}')

        # Создание отзывов
        for user in users:
            # Каждый пользователь пишет 1-3 отзыва
            user_movies = random.sample(movies, random.randint(1, 3))
            for movie in user_movies:
                # Проверяем, что отзыв еще не написан
                if not Review.objects.filter(movie=movie, user=user).exists():
                    review, created = Review.objects.get_or_create(
                        movie=movie,
                        user=user,
                        defaults={
                            'rating': random.randint(1, 10),
                            'title': f'Отзыв о фильме {movie.title}',
                            'text': f'Очень интересный фильм {movie.title}. Рекомендую всем посмотреть!',
                            'is_approved': random.choice([True, False])
                        }
                    )
                    if created:
                        self.stdout.write(f'Создан отзыв: {user.username} о {movie.title}')

        # Создание избранных фильмов
        for user in users:
            # Каждый пользователь добавляет 1-3 фильма в избранное
            favorite_movies = random.sample(movies, random.randint(1, 3))
            for movie in favorite_movies:
                favorite, created = UserFavorite.objects.get_or_create(
                    user=user,
                    movie=movie
                )
                if created:
                    self.stdout.write(f'Добавлен в избранное: {user.username} - {movie.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Тестовые данные созданы успешно!\n'
                f'Кинотеатров: {Cinema.objects.count()}\n'
                f'Залов: {Hall.objects.count()}\n'
                f'Фильмов: {Movie.objects.count()}\n'
                f'Сеансов: {Screening.objects.count()}\n'
                f'Билетов: {Ticket.objects.count()}\n'
                f'Отзывов: {Review.objects.count()}\n'
                f'Избранных: {UserFavorite.objects.count()}'
            )
        )

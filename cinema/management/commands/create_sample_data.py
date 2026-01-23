from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from cinema.models import (
    Cinema, Hall, Genre, Person, Movie,
    Screening, Ticket, Review, UserFavorite
)
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Создание тестовых данных для кинотеатра'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')

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

        halls = []
        for cinema in cinemas:
            for i in range(1, 4):
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

        movies_data = [
            ('Дюна', 'Dune', 155, '2021-10-21', '16+', 'США', 8.0, 8.2),
            ('Оппенгеймер', 'Oppenheimer', 180, '2023-07-21', '16+', 'США', 8.3, 8.5),
            ('Барби', 'Barbie', 114, '2023-07-21', '12+', 'США', 6.9, 7.1),
            ('Человек-паук: Нет пути домой', 'Spider-Man: No Way Home', 148, '2021-12-17', '12+', 'США', 8.2, 8.4),
            ('Топ Ган: Мэверик', 'Top Gun: Maverick', 130, '2022-05-27', '12+', 'США', 8.3, 8.5),

            ('Крёстный отец', 'The Godfather', 175, '1972-03-24', '18+', 'США', 9.2, 9.0),
            ('Побег из Шоушенка', 'The Shawshank Redemption', 142, '1994-09-23', '16+', 'США', 9.3, 9.1),
            ('Тёмный рыцарь', 'The Dark Knight', 152, '2008-07-18', '16+', 'США', 9.0, 8.9),
            ('Форрест Гамп', 'Forrest Gump', 142, '1994-07-06', '12+', 'США', 8.8, 8.7),
            ('Список Шиндлера', 'Schindler\'s List', 195, '1993-12-15', '18+', 'США', 8.9, 8.8),

            ('Интерстеллар', 'Interstellar', 169, '2014-11-07', '12+', 'США', 8.6, 8.5),
            ('Начало', 'Inception', 148, '2010-07-16', '12+', 'США', 8.8, 8.7),
            ('Матрица', 'The Matrix', 136, '1999-03-31', '16+', 'США', 8.7, 8.6),
            ('Бегущий по лезвию 2049', 'Blade Runner 2049', 163, '2017-10-06', '18+', 'США', 8.0, 8.1),
            ('Звёздные войны: Империя наносит ответный удар', 'Star Wars: The Empire Strikes Back', 124, '1980-05-21',
             '6+', 'США', 8.7, 8.6),

            ('Король Лев', 'The Lion King', 88, '1994-06-24', '0+', 'США', 8.5, 8.4),
            ('Тайна Коко', 'Coco', 105, '2017-11-22', '6+', 'США', 8.4, 8.3),
            ('История игрушек', 'Toy Story', 81, '1995-11-22', '0+', 'США', 8.3, 8.2),
            ('Холодное сердце', 'Frozen', 102, '2013-11-27', '6+', 'США', 7.4, 7.6),
            ('ВАЛЛИ', 'WALL·E', 98, '2008-06-27', '0+', 'США', 8.4, 8.3),

            ('Брат', 'Brat', 100, '1997-12-12', '18+', 'Россия', 8.1, 8.2),
            ('Движение вверх', 'Dvizhenie vverkh', 133, '2017-12-28', '12+', 'Россия', 7.3, 7.4),
            ('Легенда №17', 'Legenda No. 17', 134, '2013-04-18', '12+', 'Россия', 7.3, 7.4),
            ('Притяжение', 'Attraction', 132, '2017-01-26', '12+', 'Россия', 5.3, 5.4),
            ('Он - дракон', 'He\'s a Dragon', 107, '2015-12-03', '12+', 'Россия', 6.4, 6.5),

            ('Мальчишник в Вегасе', 'The Hangover', 100, '2009-06-05', '18+', 'США', 7.7, 7.8),
            ('Однажды в Голливуде', 'Once Upon a Time in Hollywood', 161, '2019-07-26', '18+', 'США', 7.6, 7.7),
            ('Девичник в Вегасе', 'Bridesmaids', 125, '2011-05-13', '18+', 'США', 6.8, 6.9),
            ('Криминальное чтиво', 'Pulp Fiction', 154, '1994-10-14', '18+', 'США', 8.9, 8.8),
            ('Большой Лебовски', 'The Big Lebowski', 117, '1998-03-06', '18+', 'США', 8.1, 8.2),

            ('Зеленая книга', 'Green Book', 130, '2018-11-21', '16+', 'США', 8.2, 8.3),
            ('Форма воды', 'The Shape of Water', 123, '2017-12-01', '18+', 'США', 7.3, 7.4),
            ('Ла-Ла Ленд', 'La La Land', 128, '2016-12-09', '12+', 'США', 8.0, 8.1),
            ('Джокер', 'Joker', 122, '2019-10-04', '18+', 'США', 8.4, 8.5),
            ('Паразиты', 'Parasite', 132, '2019-05-30', '18+', 'Южная Корея', 8.6, 8.5),

            ('Сияние', 'The Shining', 146, '1980-05-23', '18+', 'США', 8.4, 8.3),
            ('Оно', 'It', 135, '2017-09-08', '18+', 'США', 7.3, 7.4),
            ('Пила', 'Saw', 103, '2004-10-29', '18+', 'США', 7.6, 7.7),
            ('Заклятие', 'The Conjuring', 112, '2013-07-19', '18+', 'США', 7.5, 7.6),
            ('Хэллоуин', 'Halloween', 91, '1978-10-25', '18+', 'США', 7.7, 7.8),
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
            movie.genres.set(random.sample(genres, random.randint(1, 3)))
            movie.persons.set(random.sample(persons, random.randint(2, 4)))
            movies.append(movie)
            if created:
                self.stdout.write(f'Создан фильм: {title}')

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

        screenings = []
        base_date = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        base_date_naive = base_date.replace(tzinfo=None)

        for movie in movies:
            for hall in random.sample(halls, 2):
                for day_offset in range(7):
                    start_time_naive = base_date_naive + timedelta(
                        days=day_offset,
                        hours=random.randint(10, 22)
                    )
                    start_time = timezone.make_aware(start_time_naive)

                    end_time = start_time + timedelta(minutes=movie.duration_minutes + 15)

                    try:
                        screening, created = Screening.objects.get_or_create(
                            hall=hall,
                            start_time=start_time,
                            defaults={
                                'movie': movie,
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
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'Ошибка создания сеанса: {e}')
                        )

        for user in users:
            user_screenings = random.sample(screenings, random.randint(2, 5))
            for screening in user_screenings:
                hall = screening.hall
                seat_row = random.randint(1, hall.total_rows)
                seat_number = random.randint(1, hall.total_seats_per_row)

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

        for user in users:
            user_movies = random.sample(movies, random.randint(1, 3))
            for movie in user_movies:
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

        for user in users:
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

#!/usr/bin/env python
import os
import sys
import django
import random

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from cinema.models import *

def main():
    print('=== СОЗДАНИЕ ДОПОЛНИТЕЛЬНЫХ ТЕСТОВЫХ ДАННЫХ ===')

    # Создаем дополнительного обычного пользователя
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Тестовый',
            'last_name': 'Пользователь'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print('✅ Создан пользователь testuser с паролем testpass123')

    # Устанавливаем пароль для admin
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print('✅ Установлен пароль admin123 для пользователя admin')

    # Создаем несколько билетов для тестирования
    screenings = list(Screening.objects.all()[:5])
    users = list(User.objects.filter(is_superuser=False)[:3])

    for i, (screening, user) in enumerate(zip(screenings, users)):
        # Находим свободное место
        existing_tickets = set(Ticket.objects.filter(screening=screening).values_list('seat_row', 'seat_number'))

        # Ищем свободное место
        found = False
        for row in range(1, screening.hall.total_rows + 1):
            for seat in range(1, screening.hall.total_seats_per_row + 1):
                if (row, seat) not in existing_tickets:
                    ticket, created = Ticket.objects.get_or_create(
                        screening=screening,
                        user=user,
                        seat_row=row,
                        seat_number=seat,
                        defaults={
                            'final_price': screening.base_price + random.randint(-50, 100),
                            'ticket_type': random.choice(['adult', 'child', 'student']),
                            'status': random.choice(['booked', 'paid'])
                        }
                    )
                    if created:
                        print(f'✅ Создан билет: {user.username} на "{screening.movie.title}" ряд {row} место {seat}')
                    found = True
                    break
            if found:
                break

    # Создаем отзывы
    movies = list(Movie.objects.all())
    for i, movie in enumerate(movies[:3]):
        user = users[i % len(users)]
        review, created = Review.objects.get_or_create(
            movie=movie,
            user=user,
            defaults={
                'rating': random.randint(7, 10),
                'title': f'Отличный фильм {movie.title}',
                'text': f'Очень понравился фильм {movie.title}. Рекомендую всем посмотреть!',
                'is_approved': True
            }
        )
        if created:
            print(f'✅ Создан отзыв: {user.username} о "{movie.title}" (рейтинг {review.rating})')

    print('\n=== ОБНОВЛЕННАЯ СТАТИСТИКА ===')
    print(f'Пользователи: {User.objects.count()}')
    print(f'Кинотеатры: {Cinema.objects.count()}')
    print(f'Фильмы: {Movie.objects.count()}')
    print(f'Сеансы: {Screening.objects.count()}')
    print(f'Билеты: {Ticket.objects.count()}')
    print(f'Отзывы: {Review.objects.count()}')

if __name__ == '__main__':
    main()

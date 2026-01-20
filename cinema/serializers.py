from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from .models import (
    Cinema, Hall, Genre, Person, Movie, Screening,
    Ticket, Review, UserFavorite, UserProfile
)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role', 'phone_number', 'profile_picture']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_name(self, value):
        """Валидация уникальности названия кинотеатра"""
        if Cinema.objects.filter(name__iexact=value).exists():
            if self.instance and self.instance.name.lower() == value.lower():
                return value
            raise serializers.ValidationError("Кинотеатр с таким названием уже существует.")
        return value

    def validate_contact_phone(self, value):
        """Валидация телефона"""
        if value:
            # Проверка формата телефона (российский формат)
            phone_pattern = r'^(\+7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$'
            if not re.match(phone_pattern, value):
                raise serializers.ValidationError("Неверный формат телефона. Используйте формат: +7 XXX XXX XX XX или 8 XXX XXX XX XX")
        return value

    def validate_address(self, value):
        """Валидация адреса (минимум 10 символов)"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Адрес должен содержать минимум 10 символов.")
        return value


class HallSerializer(serializers.ModelSerializer):
    cinema_name = serializers.CharField(source='cinema.name', read_only=True)

    class Meta:
        model = Hall
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class ScreeningSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    hall_name = serializers.CharField(source='hall.name', read_only=True)

    class Meta:
        model = Screening
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

    def validate_base_price(self, value):
        """Валидация цены (положительная, не более 100000)"""
        if value <= 0:
            raise serializers.ValidationError("Цена должна быть положительной.")
        if value > 100000:
            raise serializers.ValidationError("Цена не может превышать 100 000 рублей.")
        return value

    def validate(self, data):
        """Комплексная валидация"""
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError({
                    'end_time': 'Время окончания сеанса должно быть позже времени начала.'
                })

        return data


class ReviewSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'likes_count']

    def validate_rating(self, value):
        """Валидация рейтинга (от 1 до 10)"""
        if not (1 <= value <= 10):
            raise serializers.ValidationError("Рейтинг должен быть от 1 до 10.")
        return value

    def validate_title(self, value):
        """Валидация заголовка отзыва"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Заголовок должен содержать минимум 3 символа.")
        return value

    def validate_text(self, value):
        """Валидация текста отзыва"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Текст отзыва должен содержать минимум 10 символов.")
        return value


class TicketSerializer(serializers.ModelSerializer):
    screening_details = serializers.CharField(source='screening.__str__', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Ticket
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'purchased_at']

    def validate_final_price(self, value):
        """Валидация цены билета"""
        if value <= 0:
            raise serializers.ValidationError("Цена билета должна быть положительной.")
        if value > 100000:
            raise serializers.ValidationError("Цена билета не может превышать 100 000 рублей.")
        return value

    def validate(self, data):
        """Комплексная валидация билета"""
        screening = data.get('screening')
        seat_row = data.get('seat_row')
        seat_number = data.get('seat_number')

        if screening and seat_row and seat_number:
            # Проверка, что место существует в зале
            hall = screening.hall
            if seat_row > hall.total_rows or seat_number > hall.total_seats_per_row:
                raise serializers.ValidationError({
                    'seat_row': f'Ряд {seat_row} не существует в зале {hall.name}. Максимум рядов: {hall.total_rows}',
                    'seat_number': f'Место {seat_number} не существует в зале {hall.name}. Максимум мест в ряду: {hall.total_seats_per_row}'
                })

            # Проверка, что место не занято (кроме текущего билета при обновлении)
            existing_ticket = Ticket.objects.filter(
                screening=screening,
                seat_row=seat_row,
                seat_number=seat_number
            )
            if self.instance:
                existing_ticket = existing_ticket.exclude(pk=self.instance.pk)

            if existing_ticket.exists():
                raise serializers.ValidationError({
                    'seat_row': f'Место ряд {seat_row}, место {seat_number} уже занято на этот сеанс.'
                })

        return data


class UserFavoriteSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserFavorite
        fields = '__all__'
        read_only_fields = ['created_at']
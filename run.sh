#!/bin/bash

# Скрипт для запуска Django сервера

echo "Запуск Django сервера для онлайн-кинотеатра..."

# Активация виртуального окружения
source venv/Scripts/activate

# Запуск сервера
python manage.py runserver

echo "Сервер запущен на http://127.0.0.1:8000/"

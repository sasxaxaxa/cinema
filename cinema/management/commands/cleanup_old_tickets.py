from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from cinema.models import Ticket


class Command(BaseCommand):
    help = 'Очистка старых билетов (старше N дней)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Количество дней, после которых билеты считаются старыми (по умолчанию 365)'
        )

        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать, что будет удалено, без фактического удаления'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']

        # Вычисляем дату, старше которой билеты будут удалены
        cutoff_date = timezone.now() - timedelta(days=days)

        # Находим старые билеты
        old_tickets = Ticket.objects.filter(created_at__lt=cutoff_date)

        tickets_count = old_tickets.count()

        if dry_run:
            self.stdout.write(
                f'Будет удалено {tickets_count} билетов старше {days} дней (сухой запуск)'
            )

            # Показываем детали
            if tickets_count > 0:
                self.stdout.write('Список билетов для удаления:')
                for ticket in old_tickets[:10]:  # Показываем первые 10
                    self.stdout.write(
                        f'  - ID {ticket.id}: {ticket.user.username} на "{ticket.screening.movie.title}" '
                        f'({ticket.created_at.strftime("%d.%m.%Y")})'
                    )

                if tickets_count > 10:
                    self.stdout.write(f'  ... и еще {tickets_count - 10} билетов')

        else:
            # Фактическое удаление
            if tickets_count == 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Нет билетов старше {days} дней для удаления')
                )
            else:
                deleted_count, _ = old_tickets.delete()

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно удалено {deleted_count} билетов старше {days} дней'
                    )
                )

                # Показываем статистику по статусам удаленных билетов
                self.stdout.write('Статистика удаленных билетов:')

                # Используем агрегацию для подсчета по статусам
                from django.db.models import Count
                status_stats = (old_tickets.values('status')
                              .annotate(count=Count('status'))
                              .order_by('-count'))

                for stat in status_stats:
                    self.stdout.write(f'  - {stat["status"]}: {stat["count"]} билетов')

        # Показываем текущую статистику
        total_tickets = Ticket.objects.count()
        self.stdout.write(f'Всего билетов в системе: {total_tickets}')

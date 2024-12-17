from django.core.management.base import BaseCommand
from django.db.models import Q
from datetime import datetime
from app.models import Event, Status


class Command(BaseCommand):
    help = "Update event statuses based on their start and end times"

    def handle(self, *args, **kwargs):
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()

        # Получаем статусы
        planned_status = Status.objects.filter(title__iexact="Запланировано").first()
        active_status = Status.objects.filter(title__iexact="Активно").first()
        completed_status = Status.objects.filter(title__iexact="Завершено").first()

        if not all([planned_status, active_status, completed_status]):
            return

        # Обновляем статусы мероприятий
        Event.objects.filter(status=planned_status, event_date__lt=current_date).update(
            status=completed_status
        )

        Event.objects.filter(
            status=planned_status, event_date=current_date, start_time__lte=current_time
        ).update(status=active_status)

        Event.objects.filter(
            Q(status=active_status)
            & (
                Q(event_date__lt=current_date)
                | Q(event_date=current_date, end_time__lt=current_time)
            )
        ).update(status=completed_status)

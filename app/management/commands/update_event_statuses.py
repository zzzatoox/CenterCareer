from django.core.management.base import BaseCommand
from datetime import datetime, date
from app.models import Event, Status


class Command(BaseCommand):
    help = "Update event statuses based on their start and end times"

    def handle(self, *args, **kwargs):
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()
        current_year = now.year
        current_month = now.month

        # Получаем статусы
        planned_status = Status.objects.filter(title__iexact="Запланировано").first()
        active_status = Status.objects.filter(title__iexact="Активно").first()
        completed_status = Status.objects.filter(title__iexact="Завершено").first()

        if not all([planned_status, active_status, completed_status]):
            self.stdout.write(self.style.ERROR("Не все статусы найдены в базе данных."))
            return

        # Функция для определения завершенных мероприятий
        def is_completed(event):
            if event.end_date:
                return event.end_date < current_date
            elif event.event_date:
                return event.event_date < current_date or (
                    event.event_date == current_date
                    and event.end_time
                    and event.end_time < current_time
                )
            return False

        # Функция для определения активных мероприятий
        def is_active(event):
            if event.end_date:
                return event.event_date <= current_date <= event.end_date
            elif event.event_date:
                return (
                    event.event_date == current_date
                    and event.start_time
                    and event.end_time
                    and event.start_time <= current_time <= event.end_time
                )
            return False

        # Функция для определения запланированных мероприятий
        def is_planned(event):
            return event.event_date > current_date if event.event_date else False

        # Обновление статусов для всех мероприятий
        events = Event.objects.filter(status__in=[planned_status, active_status])
        for event in events:
            if is_completed(event):
                event.status = completed_status
            elif is_active(event):
                event.status = active_status
            elif is_planned(event):
                event.status = planned_status
            event.save()

        # Обновляем статусы для мероприятий с event_month
        month_events = Event.objects.filter(
            status__in=[planned_status, active_status], event_month__isnull=False
        )

        for event in month_events:
            if event.event_month.year < current_year or (
                event.event_month.year == current_year
                and event.event_month.month < current_month
            ):
                event.status = completed_status
            elif (
                event.event_month.year == current_year
                and event.event_month.month == current_month
            ):
                if event.event_date and event.event_date <= current_date:
                    event.status = active_status
                else:
                    event.status = planned_status
            else:
                event.status = planned_status
            event.save()

        self.stdout.write(self.style.SUCCESS("Статусы мероприятий успешно обновлены."))

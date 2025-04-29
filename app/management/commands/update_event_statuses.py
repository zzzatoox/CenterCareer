from django.core.management.base import BaseCommand
from datetime import datetime
from app.models import Event, Status
from django.db.models import Q


# class Command(BaseCommand):
#     help = "Update event statuses based on their start and end times"

#     def handle(self, *args, **kwargs):
#         now = datetime.now()
#         current_time = now.time()
#         current_date = now.date()
#         current_year = now.year
#         current_month = now.month

#         # Получаем статусы
#         planned_status = Status.objects.filter(title__iexact="Запланировано").first()
#         active_status = Status.objects.filter(title__iexact="Активно").first()
#         completed_status = Status.objects.filter(title__iexact="Завершено").first()

#         if not all([planned_status, active_status, completed_status]):
#             self.stdout.write(self.style.ERROR("Не все статусы найдены в базе данных."))
#             return

#         # Функция для определения завершенных мероприятий
#         def is_completed(event):
#             if event.end_date:
#                 return event.end_date < current_date
#             elif event.event_date:
#                 return event.event_date < current_date or (
#                     event.event_date == current_date
#                     and event.end_time
#                     and event.end_time < current_time
#                 )
#             return False

#         # Функция для определения активных мероприятий
#         def is_active(event):
#             if event.end_date:
#                 return event.event_date <= current_date <= event.end_date
#             elif event.event_date:
#                 return (
#                     event.event_date == current_date
#                     and event.start_time
#                     and event.end_time
#                     and event.start_time <= current_time <= event.end_time
#                 )
#             return False

#         # Функция для определения запланированных мероприятий
#         def is_planned(event):
#             return event.event_date > current_date if event.event_date else False

#         # Обновление статусов для всех мероприятий
#         events = Event.objects.filter(status__in=[planned_status, active_status])
#         for event in events:
#             if is_completed(event):
#                 event.status = completed_status
#             elif is_active(event):
#                 event.status = active_status
#             elif is_planned(event):
#                 event.status = planned_status
#             event.save()

#         # Обновляем статусы для мероприятий с event_month
#         month_events = Event.objects.filter(
#             status__in=[planned_status, active_status], event_month__isnull=False
#         )

#         for event in month_events:
#             if event.event_month.year < current_year or (
#                 event.event_month.year == current_year
#                 and event.event_month.month < current_month
#             ):
#                 event.status = completed_status
#             elif (
#                 event.event_month.year == current_year
#                 and event.event_month.month == current_month
#             ):
#                 if event.event_date and event.event_date <= current_date:
#                     event.status = active_status
#                 else:
#                     event.status = planned_status
#             else:
#                 event.status = planned_status
#             event.save()

#         self.stdout.write(self.style.SUCCESS("Статусы мероприятий успешно обновлены."))


class Command(BaseCommand):
    help = "Update event statuses based on their fields"

    def handle(self, *args, **kwargs):
        now = datetime.now()
        today = now.date()
        current_time = now.time()

        planned_status = Status.objects.filter(title__iexact="Запланировано").first()
        active_status = Status.objects.filter(title__iexact="Активно").first()
        completed_status = Status.objects.filter(title__iexact="Завершено").first()

        if not all([planned_status, active_status, completed_status]):
            self.stdout.write(self.style.ERROR("Не все статусы найдены."))
            return

        # --- 1. Многодневные мероприятия ---
        multi_day_events = Event.objects.filter(
            event_date__isnull=False,
            end_date__isnull=False,
            status__in=[planned_status, active_status],
        )

        multi_day_events.filter(end_date__lt=today).update(status=completed_status)
        multi_day_events.filter(
            event_date__lte=today, end_date__gte=today, status=planned_status
        ).update(status=active_status)

        # --- 2. Однодневные мероприятия с временем ---
        single_day_full = Event.objects.filter(
            event_date__isnull=False,
            end_date__isnull=True,
            start_time__isnull=False,
            end_time__isnull=False,
            status__in=[planned_status, active_status],
        )

        single_day_full.filter(
            Q(event_date__lt=today) | Q(event_date=today, end_time__lt=current_time)
        ).update(status=completed_status)

        single_day_full.filter(
            event_date=today,
            start_time__lte=current_time,
            end_time__gte=current_time,
            status=planned_status,
        ).update(status=active_status)

        # --- 3. Однодневные мероприятия без времени ---
        single_day_no_time = Event.objects.filter(
            event_date__isnull=False,
            end_date__isnull=True,
            start_time__isnull=True,
            end_time__isnull=True,
            status__in=[planned_status, active_status],
        )

        single_day_no_time.filter(event_date__lt=today).update(status=completed_status)
        single_day_no_time.filter(event_date=today, status=planned_status).update(
            status=active_status
        )

        # --- 4. Только месяц ---
        month_only_events = Event.objects.filter(
            event_month__isnull=False,
            event_date__isnull=True,
            start_time__isnull=True,
            end_time__isnull=True,
            end_date__isnull=True,
            status__in=[planned_status, active_status],
        )

        month_only_events.filter(
            Q(event_month__year__lt=today.year)
            | Q(event_month__year=today.year, event_month__month__lt=today.month)
        ).update(status=completed_status)

        self.stdout.write(self.style.SUCCESS("Статусы мероприятий успешно обновлены."))

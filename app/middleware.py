from datetime import datetime
from django.db.models import Q
from .models import Event, Status


class UpdateEventStatusesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Вызываем функцию обновления статусов
        self.update_event_statuses()
        # Продолжаем обработку запроса
        response = self.get_response(request)
        return response

    # def update_event_statuses(self):
    #     now = datetime.now()
    #     current_time = now.time()
    #     current_date = now.date()

    #     # Получаем статусы
    #     planned_status = Status.objects.filter(title__iexact="Запланировано").first()
    #     active_status = Status.objects.filter(title__iexact="Активно").first()
    #     completed_status = Status.objects.filter(title__iexact="Завершено").first()

    #     if not all([planned_status, active_status, completed_status]):
    #         return

    #     # 1. Мероприятия, которые завершились
    #     Event.objects.filter(
    #         status__in=[planned_status, active_status],
    #         event_date__lt=current_date,
    #     ).update(status=completed_status)

    #     Event.objects.filter(
    #         status=active_status,
    #         event_date=current_date,
    #         end_time__lt=current_time,
    #     ).update(status=completed_status)

    #     # 2. Мероприятия, которые активны сейчас
    #     Event.objects.filter(
    #         status=planned_status,
    #         event_date=current_date,
    #         start_time__lte=current_time,
    #     ).update(status=active_status)

    #     Event.objects.filter(
    #         status=planned_status,
    #         event_date__lte=current_date,
    #         end_date__gte=current_date,
    #     ).update(status=active_status)

    #     # 3. Мероприятия, которые еще не начались
    #     Event.objects.filter(
    #         status=planned_status,
    #         event_date__gt=current_date,
    #     ).update(status=planned_status)

    #     # 4. Обработка мероприятий с event_month
    #     Event.objects.filter(
    #         status__in=[planned_status, active_status],
    #         event_month__isnull=False,
    #     ).filter(
    #         Q(event_month__year__lt=datetime.now().year)
    #         | Q(
    #             event_month__year=datetime.now().year,
    #             event_month__month__lt=datetime.now().month,
    #         )
    #     ).update(status=completed_status)

    #     Event.objects.filter(
    #         status=planned_status,
    #         event_month__year=datetime.now().year,
    #         event_month__month=datetime.now().month,
    #         event_date__lte=current_date,
    #     ).update(status=active_status)

    #     Event.objects.filter(
    #         status=planned_status,
    #         event_month__year__gt=datetime.now().year,
    #     ).update(status=planned_status)

    #     Event.objects.filter(
    #         status=planned_status,
    #         event_month__year=datetime.now().year,
    #         event_month__month__gt=datetime.now().month,
    #     ).update(status=planned_status)

    def update_event_statuses(self):
        now = datetime.now()
        today = now.date()
        current_time = now.time()

        # Получение статусов
        planned_status = Status.objects.filter(title__iexact="Запланировано").first()
        active_status = Status.objects.filter(title__iexact="Активно").first()
        completed_status = Status.objects.filter(title__iexact="Завершено").first()

        if not all([planned_status, active_status, completed_status]):
            return

        # --- 1. Многодневные мероприятия (event_date + end_date) ---
        multi_day_events = Event.objects.filter(
            event_date__isnull=False,
            end_date__isnull=False,
            status__in=[planned_status, active_status],
        )

        # Завершённые
        multi_day_events.filter(end_date__lt=today).update(status=completed_status)

        # Активные
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

        # Завершённые
        single_day_full.filter(
            Q(event_date__lt=today) | Q(event_date=today, end_time__lt=current_time)
        ).update(status=completed_status)

        # Активные
        single_day_full.filter(
            event_date=today,
            start_time__lte=current_time,
            end_time__gte=current_time,
            status=planned_status,
        ).update(status=active_status)

        # --- 3. Однодневные без времени ---
        single_day_no_time = Event.objects.filter(
            event_date__isnull=False,
            end_date__isnull=True,
            start_time__isnull=True,
            end_time__isnull=True,
            status__in=[planned_status, active_status],
        )

        # Завершённые
        single_day_no_time.filter(event_date__lt=today).update(status=completed_status)

        # Активные
        single_day_no_time.filter(event_date=today, status=planned_status).update(
            status=active_status
        )

        # --- 4. Только event_month — НЕ менять статус в текущем месяце ---
        month_only_events = Event.objects.filter(
            event_month__isnull=False,
            event_date__isnull=True,
            start_time__isnull=True,
            end_time__isnull=True,
            end_date__isnull=True,
            status__in=[planned_status, active_status],
        )

        # Завершённые месячные мероприятия
        month_only_events.filter(
            Q(event_month__year__lt=today.year)
            | Q(event_month__year=today.year, event_month__month__lt=today.month)
        ).update(status=completed_status)

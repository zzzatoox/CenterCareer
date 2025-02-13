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

    def update_event_statuses(self):
        now = datetime.now()
        current_time = now.time()
        current_date = now.date()

        # Получаем статусы
        planned_status = Status.objects.filter(title__iexact="Запланировано").first()
        active_status = Status.objects.filter(title__iexact="Активно").first()
        completed_status = Status.objects.filter(title__iexact="Завершено").first()

        if not all([planned_status, active_status, completed_status]):
            return

        # 1. Мероприятия, которые завершились
        Event.objects.filter(
            status__in=[planned_status, active_status],
            event_date__lt=current_date,
        ).update(status=completed_status)

        Event.objects.filter(
            status=active_status,
            event_date=current_date,
            end_time__lt=current_time,
        ).update(status=completed_status)

        # 2. Мероприятия, которые активны сейчас
        Event.objects.filter(
            status=planned_status,
            event_date=current_date,
            start_time__lte=current_time,
        ).update(status=active_status)

        Event.objects.filter(
            status=planned_status,
            event_date__lte=current_date,
            end_date__gte=current_date,
        ).update(status=active_status)

        # 3. Мероприятия, которые еще не начались
        Event.objects.filter(
            status=planned_status,
            event_date__gt=current_date,
        ).update(status=planned_status)

        # 4. Обработка мероприятий с event_month
        Event.objects.filter(
            status__in=[planned_status, active_status],
            event_month__isnull=False,
        ).filter(
            Q(event_month__year__lt=datetime.now().year)
            | Q(
                event_month__year=datetime.now().year,
                event_month__month__lt=datetime.now().month,
            )
        ).update(status=completed_status)

        Event.objects.filter(
            status=planned_status,
            event_month__year=datetime.now().year,
            event_month__month=datetime.now().month,
            event_date__lte=current_date,
        ).update(status=active_status)

        Event.objects.filter(
            status=planned_status,
            event_month__year__gt=datetime.now().year,
        ).update(status=planned_status)

        Event.objects.filter(
            status=planned_status,
            event_month__year=datetime.now().year,
            event_month__month__gt=datetime.now().month,
        ).update(status=planned_status)

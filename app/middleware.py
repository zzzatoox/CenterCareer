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
        canceled_status = Status.objects.filter(title__iexact="Отменено").first()

        if not all([planned_status, active_status, completed_status, canceled_status]):
            return

        # Обновляем статусы мероприятий
        # 1. Переводим "Запланировано" в "Завершено" или "Активно"
        Event.objects.filter(status=planned_status, event_date__lt=current_date).update(
            status=completed_status
        )

        Event.objects.filter(
            status=planned_status, event_date=current_date, start_time__lte=current_time
        ).update(status=active_status)

        # 2. Переводим "Активно" в "Завершено"
        Event.objects.filter(
            Q(status=active_status)
            & (
                Q(event_date__lt=current_date)
                | Q(event_date=current_date, end_time__lt=current_time)
            )
        ).update(status=completed_status)


# class XForwardedForMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
#         if x_forwarded_for:
#             request.META["REMOTE_ADDR"] = x_forwarded_for.split(",")[0].strip()
#         return self.get_response(request)

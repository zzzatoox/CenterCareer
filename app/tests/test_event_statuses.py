from django.test import TestCase
from django.core.management import call_command
from datetime import datetime, date, time, timedelta
from app.models import Event, Status, Category, Company, Location, City


class EventStatusTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем обязательные объекты
        cls.category = Category.objects.create(title="Тестовая категория")
        cls.company = Company.objects.create(
            title="Тестовая компания",
            address="Тестовый адрес",
            city=City.objects.create(title="Тестовый город", region="Тестовый регион"),
        )
        cls.location = Location.objects.create(location="Тестовое место")
        cls.planned_status = Status.objects.create(title="Запланировано")
        cls.active_status = Status.objects.create(title="Активно")
        cls.completed_status = Status.objects.create(title="Завершено")

    def create_event(
        self,
        event_date,
        end_date=None,
        start_time=None,
        end_time=None,
        event_month=None,
    ):
        return Event.objects.create(
            title="Тестовое мероприятие",
            event_date=event_date,
            end_date=end_date,
            start_time=start_time,
            end_time=end_time,
            event_month=event_month,
            category=self.category,
            company=self.company,
            location=self.location,
            is_online=False,  # Указываем значение для обязательного поля
            status=self.planned_status,  # Указываем начальный статус
        )

    def test_single_day_event_completed(self):
        # Однодневное мероприятие, которое завершилось
        event = self.create_event(
            event_date=date(2024, 2, 1),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.completed_status)

    def test_single_day_event_active(self):
        # Используем фиксированное время для тестирования
        current_time = time(11, 0)  # Текущее время внутри диапазона
        event = self.create_event(
            event_date=date.today(),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        # Мокируем текущее время
        with self.settings(NOW=datetime.combine(date.today(), current_time)):
            call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.active_status)

    def test_single_day_event_planned(self):
        # Однодневное мероприятие, которое еще не началось
        event = self.create_event(
            event_date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            end_time=time(12, 0),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.planned_status)

    def test_multi_day_event_completed(self):
        # Многодневное мероприятие, которое завершилось
        event = self.create_event(
            event_date=date(2024, 1, 25),
            end_date=date(2024, 1, 30),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.completed_status)

    def test_multi_day_event_active(self):
        # Многодневное мероприятие, которое активно сейчас
        event = self.create_event(
            event_date=date.today() - timedelta(days=1),
            end_date=date.today() + timedelta(days=1),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.active_status)

    def test_multi_day_event_planned(self):
        # Многодневное мероприятие, которое еще не началось
        event = self.create_event(
            event_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=3),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.planned_status)

    def test_event_month_completed(self):
        # Мероприятие с event_month в прошлом
        event = self.create_event(
            event_date=date(2024, 1, 1),
            event_month=date(2024, 1, 1),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.completed_status)

    def test_event_month_active(self):
        # Мероприятие с event_month в текущем месяце
        event = self.create_event(
            event_date=date.today(),
            event_month=date.today().replace(day=1),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.active_status)

    def test_event_month_planned(self):
        # Мероприятие с event_month в будущем
        event = self.create_event(
            event_date=date.today().replace(month=date.today().month + 1, day=1),
            event_month=date.today().replace(month=date.today().month + 1, day=1),
        )
        call_command("update_event_statuses")
        event.refresh_from_db()
        self.assertEqual(event.status, self.planned_status)

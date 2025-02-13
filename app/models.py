from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from django.core.exceptions import ValidationError


class City(models.Model):
    city_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20, unique=True, verbose_name="Название города")
    region = models.CharField(max_length=255, verbose_name="Регион")

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Company(models.Model):
    company_id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=50, unique=True, verbose_name="Название компании"
    )
    address = models.CharField(max_length=255, verbose_name="Адрес")
    logo = models.ImageField(
        upload_to="company/", blank=True, null=True, verbose_name="Лого"
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="companies", verbose_name="Город"
    )

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Vacancy(models.Model):
    vacancy_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Название вакансии")
    # description = models.TextField(blank=True, null=True, verbose_name="Описание")
    description = CKEditor5Field(
        blank=True, null=True, verbose_name="Описание", config_name="extends"
    )
    min_salary = models.IntegerField(
        blank=True, null=True, verbose_name="Минимальная зарплата"
    )
    max_salary = models.IntegerField(
        blank=True, null=True, verbose_name="Максимальная зарплата"
    )
    is_relevant = models.BooleanField(default=True, verbose_name="Актуальность")
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="vacancies",
        verbose_name="Компания",
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Filter(models.Model):
    filter_id = models.AutoField(primary_key=True)
    title = models.CharField(
        max_length=40, unique=True, verbose_name="Название фильтра"
    )

    class Meta:
        verbose_name = "Фильтр"
        verbose_name_plural = "Фильтры"
        ordering = ["title"]

    def __str__(self):
        return self.title


class FilterValue(models.Model):
    filter_value_id = models.AutoField(primary_key=True)
    filter = models.ForeignKey(
        Filter, on_delete=models.CASCADE, related_name="values", verbose_name="Фильтр"
    )
    value = models.CharField(max_length=30, verbose_name="Значение")

    class Meta:
        verbose_name = "Значение фильтра"
        verbose_name_plural = "Значения фильтров"
        ordering = ["filter__title", "value"]

    def __str__(self):
        return f"{self.filter.title}: {self.value}"


class VacancyFilter(models.Model):
    vacancy = models.ForeignKey(
        Vacancy,
        on_delete=models.CASCADE,
        related_name="filters",
        verbose_name="Вакансия",
    )
    filter_value = models.ForeignKey(
        FilterValue,
        on_delete=models.CASCADE,
        related_name="vacancies",
        verbose_name="Значение фильтра",
    )

    class Meta:
        verbose_name = "Фильтр вакансии"
        verbose_name_plural = "Фильтры вакансий"
        unique_together = ("vacancy", "filter_value")


class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=20, verbose_name="Название статуса")

    class Meta:
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name="Название категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    location = models.CharField(
        max_length=255, unique=True, verbose_name="Место проведения"
    )

    class Meta:
        verbose_name = "Место проведения"
        verbose_name_plural = "Места проведения"
        ordering = ["location"]

    def __str__(self):
        return self.location


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Название мероприятия")
    # description = models.TextField(blank=True, null=True, verbose_name="Описание")
    description = CKEditor5Field(
        blank=True, null=True, verbose_name="Описание", config_name="extends"
    )
    photo = models.ImageField(
        upload_to="events/", blank=True, null=True, verbose_name="Фото"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    event_date = models.DateField(
        blank=True, null=True, verbose_name="Дата мероприятия"
    )
    end_date = models.DateField(
        blank=True, null=True, verbose_name="Дата окончания мероприятия"
    )
    event_month = models.DateField(
        blank=True, null=True, verbose_name="Месяц мероприятия"
    )
    start_time = models.TimeField(blank=True, null=True, verbose_name="Время начала")
    end_time = models.TimeField(blank=True, null=True, verbose_name="Время окончания")
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Место проведения",
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Категория",
    )
    is_online = models.BooleanField(verbose_name="Онлайн")
    status = models.ForeignKey(
        Status, on_delete=models.CASCADE, related_name="events", verbose_name="Статус"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Компания",
    )

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
        ordering = ["event_date"]

    def clean(self):
        super().clean()

        # Проверка для event_date и end_date
        if self.event_date and self.end_date:
            if self.event_date > self.end_date:
                raise ValidationError(
                    {"end_date": "Дата окончания не может быть раньше даты начала."}
                )

        # Проверка для start_time и end_time (только для однодневных мероприятий)
        if self.start_time and self.end_time:
            if (self.event_date and not self.end_date) or (
                self.event_date == self.end_date
            ):
                if self.start_time > self.end_time:
                    raise ValidationError(
                        {
                            "end_time": "Время окончания не может быть раньше времени начала."
                        }
                    )
        # Проверка для event_month
        if self.event_month and self.event_date:
            if (
                self.event_month.month != self.event_date.month
                or self.event_month.year != self.event_date.year
            ):
                raise ValidationError(
                    {
                        "event_month": "Месяц мероприятия должен соответствовать дате начала."
                    }
                )

    def __str__(self):
        return self.title

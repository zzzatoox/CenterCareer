from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, Q, Case, When, Value, IntegerField

from .models import Status, Event, Vacancy, FilterValue, City, Company

from fuzzywuzzy import process

from django.core.mail import send_mail
from .forms import FeedbackForm

from django.conf import settings
from django.contrib import messages


def vacancies(request):
    # Получаем все вакансии
    vacancies = Vacancy.objects.filter(is_relevant=True).prefetch_related(
        "filters__filter_value"
    )

    # Поиск по должности с использованием fuzzywuzzy
    search = request.GET.get("search")
    if search:
        all_titles = Vacancy.objects.values_list("title", flat=True).distinct()

        closest_matches = process.extract(search, all_titles, limit=10)

        matched_titles = [
            match[0] for match in closest_matches if match[1] > 70
        ]  # Порог совпадения 70%
        vacancies = vacancies.filter(title__in=matched_titles)

    # Фильтрация по городу
    # city = request.GET.get("city")
    # if city:
    #     # vacancies = vacancies.filter(company__city__title__icontains=city)
    #     all_cities = Vacancy.objects.values_list(
    #         "company__city__title", flat=True
    #     ).distinct()
    #     closest_city_matches = process.extract(city, all_cities, limit=10)
    #     matched_cities = [
    #         match[0] for match in closest_city_matches if match[1] > 70
    #     ]  # Порог совпадения 70%
    #     vacancies = vacancies.filter(company__city__title__in=matched_cities)

    # Фильтрация по организации
    # organisation = request.GET.get("organisation")
    # if organisation:
    #     # vacancies = vacancies.filter(company__title__icontains=organisation)
    #     all_organisations = Vacancy.objects.values_list(
    #         "company__title", flat=True
    #     ).distinct()
    #     closest_org_matches = process.extract(organisation, all_organisations, limit=10)
    #     matched_organisations = [
    #         match[0] for match in closest_org_matches if match[1] > 70
    #     ]  # Порог совпадения 70%
    #     vacancies = vacancies.filter(company__title__in=matched_organisations)

    # Фильтрация по инвалидности
    invalids = request.GET.get("invalids")
    if invalids == "on":
        vacancies = vacancies.filter(filters__filter_value__value="Да")

    # Фильтрация по опыту работы
    experience = request.GET.getlist("experience")
    if experience:
        vacancies = vacancies.filter(filters__filter_value__value__in=experience)

    # Фильтрация по типу занятости
    type_of_employment = request.GET.getlist("type_of_employment")
    if type_of_employment:
        vacancies = vacancies.filter(
            filters__filter_value__value__in=type_of_employment
        )

    # Фильтрация по режиму работы
    schedule = request.GET.getlist("schedule")
    if schedule:
        vacancies = vacancies.filter(filters__filter_value__value__in=schedule)

    # Фильтрация по зарплате
    salary_from = request.GET.get("salary_from")
    salary_to = request.GET.get("salary_to")
    if salary_from:
        vacancies = vacancies.filter(
            Q(min_salary__gte=salary_from) | Q(max_salary__gte=salary_from)
        )
    if salary_to:
        vacancies = vacancies.filter(
            Q(max_salary__lte=salary_to) | Q(min_salary__lte=salary_to)
        )

    # Фильтрация по "Указан доход"
    income_stated = request.GET.get("income_stated")
    if income_stated == "on":
        vacancies = vacancies.filter(
            Q(min_salary__isnull=False) | Q(max_salary__isnull=False)
        )

    # Пагинация
    paginator = Paginator(vacancies, 10)  # Показывать по 10 вакансий на странице
    page = request.GET.get("page")

    try:
        vacancies = paginator.page(page)
    except PageNotAnInteger:
        vacancies = paginator.page(1)
    except EmptyPage:
        vacancies = paginator.page(paginator.num_pages)

    # Получаем первые 5 городов
    # cities = City.objects.annotate(
    #     num_vacancies=Count("companies__vacancies")
    # ).order_by("-num_vacancies")[:5]

    # Получаем первые 5 организаций
    # organisations = Company.objects.annotate(num_vacancies=Count("vacancies")).order_by(
    #     "-num_vacancies"
    # )[:5]

    # Получаем первые 8 уникальных должностей
    unique_titles = Vacancy.objects.values_list("title", flat=True).distinct()[:8]

    # Получаем все возможные значения для фильтров
    experiences = FilterValue.objects.filter(filter__title="Опыт работы").order_by(
        Case(
            When(value="Без опыта", then=Value(1)),
            When(value="от 1 до 3 лет", then=Value(2)),
            When(value="от 3 до 6 лет", then=Value(3)),
            When(value="больше 6 лет", then=Value(4)),
            default=Value(5),
            output_field=IntegerField(),
        )
    )
    type_of_employments = FilterValue.objects.filter(filter__title="Тип занятости")
    schedules = FilterValue.objects.filter(filter__title="Режим работы")

    return render(
        request,
        "vacancies.html",
        {
            "vacancies": vacancies,
            "experiences": experiences,
            "type_of_employments": type_of_employments,
            "schedules": schedules,
            # "cities": cities,
            # "organisations": organisations,
            "unique_titles": unique_titles,
            # "city": city,
            # "organisation": organisation,
            "invalids": invalids,
            "experience": experience,
            "type_of_employment": type_of_employment,
            "schedule": schedule,
            "salary_from": salary_from,
            "salary_to": salary_to,
            "income_stated": income_stated,
            "search": search,
        },
    )


def index(request):
    return render(request, "index.html")


def employment(request):
    return render(request, "employment.html")


def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, vacancy_id=vacancy_id)
    return render(request, "vacancy_detail.html", {"vacancy": vacancy})


def events(request):
    try:
        # Получаем статусы "Запланировано", "Активно", "Отменено"
        planned_status = Status.objects.filter(title__iexact="Запланировано").first()
        active_status = Status.objects.filter(title__iexact="Активно").first()
        # canceled_status = Status.objects.filter(title__iexact="Отменено").first()

        # Получаем мероприятия с нужными статусами
        events = Event.objects.filter(
            status__in=[planned_status, active_status]  # canceled_status
        ).order_by("event_date")

        context = {
            "events": events,
        }

    except ObjectDoesNotExist as e:
        # Обработка случая, если статусы не найдены
        context = {"events": [], "error_message": "Статусы мероприятий не найдены."}
    except Exception as e:
        # Обработка других ошибок
        context = {
            "events": [],
            "error_message": "Произошла ошибка при загрузке мероприятий.",
        }
    return render(request, "events.html", context)


def event_detail(request, event_id):
    event = get_object_or_404(Event, event_id=event_id)
    return render(request, "event_detail.html", {"event": event})


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            message = form.cleaned_data["message"]
            email_message = f"Имя: {name}\n\nСообщение:\n{message}"
            try:
                send_mail(
                    subject="Обратная связь с сайта",
                    message=email_message,
                    from_email=None,
                    recipient_list=[settings.EMAIL_HOST_USER],
                )
                messages.success(request, "Ваше сообщение успешно отправлено!")
            except Exception as e:
                print(f"Ошибка отправки письма: {e}")
                messages.error(
                    request,
                    "Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже.",
                )
    else:
        form = FeedbackForm()
    return render(request, "feedback.html", {"form": form})

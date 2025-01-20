from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("employment/", views.employment, name="employment"),
    path("vacancies/", views.vacancies, name="vacancies"),
    path("vacancies/<int:vacancy_id>/", views.vacancy_detail, name="vacancy_detail"),
    path("events/", views.events, name="events"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("feedback/", views.feedback_view, name="feedback"),

    # TV URLs
    path("tv/", views.tv, name="tv"),
    path("tv-vacancies/", views.tv_vacancies, name="tv_vacancies"),
    path("tv-vacancies/<int:vacancy_id>/", views.tv_vacancy_detail, name="tv_vacancy_detail"),
    path("tv-events/", views.tv_events, name="tv_events"),
    path("tv-events/<int:event_id>/", views.tv_event_detail, name="tv_event_detail"),

    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("captcha/", include("captcha.urls")),
]

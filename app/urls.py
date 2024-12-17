from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("employment/", views.employment, name="employment"),
    path("vacancies/", views.vacancies, name="vacancies"),
    path("vacancies/<int:vacancy_id>/", views.vacancy_detail, name="vacancy_detail"),
    path("events/", views.events, name="events"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
]

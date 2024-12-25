from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from app.models import Vacancy, Event


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return ["index", "employment", "vacancies", "events", "feedback"]

    def location(self, item):
        return reverse(item)


class VacancySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Vacancy.objects.filter(is_relevant=True)

    def location(self, obj):
        return reverse("vacancy_detail", args=[obj.vacancy_id])

    def lastmod(self, obj):
        pass


class EventSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.8

    def items(self):
        return Event.objects.filter(status__title__in=["Запланировано", "Активно"])

    def location(self, obj):
        return reverse("event_detail", args=[obj.event_id])

    def lastmod(self, obj):
        return obj.created_at

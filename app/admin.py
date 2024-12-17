from django.contrib import admin
from .models import (
    City,
    Company,
    Vacancy,
    Filter,
    FilterValue,
    VacancyFilter,
    Status,
    Category,
    Location,
    Event,
)

from django_ckeditor_5.widgets import CKEditor5Widget
from django import forms


class VacancyAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    description = forms.CharField(
        label="Описание",
        widget=CKEditor5Widget(
            attrs={"class": "django_ckeditor_5"}, config_name="default"
        ),
    )

    class Meta:
        model = Vacancy
        fields = "__all__"


class EventAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = False

    description = forms.CharField(
        label="Описание",
        widget=CKEditor5Widget(
            attrs={"class": "django_ckeditor_5"}, config_name="default"
        ),
    )

    class Meta:
        model = Vacancy
        fields = "__all__"


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("title", "region")
    search_fields = ("title", "region")
    ordering = ("title",)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("title", "address", "city")
    list_filter = ("city",)
    search_fields = ("title", "address")
    ordering = ("title",)


class VacancyFilterInline(admin.TabularInline):
    model = VacancyFilter
    extra = 1


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "min_salary", "max_salary", "is_relevant")
    form = VacancyAdminForm
    list_filter = ("company", "is_relevant")
    search_fields = ("title", "description")
    ordering = ("title",)
    inlines = [VacancyFilterInline]


@admin.register(Filter)
class FilterAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    ordering = ("title",)


@admin.register(FilterValue)
class FilterValueAdmin(admin.ModelAdmin):
    list_display = ("filter", "value")
    list_filter = ("filter",)
    search_fields = ("value",)
    ordering = ("filter__title", "value")


@admin.register(VacancyFilter)
class VacancyFilterAdmin(admin.ModelAdmin):
    list_display = ("vacancy", "filter_value")
    list_filter = ("vacancy", "filter_value__filter")
    search_fields = ("vacancy__title", "filter_value__value")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    ordering = ("title",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)
    ordering = ("title",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("location",)
    search_fields = ("location",)
    ordering = ("location",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "event_date",
        "start_time",
        "end_time",
        "location",
        "category",
        "status",
        "company",
    )
    list_filter = ("location", "category", "status", "company")
    form = EventAdminForm
    search_fields = ("title", "description")
    ordering = ("event_date",)

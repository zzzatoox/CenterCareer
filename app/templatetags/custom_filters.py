from django import template
import re

register = template.Library()


@register.filter
def trim(value):
    """
    Удаляет все HTML-теги, невидимые символы и лишние пробелы.
    Возвращает пустую строку, если содержимое пустое или состоит только из пробелов.
    """
    if value:
        # Удаляем все HTML-теги
        value = re.sub(r"<[^>]+>", "", value)
        # Удаляем невидимые символы (например, &nbsp;)
        value = re.sub(r"&nbsp;", " ", value)
        # Удаляем лишние пробелы и переносы строк
        value = re.sub(r"\s+", " ", value)
        # Убираем пробелы в начале и конце строки
        value = value.strip()
    return value if value else ""


@register.filter
def russian_pluralize(value, variants):
    """
    Фильтр для склонения слова в зависимости от числа (для русского языка).
    variants: строка с вариантами склонения через запятую (например, "вакансия,вакансии,вакансий").
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    variants = variants.split(",")
    if len(variants) != 3:
        return value

    if value % 10 == 1 and value % 100 != 11:
        return f"{value} {variants[0]}"
    elif 2 <= value % 10 <= 4 and (value % 100 < 10 or value % 100 >= 20):
        return f"{value} {variants[1]}"
    else:
        return f"{value} {variants[2]}"

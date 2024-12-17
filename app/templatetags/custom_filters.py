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

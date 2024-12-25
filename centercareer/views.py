from django.shortcuts import render


def custom_page_not_found(request, exception):
    return render(request, "errors/404.html", status=404)


def custom_server_error(request, exception=None):
    return render(request, "errors/500.html", status=500)


def custom_permission_denied(request, exception=None):
    return render(request, "errors/403.html", status=403)


def custom_service_unavailable(request, exception=None):
    return render(request, "errors/503.html", status=503)

"""View-классы и обработчики ошибок приложения pages."""
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Страница «О проекте»."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Страница «Наши правила»."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    """Страница 404.html при ошибке 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Страница 500.html при внутренней ошибке сервера."""
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    """Страница 403csrf.html при CSRF-ошибке 403."""
    return render(request, 'pages/403csrf.html', status=403)

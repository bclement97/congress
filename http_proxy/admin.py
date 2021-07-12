from django.contrib import admin

from .models import DailyRequestMonitor, ProPublicaRequest

admin.site.register(DailyRequestMonitor)
admin.site.register(ProPublicaRequest)

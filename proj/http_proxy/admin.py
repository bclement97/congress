from django.contrib import admin

from .models import DailyRequestMonitor, ProPublicaRequest


class DailyRequestMonitorAdmin(admin.ModelAdmin):
    date_hierarchy = 'date'
    readonly_fields = ('request_model', 'date', 'grant_count', 'sent_count',)


class ProPublicaRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('http_method', 'endpoint', 'granted', 'created_on',
                       'sent_on', 'http_code',)


admin.site.register(DailyRequestMonitor, DailyRequestMonitorAdmin)
admin.site.register(ProPublicaRequest, ProPublicaRequestAdmin)

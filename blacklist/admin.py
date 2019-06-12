from django.contrib import admin

from .models import Rule


class RuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'address', 'prefixlen', 'created', 'duration', 'is_active')
    list_filter = ('created', 'duration')
    search_fields = ('user__username', 'address', 'comments')


admin.site.register(Rule, RuleAdmin)

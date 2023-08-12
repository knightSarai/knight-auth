from django.contrib import admin

from knightauth import models


@admin.register(models.AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):
    list_display = ('digest', 'user', 'created',)
    fields = ()
    raw_id_fields = ('user',)

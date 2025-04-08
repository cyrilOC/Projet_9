from django.contrib import admin
from .models import Ticket, Review, UserFollows

admin.site.register(Ticket)
admin.site.register(Review)

@admin.register(UserFollows)
class UserFollowsAdmin(admin.ModelAdmin):
    list_display = ('user', 'followed_user', 'follow_date',)

# Register your models here.

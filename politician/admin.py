from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Community)
class CommunityModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Board)
class BoardModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Opinion)
class OpinionModelAdmin(admin.ModelAdmin):
    pass

@admin.register(Quiz)
class QuizModelAdmin(admin.ModelAdmin):
    pass

@admin.register(OrigDetail)
class OrigDetailModelAdmin(admin.ModelAdmin):
    pass
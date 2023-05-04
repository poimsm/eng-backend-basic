from django.contrib import admin
from api.models import (
    Question, Word
)

# Register your models here.
# admin.site.register(Category)
admin.site.register(Question)
admin.site.register(Word)

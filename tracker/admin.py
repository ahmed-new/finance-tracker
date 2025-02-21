from django.contrib import admin
from tracker.models import Category, Transaction


admin.site.register(Transaction)
admin.site.register(Category)

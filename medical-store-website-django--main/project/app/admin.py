from django.contrib import admin
from .models import Medicine, User,Sale,Prescription,Transaction

admin.site.register(Medicine)
admin.site.register(User)
admin.site.register(Sale)
admin.site.register(Prescription)
admin.site.register(Transaction)
from django.contrib import admin

# Register your models here.

from .models import Category,Doctor,DoctorImages,TimeSlot,Appointment

admin.site.register(Category)
admin.site.register(Doctor)
admin.site.register(DoctorImages)
admin.site.register(TimeSlot)
admin.site.register(Appointment)

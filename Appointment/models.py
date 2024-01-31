
from django.contrib.auth.models import User
from django.db import models
import uuid

class BaseModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4   , editable=False , primary_key=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now_add=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    category_name = models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.category_name

class TimeSlot(BaseModel):
    time_slots = models.CharField(max_length=100)
    def __str__(self) -> str:
        return self.time_slots
    


class Doctor(BaseModel):
    doctor_name= models.CharField(max_length=100)
    doctor_price = models.IntegerField()
    description = models.TextField()
    category = models.ManyToManyField(Category)

    def __str__(self) -> str:
        return self.doctor_name


class DoctorImages(BaseModel):
    doctor= models.ForeignKey(Doctor ,related_name="images", on_delete=models.CASCADE)
    images = models.ImageField(upload_to="doctors")


class Appointment(models.Model):
    appointment_id = models.UUIDField(default=uuid.uuid4   , editable=False , primary_key=True)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=100)
    doctor= models.ForeignKey(Doctor , related_name="doctor_bookings" , on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="user_bookings" , on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)



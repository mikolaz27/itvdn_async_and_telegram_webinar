import random

from django.contrib import admin
from django.urls import path
from django.http import HttpResponse

from faker import Faker
from faker_vehicle import VehicleProvider

from telegram_bot.models import Vehicle


def generate_date(request):
    fake = Faker()
    fake.add_provider(VehicleProvider)

    for i in range(100):
        Vehicle.objects.create(
            vin=fake.license_plate(),
            brand=fake.vehicle_make(),
            model=fake.vehicle_model(),
            production_year=fake.vehicle_year(),
            condition=random.randint(0, 6),
            mileage=random.randint(10_000, 300_000),
            seats=random.randint(1, 7),
            color=fake.hex_color(),
            transmission=random.randint(0, 2),
            price=random.randint(1000, 1_000_000)

        )
    return HttpResponse("Done")


urlpatterns = [
    path('faker/', generate_date, ),
    path('', admin.site.urls),

]

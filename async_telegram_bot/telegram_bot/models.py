from asgiref.sync import sync_to_async
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from colorfield.fields import ColorField
from django.db.models import Q
from django.utils.translation import gettext as _


class BaseModel(models.Model):
    class Meta:
        abstract = True

    create_date = models.DateTimeField(null=True, auto_now_add=True)
    last_update = models.DateTimeField(null=True, auto_now=True)

    @classmethod
    @sync_to_async
    def update_by_id(cls, id, data):
        rec = cls.objects.filter(id=id)
        rec.update(**data)
        return cls.objects.get(id=id)

    @classmethod
    @sync_to_async
    def create_record(cls, data):
        rec = cls.objects.create(**data)
        return rec


class Vehicle(BaseModel):
    YEAR_OF_PRODUCTION_MIN = 1900
    YEAR_OF_PRODUCTION_MAX = 2022

    class VEHICLE_CONDITION_CHOICES(models.IntegerChoices):
        EXCELLENT = 0, "Excellent"
        VERY_GOOD = 1, "Very Good"
        GOOD = 2, "Good"
        SATISFACTORY = 3, "Satisfactory"
        POOR = 4, "Poor"
        OUT_OF_ORDER = 5, "Out of order"
        OTHER = 6, "Other"

    class VEHICLE_TRANSMISSION_CHOICES(models.IntegerChoices):
        M = 0, "Manual"
        A = 1, "Automatic"
        OTHER = 2, "Other"

    vin = models.CharField(null=False, blank=False, unique=True, max_length=17,
                           primary_key=True, db_index=True)

    brand = models.CharField(
        max_length=50,
        null=False,
        blank=True,
    )
    model = models.CharField(
        max_length=50,
        null=False,
        blank=True,
    )
    production_year = models.PositiveSmallIntegerField(
        _("year"),
        null=True,
        blank=True,
        validators=[MaxValueValidator(YEAR_OF_PRODUCTION_MAX),
                    MinValueValidator(YEAR_OF_PRODUCTION_MIN)],
    )
    condition = models.PositiveSmallIntegerField(
        choices=VEHICLE_CONDITION_CHOICES.choices,
        default=VEHICLE_CONDITION_CHOICES.OTHER,
        null=True,
        blank=True,
    )
    mileage = models.PositiveBigIntegerField(null=True, blank=True,
                                             validators=[
                                                 MaxValueValidator(3000000)])
    seats = models.SmallIntegerField(null=True, blank=True,
                                     validators=[MaxValueValidator(7),
                                                 MinValueValidator(1)])
    color = ColorField(blank=True, null=True)
    transmission = models.PositiveSmallIntegerField(
        choices=VEHICLE_TRANSMISSION_CHOICES.choices,
        default=VEHICLE_TRANSMISSION_CHOICES.OTHER,
        null=True,
        blank=True,
    )
    image = models.ImageField(
        default="default.png",
        upload_to="media/vehicle",
        null=True,
        blank=True,
    )
    price = models.DecimalField(
        max_digits=19, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(1.00)]
    )
    description = models.TextField(
        max_length=500,
        null=False,
        blank=True,
    )

    def __str__(self):
        return f"{self.brand} {self.model} Price: {self.price} $ "

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @classmethod
    @sync_to_async
    def find_by_model_and_brand(cls, model, brand):
        records = cls.objects.filter(Q(model__icontains=model)
                                     & Q(brand__icontains=brand)).order_by('price')
        if records:
            return list(records)
        return None

    @classmethod
    @sync_to_async
    def find_vehicle_by_vin(cls, vin):
        return cls.objects.get(vin=vin)

    def tg_formatted(self, extra_fields=None, only_fields=None):
        fields_list = [
            'vin',
            'brand',
            'model',
            'production_year',
            'condition',
            'mileage',
            'seats',
            'color',
            'transmission',
            'price',
            'description',
        ]
        extra_fields = extra_fields if extra_fields else []
        only_fields = only_fields if only_fields else fields_list
        allowed_fields_list = list((set(fields_list) & set(only_fields)))
        fields_list = [field for field in fields_list if
                       field in allowed_fields_list]
        fields_list = extra_fields + fields_list

        res = ''
        fields_meta = {fm.attname: fm.verbose_name for fm in
                       type(self)._meta.fields}
        for field_name in fields_list:
            if field := getattr(self, field_name):
                field_meta = fields_meta.get(field_name)
                res += '{:16}'.format(f"\n{field_meta}:") + str(field)
        return res


class SearchHistory(BaseModel):
    class Meta:
        db_table = 'tg_search_history'

    user = models.ForeignKey('telegram_bot.User',
                             related_name="searches", on_delete=models.CASCADE)
    vehicle = models.ForeignKey('telegram_bot.Vehicle',
                                related_name="searches",
                                on_delete=models.CASCADE, null=True)
    comment = models.CharField(max_length=32)


class User(BaseModel):
    tg_id = models.IntegerField(db_index=True)
    username = models.CharField(max_length=64, null=True)
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(max_length=120, null=True)
    phone = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'tg_users'

    @classmethod
    @sync_to_async
    def find_user_by_tg_id(cls, tg_id):
        user = cls.objects.filter(tg_id=int(tg_id))
        if user:
            return user.first()
        return None

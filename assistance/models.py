from django.contrib.auth.models import User
from django.db import models
from multiselectfield import MultiSelectField


TYPE_OF_ORDER = (
    (1, "awaria"),
    (2, "wypadek"),
    (3, "auto szyba"),
    (4, "auto opony"),
)

TYPE_OF_INSURANCE = (
    (1, "Standard"),
    (2, "Comfort"),
    (3, "ComfortPlus"),
    (4, "VIP"),
)

STATUS_OF_ORDER = (
    (1, "Zgłoszenie kompletne"),
    (2, "Odmowa"),
    (3, "Rezygnacja klienta"),
    (4, "Zakończone"),
)

TYPE_OF_TASK = (
    (1, "Holowanie"),
    (2, "Naprawa na miejscu"),
    (3, "Samochód zastępczy"),
    (4, "Transport osób"),
    (5, "Wymiana szyby"),
    (6, "Wymiana opon"),
    (7, "Inne (opisz)"),
)

STATUS_OF_TASK = (
    (1, "Zlecone"),
    (2, "Anulowane"),
    (3, "Wykonane"),
)

CAR_CLASSES = (
    (1, "Klasa A"),
    (2, "Klasa B"),
    (3, "Klasa C"),
    (4, "Klasa D"),
    (5, "Klasa premium"),
    (6, "SUV"),
    (7, "Inne"),
)


class Person(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=256)
    address_street = models.CharField(max_length=256, null=True)
    address_city = models.CharField(max_length=256, null=True)
    address_post_code = models.CharField(max_length=256, null=True)
    company = models.CharField(max_length=256, null=True)
    nip_company = models.CharField(max_length=32, null=True)
    insurance_company = models.CharField(max_length=64, null=True)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)


class InsuranceType(models.Model):
    name = models.IntegerField(choices=TYPE_OF_INSURANCE)
    description = models.TextField()
    allowed_type_of_order = MultiSelectField(choices=TYPE_OF_ORDER)

    # def __str__(self):
    #     return str(self.name)


class Car(models.Model):
    manufacturer = models.CharField(max_length=128)
    model = models.CharField(max_length=64)

    def __str__(self):
        return self.manufacturer + ' ' + self.model


class Insured(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    car = models.ForeignKey(Car, null=True, on_delete=models.SET_NULL)
    car_plate_number = models.CharField(max_length=16)
    car_first_registration = models.DateTimeField()
    type_of_insurance = models.ForeignKey(InsuranceType, null=True, on_delete=models.SET_NULL)
    insurance_activ = models.BooleanField()

    def __str__(self):
        return "{} {} ({})".format(self.person.first_name, self.person.last_name, self.car_plate_number)


class NewOrder(models.Model):
    who_add = models.ForeignKey(User, null=True)
    date = models.DateField(auto_now_add=True)
    hour = models.TimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=16, null=True)
    plate_number = models.CharField(max_length=16, null=True)
    notifier_first_name = models.CharField(max_length=64, null=True)
    notifier_last_name = models.CharField(max_length=256, null=True)
    person_insured = models.ForeignKey(Insured, null=True, on_delete=models.SET_NULL)
    type_of_order = models.IntegerField(choices=TYPE_OF_ORDER, null=True)
    place_car_stay = models.TextField(null=True)
    place_car_target = models.TextField(null=True)
    place_car_rented = models.TextField(null=True)
    status_order = models.IntegerField(choices=STATUS_OF_ORDER, null=True)


class NewTask (models.Model):
    order_id = models.ForeignKey(NewOrder, on_delete=models.CASCADE)
    date_add = models.DateTimeField(auto_now_add=True)
    date_start = models.DateField(null=True)
    hour_start = models.TimeField(null=True)
    date_end = models.DateField(null=True)
    hour_end = models.TimeField(null=True)
    type_of_task = models.IntegerField(choices=TYPE_OF_TASK, null=True)
    rented_car_class = models.IntegerField(choices=CAR_CLASSES, null=True)
    provider = models.TextField()
    provider_phone_number = models.CharField(max_length=16, null=True)
    provider_email = models.EmailField(max_length=128, null=True)
    price = models.DecimalField(max_digits=7, decimal_places=2, null=True)
    description = models.CharField(max_length=256)
    status_task = models.IntegerField(choices=STATUS_OF_TASK)


class Comment(models.Model):
    who_add_comment = models.ForeignKey(User, null=True)
    date = models.DateField(auto_now_add=True)
    hour = models.TimeField(auto_now_add=True)
    comment = models.TextField(null=True)
    order = models.ForeignKey(NewOrder, null=True)


class Documents(models.Model):
    who_add = models.ForeignKey(User, null=True)
    date_add = models.DateTimeField(auto_now_add=True)
    order_id = models.ForeignKey(NewOrder, on_delete=models.CASCADE)
    type_of_doc = models.CharField(max_length=32, null=True)
    sms = models.TextField(null=True)
    email = models.TextField(null=True)
    name_of_PDF_document = models.CharField(max_length=128, null=True)
    doc_in_file = models.FileField(null=True)
from django.contrib import admin
from .models import Person, InsuranceType, Car, Insured, NewOrder, NewTask


admin.site.register(Person)
admin.site.register(InsuranceType)
admin.site.register(Car)
admin.site.register(Insured)
admin.site.register(NewOrder)
admin.site.register(NewTask)

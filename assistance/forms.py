from django import forms
from django.forms import SelectDateWidget

from assistance.models import TYPE_OF_ORDER, STATUS_OF_ORDER, STATUS_OF_TASK, TYPE_OF_TASK, \
    CAR_CLASSES


class NewOrderSimpleForm(forms.Form):
    phone_number = forms.IntegerField(label='Nr telefonu')
    plate_number = forms.CharField(max_length=100, label='Nr rejestracyjny pojazdu')
    notifier_first_name = forms.CharField(max_length=100, label='Imię')
    notifier_last_name = forms.CharField(max_length=100, label='Nazwisko')


class NewOrderFullForm(forms.Form):
    phone_number = forms.IntegerField(label='Nr telefonu')
    plate_number = forms.CharField(max_length=100, label='Nr rejestracyjny pojazdu')
    notifier_first_name = forms.CharField(max_length=100, label='Imię')
    notifier_last_name = forms.CharField(max_length=100, label='Nazwisko')
    type_of_order = forms.ChoiceField(choices=TYPE_OF_ORDER, label='Rodzaj zdarzenia')
    place_car_stay = forms.CharField(widget=forms.Textarea, required=False, label='Miejsce zdarzenia')
    place_car_target = forms.CharField(widget=forms.Textarea, required=False, label='Miejsce holowania')
    place_car_rented = forms.CharField(widget=forms.Textarea, required=False, label='Miejsce podstawienia zastępczego')
    status_order = forms.ChoiceField(choices=STATUS_OF_ORDER, label='Status zgłoszenia')


class CommentsForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, label='Komentarz operatora')


class NewTaskForm(forms.Form):
    date_start = forms.DateField(label='Data rozpoczęcia', widget=SelectDateWidget)
    hour_start = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'placeholder': '12:00'}),
        label='Godzina rozpoczęcia'
    )
    date_end = forms.DateField(label='Data zakończenia', required=False, widget=SelectDateWidget)
    hour_end = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'placeholder': '12:00'}),
        label='Godzina zakończenia', required=False
    )
    type_of_task = forms.ChoiceField(choices=TYPE_OF_TASK, label='Rodzaj zlecenia')
    rented_car_class = forms.ChoiceField(choices=CAR_CLASSES, label='Klasa samochodu do wypożyczenia', required=False)
    provider = forms.CharField(widget=forms.Textarea, required=False, label='Dane usługodawcy')
    provider_phone_number = forms.IntegerField(label='Nr telefonu usługodawcy', required=False)
    provider_email = forms.EmailField(label='e-mail usługodawcy', required=False)
    price = forms.CharField(widget=forms.NumberInput(attrs={'step': 0.01, 'max': 10000.0, 'min': 0.0}), label='Cena',
                            required=False)
    description = forms.CharField(widget=forms.Textarea, label='Opis')
    status_task = forms.ChoiceField(choices=STATUS_OF_TASK, label='Status')

    def __str__(self):
        return self.type_of_task


class DocAddForm(forms.Form):
    doc_in_file = forms.FileField(label='Dokument')


class LoginForm(forms.Form):
    username = forms.CharField(min_length=3, max_length=128, label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Hasło')

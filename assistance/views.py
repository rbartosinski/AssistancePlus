from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
import pdfkit

from assistance.forms import NewOrderSimpleForm, NewOrderFullForm, NewTaskForm, LoginForm, CommentsForm, \
    DocAddForm
from assistance.models import Person, Insured, NewOrder, NewTask, TYPE_OF_INSURANCE, TYPE_OF_TASK, \
    STATUS_OF_TASK, Comment, CAR_CLASSES, Documents
import datetime
from twilio.rest import Client


class OrderSearchView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_neworder'
    raise_exception = True

    def get(self, request):
        return render(request, 'search.html')

    def post(self, request):
        orders = NewOrder.objects.all()
        person = Insured.objects.all()
        asked_number_plate = request.POST.get('asked_number_plate')
        if asked_number_plate != '':
            orders = orders.filter(plate_number=asked_number_plate)
        insured_number_plate = request.POST.get('insured_number_plate')
        if insured_number_plate != '':
            try:
                person = person.get(car_plate_number=insured_number_plate)
                data_to_find = person.id
            except Insured.DoesNotExist:
                data_to_find = 0
            orders = orders.filter(person_insured=data_to_find)
        task_id = request.POST.get('task_id')
        try:
            if task_id != '':
                orders = orders.filter(id=task_id)
        except ValueError:
            orders = orders.filter(id=0)
        policy_holder = request.POST.get('policy_holder')
        if policy_holder != '':
            try:
                person_holder = Person.objects.get(last_name=policy_holder)
                data_to_find = person_holder.id
            except Person.DoesNotExist:
                data_to_find = 0
            orders = orders.filter(person_insured=data_to_find)
        if insured_number_plate == '' \
                and asked_number_plate == '' \
                and task_id == '' \
                and policy_holder == '':
            orders = []
        finded_orders = orders
        ctx = {
            'finded_orders': finded_orders
        }
        return render(request, 'search.html', ctx)


class OrderSimpleAddView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_neworder'
    raise_exception = True

    def get(self, request):
        ctx = {
            'form': NewOrderSimpleForm,
        }
        return render(request, 'add_order.html', ctx)

    def post(self, request):
        form = NewOrderSimpleForm(request.POST)
        if form.is_valid():
            order = NewOrder.objects.create(**form.cleaned_data)
            user = User.objects.get(username=request.user)
            order.who_add = user
            order.save()

            account_sid = "ACd7ddf6dc5a3ffda4badd44b6ecb72cc4"
            auth_token = "361f509edea7905ab42072e6251b23d2"
            client = Client(account_sid, auth_token)
            client.api.account.messages.create(
                to="48{}".format(order.phone_number),
                from_="+48732483528",
                body="Dzień dobry, zarejstrowaliśmy Twoje zgłoszenie pod nr {}. MojaNova Insurance".format(
                    order.id)
            )
            new_doc_create = Documents.objects.create(
                who_add=request.user,
                order_id=order,
                type_of_doc='sms',
                sms=
                """from_="+48732483528",
                to="48{}"
                body=""Dzień dobry, zarejstrowaliśmy Twoje zgłoszenie pod nr {}. MojaNova Insurance""".format(
                    order.phone_number, order.id),
            )
            return HttpResponseRedirect('/order_edit/{}'.format(order.id))
        ctx = {
            'form': form,
        }
        return render(request, 'add_order.html', ctx)


class OrderEditView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_neworder'
    raise_exception = True

    def get(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        comments = Comment.objects.filter(order_id=order_id)
        try:
            person = Insured.objects.get(car_plate_number=order.plate_number)
            person_data_to_ctx = person.type_of_insurance.name
        except Insured.DoesNotExist:
            person_data_to_ctx = 1
        types_of_insurance = dict(TYPE_OF_INSURANCE)
        if order.person_insured is None:
            insured_about_note_danger = 1
            insured_about_note = insured_about_note_danger
        else:
            insured_about_note_allowed = 2
            insured_about_note = insured_about_note_allowed
        print(insured_about_note)
        form = NewOrderFullForm(initial={
            'phone_number': order.phone_number,
            'plate_number': order.plate_number,
            'notifier_first_name': order.notifier_first_name,
            'notifier_last_name': order.notifier_last_name,
            'place_car_stay': order.place_car_stay,
            'place_car_target': order.place_car_target,
            'place_car_rented': order.place_car_rented,
        })
        ctx = {
            'form': form,
            'form_comment': CommentsForm,
            'comments': comments,
            'insured_about_note': insured_about_note,
            'order': order,
            'type_of_insurance': types_of_insurance[person_data_to_ctx],
        }
        return render(request, 'edit_order.html', ctx)

    def post(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        comments = Comment.objects.filter(order_id=order_id)
        form = NewOrderFullForm(request.POST, initial={
            'phone_number': order.phone_number,
            'plate_number': order.plate_number,
            'notifier_first_name': order.notifier_first_name,
            'notifier_last_name': order.notifier_last_name,
            'place_car_stay': order.place_car_stay,
            'place_car_target': order.place_car_target,
            'place_car_rented': order.place_car_rented,
        })
        form_comment = CommentsForm(request.POST)
        if form.is_valid():
            new_phone_number = form.cleaned_data['phone_number']
            new_plate_number = form.cleaned_data['plate_number']
            new_notifier_first_name = form.cleaned_data['notifier_first_name']
            new_notifier_last_name = form.cleaned_data['notifier_last_name']
            new_place_car_stay = form.cleaned_data['place_car_stay']
            new_place_car_target = form.cleaned_data['place_car_target']
            new_place_car_rented = form.cleaned_data['place_car_rented']
            status_order = form.cleaned_data['status_order']
            order.phone_number = new_phone_number
            order.plate_number = new_plate_number
            order.notifier_first_name = new_notifier_first_name
            order.notifier_last_name = new_notifier_last_name
            order.place_car_stay = new_place_car_stay
            order.place_car_target = new_place_car_target
            order.place_car_rented = new_place_car_rented
            order.status_order = status_order
            order.save()
        if form_comment.is_valid():
            comment = form_comment.cleaned_data['comment']
            comment_created = Comment.objects.create(
                comment=comment,
                who_add_comment=request.user
            )
            comment_created.order_id = order_id
            comment_created.save()
            ctx = {
                'comments': comments,
                'form_comment': CommentsForm,
                'form': form,
                'order': order,
            }
            return render(request, 'edit_order.html', ctx)
        ctx = {
            'comments': comments,
            'form_comment': CommentsForm,
            'form': form,
            'order': order,
        }
        return render(request, 'edit_order.html', ctx)


class OrderCheckView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_neworder'
    raise_exception = True

    def get(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        try:
            person = Insured.objects.get(car_plate_number=order.plate_number)
        except Insured.DoesNotExist:
            return render(request, 'ins_not_exist.html', {
                'order': order,
            })
        types_of_insurance = dict(TYPE_OF_INSURANCE)
        ctx = {
            'order': order,
            'person': person,
            'type_of_insurance': types_of_insurance[person.type_of_insurance.name],
        }
        return render(request, 'ins_coverage.html', ctx)

    def post(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        try:
            insured = Insured.objects.get(car_plate_number=order.plate_number)
        except Insured.DoesNotExist:
            return render(request, 'ins_not_exist.html', {
                'order': order,
            })
        order.person_insured = insured
        order.save()
        return HttpResponseRedirect('/order_edit/{}'.format(order.id))


class CheckInsuranceView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_neworder'
    raise_exception = True

    def get(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        ctx = {
            'order': order,
        }
        return render(request, 'check_manual.html', ctx)

    def post(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        insured_all_data = Insured.objects.all()
        person_first_name = request.POST.get('person_first_name')
        person_last_name = request.POST.get('person_last_name')
        types_of_insurance = dict(TYPE_OF_INSURANCE)
        every_insured_selected = []
        if person_first_name != '':
            if person_last_name != '':
                persons = Person.objects.filter(first_name=person_first_name, last_name=person_last_name)
                for person in persons:
                    insured_selected = insured_all_data.filter(person=person)
                    every_insured_selected.append(insured_selected)
            if person_last_name == '':
                persons = Person.objects.filter(first_name=person_first_name)
                for person in persons:
                    insured_selected = insured_all_data.filter(person=person)
                    every_insured_selected.append(insured_selected)
        if person_first_name == '' and person_last_name != '':
            persons = Person.objects.filter(last_name=person_last_name)
            for person in persons:
                insured_selected = insured_all_data.filter(person=person)
                every_insured_selected.append(insured_selected)
        if person_first_name == '' and person_last_name == '':
            every_insured_selected = []
        ctx = {
            'every_insured_selected': every_insured_selected,
            'types_of_insurance': types_of_insurance,
            'order': order,
        }
        return render(request, 'check_manual.html', ctx)


class PolicyDetailsView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id, policy_id):
        order = NewOrder.objects.get(id=order_id)
        try:
            person = Insured.objects.get(id=policy_id)
        except Insured.DoesNotExist:
            return render(request, 'ins_not_exist.html', {
                'order': order,
            })
        types_of_insurance = dict(TYPE_OF_INSURANCE)
        ctx = {
            'order': order,
            'person': person,
            'type_of_insurance': types_of_insurance[person.type_of_insurance.name],
        }
        return render(request, 'ins_coverage.html', ctx)

    def post(self, request, order_id, policy_id):
        order = NewOrder.objects.get(id=order_id)
        try:
            insured = Insured.objects.get(id=policy_id)
        except Insured.DoesNotExist:
            return render(request, 'ins_not_exist.html', {
                'order': order,
            })
        if insured.car_plate_number == order.plate_number:
            order.person_insured = insured
            order.save()
        else:
            return render(request, 'ins_not_exist.html', {
                'order': order,
                'validate_failed': 'Nr rejestracyjne się nie zgadzają',
            })
        return HttpResponseRedirect('/order_edit/{}'.format(order.id))


class TaskListView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id):
        tasks = NewTask.objects.all().filter(order_id=order_id)
        order = NewOrder.objects.get(id=order_id)
        types_of_tasks = dict(TYPE_OF_TASK)
        statuses_of_tasks = dict(STATUS_OF_TASK)
        ctx = {
            'tasks': tasks,
            'order': order,
            'types_of_tasks': types_of_tasks,
            'statuses_of_tasks': statuses_of_tasks,
        }
        return render(request, 'tasks.html', ctx)


class TaskAddView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        ctx = {
            'form': NewTaskForm,
            'order': order,
        }
        return render(request, 'add_task.html', ctx)

    def post(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        form = NewTaskForm(request.POST)

        if form.is_valid():

            date_start = form.cleaned_data['date_start']
            hour_start = form.cleaned_data['hour_start']
            date_end = form.cleaned_data['date_end']
            hour_end = form.cleaned_data['hour_end']
            type_of_task = form.cleaned_data['type_of_task']
            rented_car_class = form.cleaned_data['rented_car_class']
            provider = form.cleaned_data['provider']
            provider_phone_number = form.cleaned_data['provider_phone_number']
            provider_email = form.cleaned_data['provider_email']
            price = form.cleaned_data['price']
            description = form.cleaned_data['description']
            status_task = form.cleaned_data['status_task']

            NewTask.objects.create(
                order_id=order,
                date_start=date_start,
                hour_start=hour_start,
                who_add=request.user,
                date_end=date_end,
                hour_end=hour_end,
                type_of_task=type_of_task,
                rented_car_class=rented_car_class,
                provider=provider,
                provider_phone_number=provider_phone_number,
                provider_email=provider_email,
                price=price,
                description=description,
                status_task=status_task,
            )
            if type_of_task == '1' and provider_phone_number is not None:
                account_sid = "ACd7ddf6dc5a3ffda4badd44b6ecb72cc4"
                auth_token = "361f509edea7905ab42072e6251b23d2"

                client = Client(account_sid, auth_token)

                client.api.account.messages.create(
                    to="48{}".format(provider_phone_number),
                    from_="+48732483528",
                    body="Zgłoszenie assistance id {} nr rej. {} {} tel. do klienta {}".format(
                        order.id, order.plate_number, order.place_car_stay, order.phone_number)
                )

                new_doc_create = Documents.objects.create(
                    who_add=request.user,
                    order_id=order,
                    type_of_doc='sms',
                    sms=
                    """from_="+48732483528",
                    to="48{}"
                    body="Zgłoszenie assistance id {} nr rej. {} {} tel. do klienta {}""".format(
                        provider_phone_number, order.id, order.plate_number, order.place_car_stay, order.phone_number),
                )

                return HttpResponseRedirect('/task_list/{}'.format(order.id))

            return HttpResponseRedirect('/task_list/{}'.format(order.id))

        ctx = {
            'form': form,
            'order': order,
        }
        return render(request, 'add_task.html', ctx)


class TaskEditView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id, task_id):
        order = NewOrder.objects.get(id=order_id)
        task = NewTask.objects.get(id=task_id)
        form = NewTaskForm(initial={
            'date_start': task.date_start,
            'hour_start': task.hour_start,
            'date_end': task.date_end,
            'hour_end': task.hour_end,
            'type_of_task': task.type_of_task,
            'rented_car_class': task.rented_car_class,
            'provider': task.provider,
            'provider_phone_number': task.provider_phone_number,
            'provider_email': task.provider_email,
            'price': task.price,
            'description': task.description,
            'status_task': task.status_task,
        })
        ctx = {
            'form': form,
            'order': order,
            'task': task,
        }
        return render(request, 'edit_task.html', ctx)

    def post(self, request, order_id, task_id):
        order = NewOrder.objects.get(id=order_id)
        task = NewTask.objects.get(id=task_id)
        form = NewTaskForm(request.POST)
        if form.is_valid():
            new_date_start = form.cleaned_data['date_start']
            new_hour_start = form.cleaned_data['hour_start']
            new_date_end = form.cleaned_data['date_end']
            new_hour_end = form.cleaned_data['hour_end']
            new_type_of_task = form.cleaned_data['type_of_task']
            new_rented_car_class = form.cleaned_data['rented_car_class']
            new_provider = form.cleaned_data['provider']
            new_provider_phone_number = form.cleaned_data['provider_phone_number']
            new_provider_email = form.cleaned_data['provider_email']
            new_price = form.cleaned_data['price']
            new_description = form.cleaned_data['description']
            new_status_task = form.cleaned_data['status_task']

            task.date_start = new_date_start
            task.hour_start = new_hour_start
            task.date_end = new_date_end
            task.hour_end = new_hour_end
            task.type_of_task = new_type_of_task
            task.rented_car_class = new_rented_car_class
            task.provider = new_provider
            task.provider_phone_number = new_provider_phone_number
            task.provider_email = new_provider_email
            task.price = new_price
            task.description = new_description
            task.status_task = new_status_task
            task.save()

            ctx = {
                'form': form,
                'order': order,
                'task': task,
            }
            return render(request, 'edit_task.html', ctx)

        ctx = {
            'form': form,
            'order': order,
            'task': task,
        }
        return render(request, 'edit_task.html', ctx)


class GenerateTaskReceipt(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id, task_id):
        order = NewOrder.objects.get(id=order_id)
        task = NewTask.objects.get(id=task_id)
        date = str(datetime.datetime.now().strftime('%d.%m.%Y'))
        date_to_pdf_file = str(datetime.datetime.now().strftime('%d%m%Y'))
        date_and_hour = str(datetime.datetime.now().strftime('%H:%M:%S, %d.%m.%Y'))
        car_classes = dict(CAR_CLASSES)
        ctx = {
            'date': date,
            'order': order,
            'task': task,
            'car_class': car_classes[task.rented_car_class],
        }
        return render(request, 'generate.html', ctx)


class SaveTaskReceipt(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id, task_id):
        order = NewOrder.objects.get(id=order_id)
        task = NewTask.objects.get(id=task_id)
        date_to_pdf_file = str(datetime.datetime.now().strftime('%d_%m_%Y_%H%M%S'))
        name_of_pdf = 'MojaNovaOrder_nr{}_{}.pdf'.format(order_id, date_to_pdf_file)
        pdf_file = pdfkit.from_url(
            'http://127.0.0.1:8000/generate_receipt/{}/{}'.format(order.id, task.id),
            'media/{}'.format(name_of_pdf)
        )
        email_body = """
        Szanowni państwo,
        
        w załączniku przesyłamy gwarancję płatności wynajmu pojazdu do zgłoszenia assistance nr {}.
        
        Z poważaniem,
        zespół MojaNova Insurance
        """.format(order_id)
        email = EmailMessage(
            'MojaNova - gwarancja płatności - zgłoszenie ID {}'.format(order_id),
            '{}'.format(email_body),
            'assistancesystem@wp.pl',
            ['{}'.format(task.provider_email)],
            reply_to=['assistance@mojanova.pl'],
        )
        email.attach_file('media/{}'.format(name_of_pdf))
        newdoc_create = Documents.objects.create(
            who_add=request.user,
            order_id=order,
            type_of_doc='email',
            email=email,
            name_of_PDF_document=name_of_pdf,
        )
        email.send()
        return HttpResponseRedirect('/task_edit/{}/{}'.format(order.id, task.id))


class DocListView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        docs = Documents.objects.filter(order_id=order_id)
        ctx = {
            'order': order,
            'docs': docs,
        }
        return render(request, 'doc_list.html', ctx)


class DocAddView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        ctx = {
            'order': order,
            'form': DocAddForm,
        }
        return render(request, 'doc_add.html', ctx)

    def post(self, request, order_id):
        order = NewOrder.objects.get(id=order_id)
        form = DocAddForm(request.POST, request.FILES)
        new_doc_create = Documents.objects.create(
            who_add=request.user,
            order_id=order,
            type_of_doc='inny',
            doc_in_file=request.FILES['doc_in_file'],
        )
        ctx = {
            'order': order,
            'form': form,
        }
        return HttpResponseRedirect('/doc_list/{}'.format(order.id))


class ShowDocView(PermissionRequiredMixin, View):
    permission_required = 'assistance.add_newtask'
    raise_exception = True

    def get(self, request, order_id, doc_id):
        order = NewOrder.objects.get(id=order_id)
        doc = Documents.objects.get(id=doc_id)
        ctx = {
            'order': order,
            'doc': doc,
        }
        return render(request, 'doc_details.html', ctx)


class LoginView(View):

    def get(self, request):
        ctx = {
            'form': LoginForm,
        }
        return render(request, 'login.html', ctx)

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                url = request.GET.get('next')
                if url:
                    return redirect(url)
                return HttpResponseRedirect('/order_search/')

            form.add_error(field=None, error='Zły login lub hasło!')

        ctx = {
            'form': form,
        }
        return render(request, 'login.html', ctx)


class LogoutView(View):

    def get(self, request):
        logout(request)
        return HttpResponseRedirect('/login/')


class HelpView(View):

    def get(self, request):
        return render(request, 'help.html')


class ContactView(View):

    def get(self, request):
        return render(request, 'contact.html')

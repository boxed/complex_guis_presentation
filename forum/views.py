from datetime import datetime

from django import forms
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from tri.form import Form, Field
from tri.form.views import create_object, edit_object

from .models import Room, Contact


def django_example1(request):
    class CreateRoomForm(forms.Form):
        name = forms.CharField()
        description = forms.CharField(widget=forms.Textarea)

    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            Room.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description']
            )
            return HttpResponseRedirect('/something/')

    else:
        form = CreateRoomForm()

    return render(request, 'forum/room_form.html', {'form': form})


def tri_form_example1(request):
    class CreateRoomForm(Form):
        name = Field()
        description = Field.textarea()

    if request.method == 'POST':
        form = CreateRoomForm(request=request)
        if form.is_valid():
            Room.objects.create(
                name=form.fields_by_name.name.value,
                description=form.fields_by_name.description,
            )
            return HttpResponseRedirect('/something/')

    else:
        form = CreateRoomForm()

    return render(request, 'forum/room_form.html', {'form': form})


###############################################


class DjangoExample1B(CreateView):
    model = Room
    fields = ['name', 'description']
    # implicit template_name = 'forum/room_form.html'


def tri_form_example1_b(request):
    # by default shows all fields except AutoFields, which is not what we want here
    # tri.form doesn't implicitly access a template, we just use the built in
    return create_object(
        request=request,
        model=Room,
        form__include=['name', 'description'],
    )


###############################################

class DjangoExample2(CreateView):
    model = Room
    fields = ['name', 'description', 'auditor_notes']

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if not self.request.user.is_staff:
            del form.fields['auditor_notes']
        return form


def tri_form_example2(request):
    return create_object(
        request=request,
        model=Room,
        form__include=['name', 'description', 'auditor_notes'],
        form__field__auditor_notes__show=request.user.is_staff,

        form__field__description__call_target=Field.textarea,
        form__field__auditor_notes__call_target=Field.textarea,
    )


###############################################

class DjangoExample3(UpdateView):
    model = Room
    fields = ['name', 'description', 'auditor_notes']

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if not self.request.user.is_staff:
            del form.fields['auditor_notes']
        else:
            form.fields['audit_complete'] = forms.BooleanField(required=False)

        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.is_staff and form.cleaned_data['audit_complete']:
            self.object.last_audit = datetime.now()
            self.object.auditor = self.request.user
            self.object.save()
        return response


def tri_form_example3(request, pk):
    def on_save(instance, form, **_):
        if request.user.is_staff and form.fields_by_name.audit_complete.value:
            instance.last_audit = datetime.now()
            instance.auditor = request.user
            instance.save()

    return edit_object(
        request=request,
        instance=Room.objects.get(pk=pk),
        on_save=on_save,
        form__exclude=['auditor', 'last_audit'],
        form__extra_fields=[
            Field.boolean(
                name='audit_complete',
                attr=None,  # don't write "audit_complete" to the Room object
                show=request.user.is_staff,
            ),
        ],
        form__field__auditor_notes__show=request.user.is_staff,

        form__field__description__call_target=Field.textarea,
        form__field__auditor_notes__call_target=Field.textarea,
    )

# The kicker here is that CreateView/UpdateView create their forms via
# django.forms.models.modelform_factory which has a lot of parameters,
# but you can't actually use them because there is no way to pass
# parameters down that chain. "exclude" being maybe the most egregious case.


###############################################


# Ok, that's all fine and good, but there's no big difference between django forms and tri.form...
# let's increase the complexity!

# - Separate roles of staff and auditors. Now staff should be able to read auditor notes but not edit.
# - insert a header above the audit fields
# - style audit fields with an "admin" css class

class DjangoExample4(UpdateView):
    model = Room
    fields = ['name', 'description', 'auditor_notes']
    template_name = 'forum/django_example4.html'  # <- this is the kicker!

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)

        form.fields['auditor_notes'].disabled = not self.request.user.contact.is_auditor

        if not self.request.user.contact.is_auditor and not self.request.user.is_staff:
            del form.fields['auditor_notes']
        else:
            if self.request.user.contact.is_auditor:
                form.fields['audit_complete'] = forms.BooleanField(required=False)
            if self.request.user.is_staff:
                form.fields['auditor'] = forms.ModelChoiceField(
                    disabled=True,
                    queryset=User.objects.all(),
                    initial=self.object.auditor,
                )
                form.fields['last_audit'] = forms.DateTimeField(
                    initial=self.object.last_audit,
                    disabled=True,
                )

        return form

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('audit_complete'):
            self.object.last_audit = datetime.now()
            self.object.auditor = self.request.user
            self.object.save()
        return response


def tri_form_example4(request, pk):
    def on_save(instance, form, **_):
        if request.user.contact.is_auditor and form.fields_by_name.audit_complete.value:
            instance.last_audit = datetime.now()
            instance.auditor = request.user
            instance.save()

    return edit_object(
        request=request,
        instance=Room.objects.get(pk=pk),
        on_save=on_save,
        form__extra_fields=[
            Field.boolean(
                name='audit_complete',
                attr=None,  # don't write "audit_complete" to the Room object
                show=request.user.contact.is_auditor,
            ),
            Field.heading(
                name='audit',
                after='description',
                show=request.user.contact.is_auditor or request.user.is_staff,
            ),
        ],
        form__field=dict(
            auditor_notes__show=request.user.is_staff or request.user.contact.is_auditor,
            auditor_notes__editable=request.user.contact.is_auditor,

            auditor__editable=False,
            auditor__show=request.user.is_staff,

            last_audit__editable=False,
            last_audit__show=request.user.is_staff,

            description__call_target=Field.textarea,
            auditor_notes__call_target=Field.textarea,

            last_audit__container__attrs__class__audit=True,
            auditor__container__attrs__class__audit=True,
            auditor_notes__container__attrs__class__audit=True,
        ),
    )


# TODO:
#  - show that tri.form will validate stuff, while django will silently pass on spelling errors









###############################################
# Stuff to make demoing and testing easier
###############################################

def switch_user(request):
    standard_user = User.objects.get_or_create(username='normal_user')[0]
    Contact.objects.get_or_create(user=standard_user)

    staff_user = User.objects.get_or_create(username='staff_user', defaults=dict(is_staff=True))[0]
    Contact.objects.get_or_create(user=staff_user)
    auditor_user = User.objects.get_or_create(username='auditor_user')[0]
    Contact.objects.get_or_create(user=auditor_user, defaults=dict(is_auditor=True))

    class SwitchForm(Form):
        user = Field.choice_queryset(User.objects.all(), initial=request.user)

    form = SwitchForm(request)
    if request.method == 'POST':
        login(request, form.fields_by_name.user.value)
        return HttpResponseRedirect('.')

    return render(request, 'forum/switch_user.html', context=dict(form=form))


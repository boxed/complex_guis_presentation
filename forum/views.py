from datetime import datetime

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView
from tri.form import Form, Field
from tri.form.views import create_object, edit_object

from .models import Room


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
        form.fields['test_field'] = forms.BooleanField()

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
        if request.user.is_staff and form.fields_by_name.audit_complete:
            instance.last_audit = datetime.now()
            instance.auditor = request.user
            instance.save()

    return edit_object(
        request=request,
        instance=Room.objects.get(pk=pk),
        on_save=on_save,
        form=dict(
            include=['name', 'description', 'auditor_notes'],
            extra_fields=[
                Field.boolean(
                    name='audit_complete',
                    attr=None,  # don't write "audit_complete" to the Room object
                    show=request.user.is_staff,
                ),
            ],
            field=dict(
                auditor_notes__show=request.user.is_staff,
                description__call_target=Field.textarea,
                auditor_notes__call_target=Field.textarea,
            ),
        ),
    )

# TODO:
#  - show that tri.form will validate stuff, while django will silently pass on spelling errors

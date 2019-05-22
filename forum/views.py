from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Room


def example1(request):
    class CreateRoomForm(forms.Form):
        name = forms.CharField()

    if request.method == 'POST':
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            Room.objects.create(name=form.cleaned_data['name'])
            return HttpResponseRedirect('/thanks/')

    else:
        form = CreateRoomForm()

    return render(request, 'create_room.html', {'form': form})

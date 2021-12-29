from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import numpy as np
from pickle import load
from tensorflow import keras

from .forms import SignUpForm

def signup_view(request):
	if request.user.is_authenticated:
		return redirect('users:dashboard')
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			return redirect('users:dashboard')
		else:
			messages.error(request, 'Correct the errors below')
	else:
		form = SignUpForm()

	return render(request, 'app/signup.html', {'form': form})


@login_required
def dashboard_view(request):
	result = None
	if request.method == 'POST':
		day = int(request.POST.get("day", 0))
		fdbk = int(request.POST.get("feedback", 0))
		leave_record = int(request.POST.get("leave_record", 0))
		shift = int(request.POST.get("shift", 0))
		vehicle_condition = int(request.POST.get("vehicle_condition", 0))
		traffic_condition = int(request.POST.get("traffic_condition", 0))
		road_condition = int(request.POST.get("road_condition", 0))
		input = np.array([[day,fdbk,leave_record, shift, vehicle_condition, traffic_condition, road_condition]])
		print(input)
		result = 10
	return render(request, 'app/dashboard.html', {'result': result})


def home_view(request):
	return render(request, 'app/home.html')
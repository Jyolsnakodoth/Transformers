from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import numpy as np
from pickle import load
from tensorflow import keras

from .forms import SignUpForm
scaler = load(open('Resource/scaler.pkl', 'rb'))
model = keras.models.load_model('Resource/model/')

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
	reasons = []
	message = {}
	if request.method == 'POST':
		day = int(request.POST.get("day", 0))
		fdbk = int(request.POST.get("feedback", 0))
		leave_record = int(request.POST.get("leave_record", 0))
		shift = int(request.POST.get("shift", 0))
		vehicle_condition = int(request.POST.get("vehicle_condition", 0))
		traffic_condition = int(request.POST.get("traffic_condition", 0))
		road_condition = int(request.POST.get("road_condition", 0))
		input = np.array([[day,fdbk,leave_record, shift, vehicle_condition, traffic_condition, road_condition]])
		input = scaler.transform(input.astype(np.float))
		result = model.predict(input)[0][0]
		hrs = int(abs(result))
		minutes = round((abs(result) % 1) * 60)
		if result < 0:
			result = 'Your order is {} hours and {} minutes late'.format(hrs, minutes)
			if vehicle_condition == 16:
				reasons.append('vechicle')
			if traffic_condition == 16:
				reasons.append('traffic')
			if road_condition == 16:
				reasons.append('road')
			if not reasons:
				reasons.append('')
			message['value'] = 'Reason: Unfavourable ' + (', ').join(reasons) + ' condition'
			message['is_late'] = True
		elif result == 0:
			result = 'Your order will arrive on time'
			message['value'] = ''
		else:
			result = 'Your order is {} hours and {} minutes early'.format(hrs, minutes)
			if vehicle_condition == 15:
				reasons.append('vechicle')
			if traffic_condition == 15:
				reasons.append('traffic')
			if road_condition == 15:
				reasons.append('road')
			if not reasons:
				reasons.append('')
			message['value'] = 'Reason: Favourable ' + (', ').join(reasons) + ' condition'
			message['is_late'] = False

	return render(request, 'app/dashboard.html', {'result': result, 'reason': message})


def home_view(request):
	return render(request, 'app/home.html')
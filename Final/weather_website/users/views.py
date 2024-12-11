from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from pathlib import Path
import json
import requests

USER_DATA_FILE = settings.USER_DATA_FILE

def load_user_data():
    if Path(USER_DATA_FILE).exists():
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        users = load_user_data()
        if username in users and users[username] == password:
            request.session['username'] = username
            return redirect('weather')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        users = load_user_data()
        if username in users:
            messages.error(request, 'Username already exists')
        else:
            users[username] = password
            save_user_data(users)
            messages.success(request, 'Signup successful')
            return redirect('login')
    return render(request, 'signup.html')

def weather(request):
    if 'username' not in request.session:
        return redirect('login')  # 로그인하지 않은 사용자는 리다이렉트

    location = "울산 남구 무거동"
    api_url = f"http://api.openweathermap.org/data/2.5/onecall?lat=35.543&lon=129.318&units=metric&exclude=minutely,hourly&appid={settings.OPENWEATHER_API_KEY}"

    try:
        # API 호출
        response = requests.get(api_url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = response.json()

        # API 응답 데이터 확인
        if 'current' not in data:
            raise KeyError("'current' 키가 응답 데이터에 없습니다.")

        # 데이터 처리
        current = data['current']
        daily = data['daily']

        alert = None
        if 'rain' in current['weather'][0]['description']:
            alert = "오늘은 비 예보가 있습니다. 우산 챙기는 것 잊지마세요."
        elif 'clear' in current['weather'][0]['description']:
            alert = "오늘 날씨는 화창합니다. 나들이를 가는 건 어떨까요?"

        return render(request, 'weather.html', {
            'location': location,
            'current_temp': current['temp'],
            'current_weather': current['weather'][0]['description'],
            'today_min': daily[0]['temp']['min'],
            'today_max': daily[0]['temp']['max'],
            'daily_forecast': daily,
            'alert': alert,
        })

    except requests.exceptions.RequestException as e:
        return render(request, 'error.html', {'error': f"API 호출 오류: {str(e)}"})
    except KeyError as e:
        return render(request, 'error.html', {'error': f"API 응답 데이터 오류: {str(e)}"})

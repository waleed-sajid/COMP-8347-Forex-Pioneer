from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from forex.models import CryptoCurrency


@login_required(login_url='login')
def HomePage(request):
    return render(request, 'home.html')


def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse("Your password and confrom password are not Same!!")
        else:

            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return redirect('login')

    return render(request, 'signup.html')


def LoginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass')
        user = authenticate(request, username=username, password=pass1)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Username or Password is incorrect!!!")

    return render(request, 'login.html')


def LogoutPage(request):
    logout(request)
    return redirect('login')


# your_app_name/views.py
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json


def coin_market_datal(request):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {
        'X-CMC_PRO_API_KEY': '407f8d80-c5da-4e63-9b94-c8e208fc44a8',
        'Accepts': 'application/json',
    }
    session = Session()
    session.headers.update(headers)

    parameters = {
        'convert': "USD",
        'cryptocurrency_type': 'all',
    }
    got_data = session.get(url, params=parameters)
    in_json = json.loads(got_data.text)
    return render(request, 'coin_market_data.html', {'data': json.dumps(in_json, indent=2)})
    # except (ConnectionError, Timeout, TooManyRedirects) as e:
    # return render(request, 'error.html', {'error_message': str(e)})


def coin_market_data(request):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    headers = {
        'X-CMC_PRO_API_KEY': '407f8d80-c5da-4e63-9b94-c8e208fc44a8',
        'Accepts': 'application/json',
    }
    session = Session()
    session.headers.update(headers)

    parameters = {
        'convert': "USD",
        'cryptocurrency_type': 'all',
    }
    got_data = session.get(url, params=parameters)
    response_data = got_data.json()

    # Extract specific fields from the response
    relevant_data = []
    for cryptocurrency in response_data.get('data', []):
        crypto_info = {
            'name': cryptocurrency.get('name', ''),
            'price': cryptocurrency.get('quote', {}).get('USD', {}),
            'Percent_change_1h': cryptocurrency.get('quote', {}).get('USD', {}).get('percent_change_1h', ''),
            'Percent_change_24h': cryptocurrency.get('quote', {}).get('USD', {}).get('percent_change_24h', ''),
            'Market_cap': cryptocurrency.get('quote', {}).get('USD', {}).get('market_cap', ''),
            'Volume_24h': cryptocurrency.get('quote', {}).get('USD', {}).get('volume_24h', ''),

            # Add more fields as needed
        }
        relevant_data.append(crypto_info)
        request.session['relevant_data'] = relevant_data
    # print(response_data)
    return render(request, 'coin_market_data.html', {'data': relevant_data})
    # return JsonResponse({'data': relevant_data})


def currency_details(request, crypto_name):
    relevant_data = request.session.get('relevant_data', [])
    # Extract the details for the specific cryptocurrency
    selected_crypto = None
    for crypto_info in relevant_data:
        if crypto_info['name'] == crypto_name:
            selected_crypto = crypto_info
            break

    context = {
        'crypto_name': crypto_name,
        'selected_crypto': selected_crypto,
    }

    return render(request, 'currency_details.html', context)

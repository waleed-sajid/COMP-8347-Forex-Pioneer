from django.core.mail import send_mail
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from requests import Session
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from .models import Order, UserProfile
from forex.forms import SignupForm, LoginForm
from django.shortcuts import render
from django.contrib import messages
from .forms import PasswordResetForm
from .models import PasswordResetRequest
import secrets
import json


def HomePage(request):
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
    return render(request, 'forexPioneer/index.html', {'data': relevant_data})


def SignupPage(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            uname = form.cleaned_data['username']
            email = form.cleaned_data['email']
            pass1 = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Try to get the user, create if not exists
            user, created = User.objects.get_or_create(username=uname, defaults={'email': email, 'first_name': first_name, 'last_name': last_name})
            user.set_password(pass1)
            user.save()

            # Create UserProfile linked to the user
            user_profile = UserProfile(user=user, id_or_photo=form.cleaned_data['id_or_photo'])
            user_profile.save()

            # Send confirmation email
            send_confirmation_email(email)

            # Set a session variable to indicate successful registration
            request.session['registration_success'] = True
            return redirect('forexPioneer:login')
    else:
        form = SignupForm()

    return render(request, 'forexPioneer/signup.html', {'form': form})


def send_confirmation_email(email):
    subject = 'Welcome to Forex Pioneer'
    message = 'Thank you for registering with Forex Pioneer. Your account has been created successfully.'
    from_email = 'your_email@example.com'
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def LoginPage(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['login_success'] = True
                return redirect('forexPioneer:index')
            else:
                return HttpResponse("Username or Password is incorrect!!!")
    else:
        form = LoginForm()

    return render(request, 'forexPioneer/login.html', {'form': form})


def LogoutPage(request):
    logout(request)
    request.session.pop('login_success', False)
    request.session.pop('registration_success', False)

    return redirect('forexPioneer:index')


def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            try:
                # Check if the email exists in your user database
                user = UserProfile.objects.get(email=email)
            except UserProfile.DoesNotExist:
                messages.error(request, 'Email does not exist.')
                return redirect('forexPioneer:forgot_password')

            # Generate and save a reset token
            token = secrets.token_urlsafe(20)
            PasswordResetRequest.objects.create(email=email, token=token)

            base_url = request.build_absolute_uri('/')[:-1]

            # Send email with reset link
            subject = 'Reset Your Password'
            message = f'Click the following link to reset your password: {base_url}/reset_password/{token}'

            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            send_mail(subject, message, from_email, to_email, fail_silently=False)

            messages.success(request, 'Password reset email sent. Please check your email.')
            return redirect('forexPioneer:login')

    else:
        form = PasswordResetForm()

    return render(request, 'forexPioneer/forget_password.html', {'form': form})


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
    return render(request, 'forexPioneer/currency_details.html', context)


stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000/forexPioneer'


# home view
def home(request):
    return render(request, 'forexPioneer/checkout.html')


# success view
def success(request):
    return render(request, 'forexPioneer/success.html')


# cancel view
def cancel(request):
    return render(request, 'forexPioneer/cancel.html')


@csrf_exempt
def checkout(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body.decode('utf-8'))
        customer_email = data.get('customer_email', '')
    except json.JSONDecodeError:
        customer_email = ''

    order = Order(email=customer_email, paid=False, amount=0, description="")
    order.save()

    session = stripe.checkout.Session.create(
        client_reference_id=request.user.id if request.user.is_authenticated else None,
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': 'Intro to Django Course',
                },
                'unit_amount': 10000,
            },
            'quantity': 1,
        }],
        metadata={
            "order_id": order.id
        },
        mode='payment',
        success_url=YOUR_DOMAIN + '/success.html',
        cancel_url=YOUR_DOMAIN + '/cancel.html',
    )
    print(session)

    return JsonResponse({'id': session.id})


@csrf_protect
def webhook(request):
    print("Webhook")
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        session = event['data']['object']
        # creating order
        customer_email = session["customer_details"]["email"]
        price = session["amount_total"] / 100
        sessionID = session["id"]
        ID = session["metadata"]["order_id"]
        Order.objects.filter(id=ID).update(email=customer_email, amount=price, paid=True, description=sessionID)

    return HttpResponse(status=200)

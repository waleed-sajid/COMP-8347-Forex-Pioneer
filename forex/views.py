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
import json
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError


def latest_listing(request):
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
        'limit': 100
    }
    got_data = session.get(url, params=parameters)
    response_data = got_data.json()

    # Extract specific fields from the response
    relevant_data = []
    for cryptocurrency in response_data.get('data', []):
        crypto_info = {
            'name': cryptocurrency.get('name', ''),
            'price': cryptocurrency.get('quote', {}).get('USD', {}).get('price', ''),
            'Percent_change_1h': cryptocurrency.get('quote', {}).get('USD', {}).get('percent_change_1h', ''),
            'Percent_change_24h': cryptocurrency.get('quote', {}).get('USD', {}).get('percent_change_24h', ''),
            'Market_cap': cryptocurrency.get('quote', {}).get('USD', {}).get('market_cap', ''),
            'Volume_24h': cryptocurrency.get('quote', {}).get('USD', {}).get('volume_24h', ''),
        }
        relevant_data.append(crypto_info)

    # Sort the relevant_data based on the 'price' key
    relevant_data_price_sorted = sorted(relevant_data, key=lambda x: x['price'], reverse=True)

    # Take only the top 9 currencies based on price
    top_10_currencies_price = relevant_data_price_sorted[:9]

    # Sort the relevant_data based on the 'market_cap' key
    relevant_data_market_cap_sorted = sorted(relevant_data, key=lambda x: x['Market_cap'], reverse=True)

    # Take only the top 6 currencies based on market cap
    top_6_currencies_market_cap = relevant_data_market_cap_sorted[:6]

    # Update the session with the latest data (outside the loop)
    request.session['relevant_data'] = relevant_data

    return render(request, 'forexPioneer/index.html', {
        'data': relevant_data,
        'top_10_currencies_price': top_10_currencies_price,
        'top_6_currencies_market_cap': top_6_currencies_market_cap,
    })


def map_historical(request):
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map'
    headers = {
        'X-CMC_PRO_API_KEY': '407f8d80-c5da-4e63-9b94-c8e208fc44a8',
        'Accepts': 'application/json',
    }
    session = Session()
    session.headers.update(headers)

    parameters = {
        'limit': 100
    }
    got_data = session.get(url, params=parameters)
    response_data = got_data.json()

    # Extract specific fields from the response
    relevant_data = []
    for cryptocurrency in response_data.get('data', []):
        crypto_info = {
            'name': cryptocurrency.get('name', ''),
            'symbol': cryptocurrency.get('symbol', ''),
            'slug': cryptocurrency.get('slug', ''),
            'rank': cryptocurrency.get('rank', ''),
            'first_historical_data': cryptocurrency.get('first_historical_data', ''),
            'last_historical_data': cryptocurrency.get('last_historical_data', ''),
            # Add more fields as needed
        }
        relevant_data.append(crypto_info)

    # Update the session with the latest data
    request.session['relevant_data'] = relevant_data

    return render(request, 'forexPioneer/historical.html', {'data': relevant_data})


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
            user, created = User.objects.get_or_create(username=uname,
                                                       defaults={'email': email, 'first_name': first_name,
                                                                 'last_name': last_name})
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
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, 'Email does not exist.')
                return redirect('forexPioneer:forgot_password')

            # Generate and save a reset token using Django's built-in utility
            token = default_token_generator.make_token(user)
            PasswordResetRequest.objects.create(email=email, token=token)

            base_url = request.build_absolute_uri('/')[:-1]

            # Send email with reset link
            subject = 'Reset Your Password'
            reset_url = reverse('forexPioneer:reset_password', kwargs={'token': token})
            reset_url = f'{base_url}{reset_url}'
            message = f'Click the following link to reset your password: {reset_url}'

            from_email = settings.EMAIL_HOST_USER
            to_email = [email]

            try:
                send_mail(subject, message, from_email, to_email, fail_silently=False)
                messages.success(request, 'Password reset email sent. Please check your email.')
            except Exception as e:
                messages.error(request, f'Error sending password reset email: {str(e)}')

            return redirect('forexPioneer:login')

    else:
        form = PasswordResetForm()

    return render(request, 'forexPioneer/forget_password.html', {'form': form})


def password_reset_view(request, token):
    try:
        password_reset_request = PasswordResetRequest.objects.get(token=token)
        # Check if the token is still valid (e.g., not expired)
        if password_reset_request.is_valid():
            # Render a form for the user to set a new password
            return render(request, 'forexPioneer/reset_password_form.html', {'token': token})
        else:
            messages.error(request, 'Invalid or expired token for password reset.')
            return redirect('forexPioneer:login')
    except PasswordResetRequest.DoesNotExist:
        messages.error(request, 'Invalid or expired token for password reset.')
        return redirect('forexPioneer:login')


def reset_password_submit(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        try:
            password_reset_request = PasswordResetRequest.objects.get(token=token)
            # Check if the token is still valid (e.g., not expired)
            if password_reset_request.is_valid():
                # Update the user's password
                user = User.objects.get(email=password_reset_request.email)
                user.set_password(new_password)
                user.save()

                # Log in the user
                user = authenticate(request, username=user.username, password=new_password)
                login(request, user)

                # Mark the token as used or delete it
                password_reset_request.used = True
                password_reset_request.save()

                messages.success(request, 'Password reset successful.')
                return redirect('forexPioneer:index')
            else:
                messages.error(request, 'Invalid or expired token for password reset.')
        except PasswordResetRequest.DoesNotExist:
            messages.error(request, 'Invalid or expired token for password reset.')

    return redirect('forexPioneer:login')


def currency_details(request, crypto_name):
    relevant_data = request.session.get('relevant_data', [])
    # Extract the details for the specific cryptocurrency
    selected_crypto = None
    for crypto_info in relevant_data:
        if crypto_info['name'] == crypto_name:
            selected_crypto = crypto_info
            break

    # Store the selected cryptocurrency data in the session
    request.session['selected_crypto'] = selected_crypto

    context = {
        'crypto_name': crypto_name,
        'selected_crypto': selected_crypto,
    }
    return render(request, 'forexPioneer/currency_details.html', context)


stripe.api_key = settings.STRIPE_PRIVATE_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000/forexPioneer'


# home view
def home(request):
    # Retrieve the selected cryptocurrency data from the session
    selected_crypto = request.session.get('selected_crypto', None)

    if selected_crypto:
        context = {
            'crypto_name': selected_crypto['name'],
            'crypto_price': selected_crypto['price']['price'],
        }
        return render(request, 'forexPioneer/checkout.html', context)
    else:
        return render(request, 'forexPioneer/checkout.html', {})


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
        quantity = int(data.get('quantity', 1))

        # Dynamic calculation logic based on your requirements
        crypto_price = float(data.get('crypto_price', 0.0))  # Assuming 'crypto_price' is a float
        total_amount = crypto_price
        amount_to_be_saved = round(total_amount * quantity, 2)

        # Get or create a user instance
        user_instance = request.user if request.user.is_authenticated else None

        order = Order(user=user_instance, email=customer_email, paid=True, amount=amount_to_be_saved, description="")
        order.save()

        session = stripe.checkout.Session.create(
            client_reference_id=request.user.id if request.user.is_authenticated else None,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # Adjust currency as needed
                    'product_data': {
                        'name': 'Amount to be paid',  # Replace with your product name
                    },
                    'unit_amount': int(total_amount * 100),  # Convert to cents
                },
                'quantity': quantity,
            }],
            metadata={
                "order_id": order.id
            },
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
        )

        return JsonResponse({'id': session.id})
    except IntegrityError as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


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


@login_required
def orders(request):
    # Retrieve orders for the logged-in user
    user_orders = Order.objects.filter(user=request.user)

    return render(request, 'forexPioneer/orders.html', {'user_orders': user_orders})


def about(request):
    return render(request, 'forexPioneer/about.html')


def contact(request):
    return render(request, 'forexPioneer/contact.html')

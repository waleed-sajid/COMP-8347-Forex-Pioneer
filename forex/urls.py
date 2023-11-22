from django.urls import path
from forex import views

app_name = 'forexPioneer'

urlpatterns = [
    path('signup/', views.SignupPage, name='signup'),
    path('index/', views.HomePage, name='index'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutPage, name='logout'),
    path('currency_details/<str:crypto_name>/', views.currency_details, name='currency_details'),
    # path('forgot_password/', views.forgot_password, name='forgot_password'),
]

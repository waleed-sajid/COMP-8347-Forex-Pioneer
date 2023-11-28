from django.urls import path
from forex import views
from forex.views import CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
from .views import CustomPasswordResetCompleteView
app_name = 'forexPioneer'

urlpatterns = [
    path('signup/', views.SignupPage, name='signup'),
    path('', views.HomePage, name='index'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutPage, name='logout'),
    path('currency_details/<str:crypto_name>/', views.currency_details, name='currency_details'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('home/', views.home,name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('success.html/', views.success,name='success'),
    path('cancel.html/', views.cancel,name='cancel'),
    path('webhooks/stripe/', views.webhook,name='webhook'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/<str:uidb64>/<slug:token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    #path('password_reset_complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),

]

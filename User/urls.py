from django.urls import path

from User import views

urlpatterns = [
    path('', views.UserView.as_view()),
    path('me', views.UserMeView.as_view()),
    path('email', views.UserEmailView.as_view()),
    path('phone', views.UserPhoneView.as_view()),
    path('bark', views.UserBarkView.as_view()),
    path('email/captcha', views.UserEmailCaptchaView.as_view()),
    path('phone/captcha', views.UserPhoneCaptchaView.as_view()),
    path('bark/captcha', views.UserBarkCaptchaView.as_view()),
    path('<str:name>', views.UserNameView.as_view()),
]

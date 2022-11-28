from django.urls import path

from Host import views

urlpatterns = [
    path('', views.HostView.as_view()),
    path('report/disk', views.ReportDiskView.as_view()),
    path('report/disk/memory', views.ReportDiskMemoryView.as_view()),

    path('@<str:name>', views.HostNameView.as_view()),
    path('@<str:name>/disk', views.HostDiskView.as_view()),
    path('@<str:name>/disk/@<str:disk_name>', views.HostDiskNameView.as_view()),
    path('@<str:name>/auth', views.HostAuthView.as_view()),

    path('@<str:name>/userdisk/percentage', views.UserDiskPercentageView.as_view()),
    path('@<str:name>/userdisk/@<str:disk_name>', views.UserDiskView.as_view()),
]

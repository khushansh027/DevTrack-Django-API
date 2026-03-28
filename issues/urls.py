from django.urls import path
from issues import views

urlpatterns = [
    path('reporters/', views.reporters_view),
    path('issues/', views.issues_view),
]


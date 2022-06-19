from django.urls import path, include
from .views import DevelopmentsListView, FilterDevelopmentsListView


urlpatterns = [
    path('', DevelopmentsListView.as_view(), name='developments'),
    path('filter', FilterDevelopmentsListView.as_view(), name='filter_developments'),
]
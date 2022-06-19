from django.urls import path, include
from .views import LocalLoreListView, FilterLocalLoreView#, JsonFilterLocalLoreView


urlpatterns = [
    path('', LocalLoreListView.as_view(), name='local_lore'),
    path('filter', FilterLocalLoreView.as_view(), name='filter_local_lore'),
]
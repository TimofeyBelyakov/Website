from django.urls import path, include
from .views import MainView


urlpatterns = [
    path('', MainView.as_view(), name='main_ru'),
    path('<slug:lang>/', MainView.as_view(), name='main_extra_lang'),
    path('<slug:lang>/our_land/', include('our_land.urls')),
    path('<slug:lang>/local_lore/', include('local_lore_knowledge.urls')),
    path('<slug:lang>/developments/', include('methodical_developments.urls'))
]
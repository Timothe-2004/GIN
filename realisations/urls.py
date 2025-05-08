from django.urls import path
from .views import RealisationListCreateView, RealisationRetrieveUpdateDestroyView

urlpatterns = [
    path('', RealisationListCreateView.as_view(), name='realisation-list'),
    path('<int:pk>/', RealisationRetrieveUpdateDestroyView.as_view(), name='realisation-detail'),
]
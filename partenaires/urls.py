from django.urls import path
from .views import (
    PartenaireListCreateView,
    PartenaireRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('', PartenaireListCreateView.as_view(), name='partenaire-list-create'),
    path('<int:pk>/', PartenaireRetrieveUpdateDestroyView.as_view(), name='partenaire-detail'),
]

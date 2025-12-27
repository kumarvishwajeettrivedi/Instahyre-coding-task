from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterView, AddReviewView, PlaceSearchView, PlaceDetailView, api_root

urlpatterns = [
    path('', api_root, name='api-root'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('reviews/', AddReviewView.as_view(), name='add-review'),
    path('places/search/', PlaceSearchView.as_view(), name='place-search'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
]

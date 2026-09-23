from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('request/<int:property_id>/', views.send_rental_request, name='send_request'),
    path('request/<int:pk>/cancel/', views.cancel_rental_request, name='cancel_request'),
    path('request/<int:pk>/accept/', views.accept_rental_request, name='accept_request'),
    path('request/<int:pk>/reject/', views.reject_rental_request, name='reject_request'),
    path('owner-dashboard/', views.owner_dashboard_view, name='owner_dashboard'),
    path('tenant-dashboard/', views.tenant_dashboard_view, name='tenant_dashboard'),
]

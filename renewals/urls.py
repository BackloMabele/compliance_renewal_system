from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_renewal, name='create_renewal'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('delete/<int:pk>/', views.delete_renewal, name='delete_renewal'),
    path('detail/<int:pk>/', views.renewal_detail, name='renewal_detail'),
    path('update/<int:pk>/', views.update_renewal, name='update_renewal'),
    path('bulk-delete/', views.bulk_delete_renewals, name='bulk_delete_renewals'),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                                             # Route for the home page
    path('register/', views.register, name='register'),                            # Route for user registration
    path('login/', views.login_view, name='login'),                                # Route for user login
    path('logout/', views.logout_view, name='logout'),                             # Route for logging out the user
    path('superuser/dashboard/', views.superuser_dashboard, name='superuser_dashboard'),  # Superuser dashboard view
    path('superuser/register_admin/', views.register_admin, name='register_admin'),  # Register admin view
    path('dashboard/', views.dashboard, name='dashboard'),  # User and admin dashboard view
    path('upload/', views.upload_assignment, name='upload'),  # Upload assignment view
    path('assignments/accept/<str:assignment_id>/', views.accept_assignment, name='accept_assignment'),  # Accept assignment
    path('assignments/reject/<str:assignment_id>/', views.reject_assignment, name='reject_assignment'),  # Reject assignment
]

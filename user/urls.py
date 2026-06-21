from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('list/', views.UserList.as_view(), name='user_list'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('<int:user_id>/', views.UserDetail.as_view(), name='user_detail'),
    path('edit-profile/', views.EditProfile.as_view(), name='edit_profile_me'),
    path('change-password/', views.ChangePassword.as_view(),
         name='change_password_me'),
]

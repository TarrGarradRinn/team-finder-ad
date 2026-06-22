from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import DetailView, ListView

from team_finder.constants import PAGINATE_BY

from .forms import ChangePasswordForm, EditProfileForm, LoginForm, RegisterForm
from .models import User


class UserList(ListView):
    """Список всех пользователей"""
    model = User
    template_name = 'users/participants.html'
    context_object_name = 'participants'
    ordering = 'id'
    paginate_by = PAGINATE_BY


class UserDetail(DetailView):
    """Страница пользователя"""
    model = User
    template_name = 'users/user-details.html'
    context_object_name = 'user'
    pk_url_kwarg = 'user_id'


class Register(View):
    """Регистрация"""

    def get(self, request):
        form = RegisterForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:login')
        return render(request, 'users/register.html', {'form': form})


class Login(View):
    """Вход"""

    def get(self, request):
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
            )
            if user:
                login(request, user)
                return redirect('projects:list')
            form.add_error(None, 'Неверный email или пароль')
        return render(request, 'users/login.html', {'form': form})


class Logout(View):
    """Выход"""

    def get(self, request):
        logout(request)
        return redirect('projects:list')


class EditProfile(LoginRequiredMixin, View):

    def get(self, request):
        form = EditProfileForm(instance=request.user)
        return render(request, 'users/edit_profile.html', {'form': form})

    def post(self, request):
        form = EditProfileForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.avatar:
                user.avatar = user.generate_avatar()
            user.save()
            return redirect('users:detail')
        return render(request, 'users/edit_profile.html', {'form': form})


class ChangePassword(LoginRequiredMixin, View):

    def get(self, request):
        form = ChangePasswordForm(user=request.user)
        return render(request, 'users/change_password.html', {'form': form})

    def post(self, request):
        form = ChangePasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            return redirect('users:detail')
        return render(request, 'users/change_password.html', {'form': form})

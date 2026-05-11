from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User
from .tokens import account_activation_token
from .utils import send_welcome_email, send_password_reset_email

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Ativado automaticamente (pode usar email activation depois)
            user.save()
            
            # Envia email de boas-vindas
            try:
                send_welcome_email(user)
            except Exception:
                pass  # Falha silenciosa em desenvolvimento
            
            # Faz login automaticamente
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo ao Dimbo Tools.')
            return redirect('dashboard:index')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_invalid(self, form):
        messages.error(self.request, 'Email ou palavra-passe incorretos.')
        return super().form_invalid(form)


@login_required
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password(request):
    from django.contrib.auth.forms import PasswordChangeForm

    from .forms import CustomPasswordChangeForm 
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'A sua palavra-passe foi alterada.')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def send_mail(self, subject_template_name, email_template_name, context, from_email, to_email, html_email_template_name=None):
        """Envia email customizado usando a nossa função"""
        user = context.get('user')
        reset_url = self.request.build_absolute_uri(reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': context['uid'],
            'token': context['token'],
        }))
        send_password_reset_email(user, reset_url)


def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')
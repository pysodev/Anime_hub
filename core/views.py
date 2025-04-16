from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from users.models import User  # Corrected import
from django.contrib.auth.hashers import make_password  
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail 
from django.conf import settings
from django.core.validators import EmailValidator 
from django.core.exceptions import ValidationError 
from django.conf import settings
import uuid  # For generating unique tokens
from django.utils import timezone # For handling expiry
from anime.models import Genre, Anime
from django.contrib.auth import get_user_model  # Import get_user_model

# Assuming your User model is defined in core/models.py

class PasswordResetRequestView(View):
    def get(self, request):
        return render(request, 'password_reset_request.html')

    def post(self, request):
        email = request.POST.get('email')
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            token = uuid.uuid4().hex
            user.reset_token = token
            user.reset_token_expiry = timezone.now() + timezone.timedelta(hours=1) # Token expires in 1 hour
            user.save()
            self.send_password_reset_email(user.email, token)
            return render(request, 'password_reset_sent.html')
        except User.DoesNotExist:
            return render(request, 'password_reset_request.html', {'error': 'No user found with this email.'})

    def send_password_reset_email(self, email, token):
        subject = 'Password Reset Request'
        message = f'Click the following link to reset your password: http://127.0.0.1:8000/password_reset_confirm/{token}/'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

class PasswordResetConfirmView(View):
    def get(self, request, token):
        User = get_user_model()
        try:
            user = User.objects.get(reset_token=token, reset_token_expiry__gt=timezone.now())
            return render(request, 'password_reset_confirm.html', {'token': token})
        except User.DoesNotExist:
            return render(request, 'password_reset_invalid.html')

    def post(self, request, token):
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if password != confirm_password:
            return render(request, 'password_reset_confirm.html', {'token': token, 'error': 'Passwords do not match.'})

        User = get_user_model()
        try:
            user = User.objects.get(reset_token=token, reset_token_expiry__gt=timezone.now())
            user.password = make_password(password)
            user.reset_token = None
            user.reset_token_expiry = None
            user.save()
            return render(request, 'password_reset_complete.html')
        except User.DoesNotExist:
            return render(request, 'password_reset_invalid.html')

class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page upon successful login
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})


class SignupView(View):
    def get(self, request):
        return render(request, 'signup.html')

    def post(self, request):
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        dob = request.POST.get('dob')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirmPassword')

        errors = {}
        if password != confirm_password:
            errors['password_mismatch'] = "Passwords do not match."
        if len(password) < 8 or not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
            errors['password_rules'] = "Password must be at least 8 characters long and include letters and numbers."

        if errors:
            return render(request, 'signup.html', {'errors': errors, 'firstName': first_name, 'lastName': last_name, 'dob': dob})
        

        email_validator = EmailValidator()
        try:
            email_validator(email)
        except ValidationError:
            errors['email_invalid'] = "Invalid email address."


        if errors:
            return render(request, 'signup.html', {'errors': errors, 'firstName': first_name, 'lastName': last_name, 'dob': dob, 'email': email})

        # Generate a unique username
        base_username = f"{first_name.lower()}{last_name.lower()[:2]}"
        username = self.generate_unique_username(base_username)

        # Hash the password
        hashed_password = make_password(password)

        # Create a new user in the NoSQL database
        user = User(first_name=first_name, last_name=last_name, dob=dob, username=username, password=hashed_password, email=email)
        user.save()

        self.send_welcome_email(username, email)

        return redirect('login') # Redirect to the login page after successful signup

    def generate_unique_username(self, base_username):
        counter = 0
        while True:
            username = base_username
            if counter > 0:
                username += str(counter)
            try:
                User.objects.get(username=username) # Check if the username exists
                counter += 1
            except ObjectDoesNotExist:
                return username

    def send_welcome_email(self, username, email):
        subject = 'Welcome to Anime HUB!'
        message = f'Hi {username}, welcome to Anime HUB! Thank you for signing up.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the home page upon successful login
        else:
            return render(request, 'login.html', {'error_message': 'Invalid username or password'})

@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')

@method_decorator(login_required, name='dispatch')
class HomeView(View):
    def get(self, request):
        genres = Genre.objects.all()
        # You'll later fetch and pass anime data here as well
        return render(request, 'home.html', {'genres': genres})


def logout_view(request):
    logout(request)
    return redirect('login')
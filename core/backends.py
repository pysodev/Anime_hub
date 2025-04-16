from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from users.models import User

class NoSQLAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)  # Adjust based on your model manager
            if check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)  # Adjust based on how you identify users in NoSQL
        except User.DoesNotExist:
            return None
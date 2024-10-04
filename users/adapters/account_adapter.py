from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_username
from users.models import CustomUser

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data['email']
        else:
            email = None

        existing_user = CustomUser.objects.filter(email=email).first()

        if existing_user:
            sociallogin.connect(request, existing_user)
        else:
            user = sociallogin.user
            user_email(user, email)
            user_username(user, email)
            user.save()

            sociallogin.connect(request, user)

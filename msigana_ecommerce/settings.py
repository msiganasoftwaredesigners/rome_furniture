import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# GENERAL SETTINGS
# SECRET_KEY = config('SECRET_KEY')
SECRET_KEY=django-indesecure-$epx^r=3u8b8ptdfr+yc_3&e)50gr1%-@3jgpl#j-&9&am#$2on*8

# DEBUG = config('DEBUG', default=True, cast=bool)
# DEBUG = True
# # ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# ALLOWED_HOSTS=True

DEBUG = True

# ALLOWED_HOSTS configuration
ALLOWED_HOSTS = ["localhost","romefurnitures.com"]


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'corsheaders',
    'users.apps.UsersConfig',
    'category.apps.CategoryConfig',
    'store.apps.StoreConfig',
    'footer.apps.FooterConfig',
    'contact.apps.ContactConfig',
    'blog.apps.BlogConfig', 
    'heads.apps.HeadsConfig',
    'advertizement.apps.AdvertizementConfig',
    'nested_admin',
    'theme',
    'django_quill',
    # 'django_browser_reload' if DEBUG else '',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
]

INSTALLED_APPS = [app for app in INSTALLED_APPS if app]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware' if not DEBUG else '',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django_browser_reload.middleware.BrowserReloadMiddleware" if DEBUG else '',
]

MIDDLEWARE = [mw for mw in MIDDLEWARE if mw]


# DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         }
#     }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'romefupk_rome_furniture',
        'HOST': 'localhost',
        'PORT': 3306,
        'USER': 'romefupk_rome_furniture',
        'PASSWORD': 'Melaku11@#',
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', default='localhost'),
#         'PORT': config('DB_PORT', default='3306'),
#     }
# }


# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'category.context_processors.menu_links', 
                'footer.context_processors.footer',
                'heads.context_processors.head_contents',
                'store.context_processors.most_liked_products',
                'advertizement.context_processors.favicon',
                'users.context_processors.liked_products',
            ],
        },
    },
]

# AUTHENTICATION
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# STATIC AND MEDIA FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
   

# else:
#     STATIC_URL = '/static/'
#     STATIC_ROOT = '/home/kodeplwq/kode_plc/staticfiles/'

STATICFILES_DIRS = [
BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'




STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": BASE_DIR / "media",
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}



# EMAIL AND ACCOUNT SETTINGS
ACCOUNT_EMAIL_VERIFICATION = 'none'  
LOGIN_REDIRECT_URL = '/admin'  
SOCIALACCOUNT_QUERY_EMAIL = True  

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# SECURITY SETTINGS FOR PRODUCTION
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_COOKIE_HTTPONLY = True

# OTHER SETTINGS
ROOT_URLCONF = 'msigana_ecommerce.urls'
WSGI_APPLICATION = 'msigana_ecommerce.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# SOCIAL ACCOUNT PROVIDERS
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID'),
            'secret': config('GOOGLE_SECRET'),
        }
    },
    'facebook': {
        'APP': {
            'client_id': config('FACEBOOK_CLIENT_ID'),
            'secret': config('FACEBOOK_SECRET'),
        },
        'SCOPE': ['email', 'public_profile', 'user_friends'],
    }
}

ACCOUNT_FORMS = {'signup': 'users.forms.CustomSignupForm'}
SOCIALACCOUNT_ADAPTER = 'users.adapters.account_adapter.CustomSocialAccountAdapter'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'
CORS_ALLOW_ALL_ORIGINS = not DEBUG



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.kodeplc.com' 
EMAIL_PORT = 465  
EMAIL_USE_SSL = True  
EMAIL_USE_TLS = False  
EMAIL_HOST_USER = 'info@romefurniture.com'  
EMAIL_HOST_PASSWORD = 'KodePLC11@#'  
DEFAULT_FROM_EMAIL = 'info@kodeplc.com'  
ADMIN_EMAIL = 'info@kodeplc.com'  

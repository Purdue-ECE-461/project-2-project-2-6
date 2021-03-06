from dotenv import load_dotenv
from pathlib import Path
import os


load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")
PROD_DATABASE_PASSWORD = os.environ.get('PROD_DATABASE_PASSWORD')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'ece461-project2-6.uc.r.appspot.com',
    'localhost',
    '127.0.0.1'
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registry.apps.RegistryConfig',
    'rest_framework',
    'corsheaders'
]

CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'package_registry.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'package_registry.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    # PRODUCTION
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'npm-db',
        'USER': 'postgres',
        'PASSWORD': PROD_DATABASE_PASSWORD,
        'HOST': '/cloudsql/ece461-project2-6:us-central1:npm-db',
        'PORT': '5432'
    }

    # PROXY CLOUDSQL
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'npm-db',
    #     'USER': 'postgres',
    #     'PASSWORD': PROD_DATABASE_PASSWORD,
    #     'HOST': '127.0.0.1',
    #     'PORT': '3306'
    # }

    # DEVELOPMENT
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': "devDB",
    #     'USER': "postgres",
    #     'PASSWORD': "1234",
    #     'HOST': 'localhost',
    #     'PORT': '5432'
    # }
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 4294967295  #4GB limit for storage

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
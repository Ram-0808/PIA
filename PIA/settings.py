import os
import datetime
from pathlib import Path

from django.core.management.utils import get_random_secret_key

from dotenv import load_dotenv

load_dotenv()


SAFE_MODE = os.getenv("SAFE_MODE", "False") == "True"

DYNAMICS_SAFE_MODE = SAFE_MODE or os.getenv("DYNAMICS_SAFE_MODE", "False") == "True"

FLOW_SAFE_MODE = SAFE_MODE or os.getenv("FLOW_SAFE_MODE", "False") == "True"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())


# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = os.getenv("DEBUG", "False") == "True"


URL_SCHEMA = os.getenv('URL_SCHEMA', "http")
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
CSRF_TRUSTED_ORIGINS = [ URL_SCHEMA +'://'+host for host in ALLOWED_HOSTS ]

GLOBAL_API_URL = os.getenv("GLOBAL_API_URL", URL_SCHEMA + '://' + ALLOWED_HOSTS[0])
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dynamic_preferences',
    

    
    # 'rest_framework_simplejwt.token_blacklist',

    'rest_framework',
    'drf_spectacular',
    'django_filters',
    'dbbackup',
    'import_export',
    'imagekit',
    'django_admin_listfilter_dropdown',
    'rangefilter',
    'django_crontab',
     
    'admin_auto_filters',
    
    'Core.Core',
    'Core.Users',
    'Core.System',
    'Core.Reports',
    'DynamicDjango',
    'Dynamics',
    'Users',
    'Masters',
    'Core.node',
    # 'advanced_filters',
    'thirdparty',
    'General',

    'LeadManagement',
    'ProjectManagement',
    'TenderManagement',
    'PurchaseIndent',
    'PurchaseEnquiry',
    'CompareQuotation',
    'Quotation',
    'BOQ',

    'PurchaseOrder',
    'Payments',
    'MaterialRequest',
    'TaskManagement',
    'ActionManagement',
    'ServiceManagement',

    'FileSystem',
    
]

APP_LABEL = 'Absolin'
USER_MODELS = [
                {
                    'name': 'User',
                    'type': 'User',
                    'model': 'Users.User',
                },
                {
                    'name': 'Technician',
                    'type': 'Technician',
                    'model': 'Users.Technician',
                }
            ]


AUTH_USER_MODEL = 'Users.User'



REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'Core.Core.authentication.Authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ),
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
        'Core.Core.permissions.permissions.AllPermissions',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PAGINATION_CLASS': 'Core.Core.pagination.Paginations.StandardResultsSetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    # Other Django REST framework settings
}


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 'Common.middleware.SqlPrintingMiddleware',
    'Core.Core.middleware.allpermissions.allPermissionsMiddleware',
    'Core.Core.middleware.error.ErrorMiddleware',
    # 'Common.middleware.TimezoneMiddleware',

    'corsheaders.middleware.CorsMiddleware',
]


AUTHENTICATION_BACKENDS = [
    # 'django.contrib.auth.backends.ModelBackend',
    'Core.Core.authentication.Authentication.CustomAuthenticationBackend',
    # 'django.contrib.auth.backends.ModelBackend',
    # 'Users.auth_backends.UserTypeBackend',
    # 'Users.auth_backends.OrganizerAuthenticationBackend',
]


# AUTHENTICATION_BACKENDS = ('Common.Authentication.CustomAuthenticationBackend',)

DYNAMICS_APP_LABEL = os.getenv("DYNAMICS_APP_LABEL", 'Absolin')
GENERAL_APP_LABEL = 'General'

INSTALLED_APPS += [ 'corsheaders',]

CORS_ORIGIN_ALLOW_ALL = True

# CORS_ORIGIN_WHITELIST = (
#   'http://localhost:8000',
# )

ROOT_URLCONF = 'PIA.urls'

APPEND_SLASH = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'build'),os.path.join('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'dynamic_preferences.processors.global_preferences',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'common_tags': 'Core.Core.filters.TemplateFilters',
            },
        },
    },
]

WSGI_APPLICATION = 'PIA.wsgi.application'

if os.getenv("DEBUG", "False") == "True" and os.getenv("DB_NAME", None) is None:
    raise Exception("DB_NAME environment variable not defined")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pia_db',
        'USER': 'postgres',
        'PASSWORD': '12345',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
    }
}

CACHE_TIME_OUT_ONE_YEAR = 60 * 60 * 24 * 365
CACHE_TIME_OUT_ONE_MONTH = 60 * 60 * 24 * 30

import sys
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test_db.sqlite3'
    }


ACCESS_TOKEN_LIFETIME =  datetime.timedelta(days=365) #minutes=120
REFRESH_TOKEN_LIFETIME = datetime.timedelta(days=365) #days=1


LOGIN_URL = '/admin/login/' 
LOGOUT_URL = '/admin/logout/'

SPECTACULAR_SETTINGS = {
    'TITLE': 'PIA API',
    'DESCRIPTION': 'PIA API',
    'VERSION': '1.0.0',
    'LICENSE': {'name': 'Closed License'},
    'CONTACT': {'email': 'admin@absolinsoft.com'},
    'SERVE_INCLUDE_SCHEMA': False,    # /schema/ endpoint is not  included in the generated schema.
    'SECURITY': [{'Bearer': []}],

    'SWAGGER_UI_SETTINGS': {
        'docExpansion': 'none',
        'deepLinking': True,
        'defaultModelRendering': 'model',
        'displayRequestDuration': True,
        'filter': True,
        'persistAuthorization': False,
        "displayOperationId": True,
    },

    'SERVERS': [
        {'url': '/', 'description': '(HTTP or HTTPS)'},
    ],

    'SERVE_AUTHENTICATION': ['rest_framework.authentication.SessionAuthentication'],

    'SERVE_PERMISSIONS': ['rest_framework.permissions.IsAuthenticated'],

    "EXTENSIONS_INFO": {
        "x-login-url": "/api/login/",
        "x-logout-url": "/api/logout/",
    }, 

}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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

# AUTHENTICATION_BACKENDS = ('Common.Authentication.CustomAuthenticationBackend',)

SINGLE_MOBILE_DEVICE_PER_USER = False

# IMPORT_EXPORT_USE_TRANSACTIONS = True 

# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Kolkata'



USE_I18N = True

USE_L10N = True

USE_TZ = True

USE_GLOBAL_URL = True


STATICFILES_DIRS = [ os.path.join(BASE_DIR, 'static_assets'),os.path.join(BASE_DIR, 'build/static'),]
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

DBBACKUP_FILENAME_TEMPLATE = 'backup-{datetime}.sql'
BACKUP_DIRECTORY = r'db/backup'
DBBACKUP_STORAGE_OPTIONS = {'location': BACKUP_DIRECTORY}

# DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
# DBBACKUP_STORAGE_OPTIONS = {'location': os.path.join(BASE_DIR, 'media\\backup')}


USE_S3 = False


if USE_S3:
    # AWS S3 Configrations
    INSTALLED_APPS += ['storages']
    
    AWS_ACCESS_KEY_ID = ''
    AWS_SECRET_ACCESS_KEY = ''
    AWS_STORAGE_BUCKET_NAME = ''
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

    # ap-south-1
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }

    AWS_S3_REGION_NAME = 'ap-south-1' #change to your region
    AWS_S3_SIGNATURE_VERSION = 's3v4'

    AWS_STATIC_LOCATION = 'static'
    # STATICFILES_STORAGE = 'Common.storage_backends.StaticStorage'
    # STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_STATIC_LOCATION)
    STATIC_URL = 'static/'

    AWS_PUBLIC_MEDIA_LOCATION = 'media/public'
    PUBLIC_FILE_STORAGE = 'Common.storage_backends.PublicMediaStorage'

    AWS_PRIVATE_MEDIA_LOCATION = 'media'
    PRIVATE_FILE_STORAGE = 'Common.storage_backends.PrivateMediaStorage'

    DEFAULT_FILE_STORAGE = PRIVATE_FILE_STORAGE

    MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, AWS_PRIVATE_MEDIA_LOCATION)

    # IMAGEKIT_DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    # STATICFILES_DIRS = [
    #     os.path.join(BASE_DIR, 'static'),
    # ]
    
    AWS_DBBACKUP_MEDIA_LOCATION = r'db/backups/'
    DBBACKUP_STORAGE = 'Common.storage_backends.DBBackupStorage'
    # DBBACKUP_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DBBACKUP_STORAGE_OPTIONS = {
        'access_key': AWS_ACCESS_KEY_ID,
        'secret_key': AWS_SECRET_ACCESS_KEY,
        'bucket_name': AWS_STORAGE_BUCKET_NAME,
        'location': AWS_DBBACKUP_MEDIA_LOCATION,
        'encrypt_key': True,  # Enable encryption
    }
else:
    # STATIC IN LOCALS
    STATIC_URL = 'static/'

    MEDIA_ROOT =  os.path.join(BASE_DIR, 'media')
    MEDIA_URL = 'media/'

    DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'

    DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
    BACKUP_FILE_NAME = 'backup-{datetime}.sql'
    BACKUP_FILE_PATH = os.path.join(BACKUP_DIRECTORY, BACKUP_FILE_NAME)
    DBBACKUP_STORAGE_OPTIONS = {'location': BACKUP_DIRECTORY}

    def generate_backup_filename():
        timestamp = datetime.datetime.now().strftime('%d/%b/%Y %H:%M:%S')
        return DBBACKUP_FILENAME_TEMPLATE.format(datetime=timestamp)

    if __name__ == "__main__":
        backup_filename = generate_backup_filename()


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

## Removed After Dynamic Preferences Added
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com' # Has to enable low security clients in gmail
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = 'adityaabsolin@gmail.com'
# EMAIL_HOST_PASSWORD = ''


CRONJOBS = [
    # ('*/5 * * * *', 'myapp.cron.other_scheduled_job', ['arg1', 'arg2'], {'verbose': 0}), # To call a function
]

LOG_DIR = os.path.join(BASE_DIR, '.log')
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': ".log/DEBUG_LogFile.log",
        },
        'logfile_info':{
            'level':'INFO',
            'class':'logging.FileHandler',
            'formatter': 'standard',
            'filename': ".log/INFO_LogFile.log",
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        # 'level':'DEBUG' if DEBUG else 'WARNING',
        'class':'logging.FileHandler',
        'filename': ".log/root_logfile.log",
        'maxBytes': 1024 * 1024 * 10, #Max 10MB
        'backupCount': 3,
        'formatter': 'standard',
    },
    'loggers': {
        # 'django': {
        #     'handlers':['console'],
        #     'propagate': True,
        #     'level':'WARN',
        # },
        # 'django.db.backends': {
        #     'handlers': ['console'],
        #     'level': 'DEBUG',
        #     'propagate': False,
        # },
        'Common': {
            'level':'DEBUG' if DEBUG else 'WARNING',
            'handlers': ['logfile', 'console'],
        },
        'Common': {
            'level':'INFO',
            'handlers': ['logfile_info', 'console'],
        },
        'thirdparty': {
            'level':'INFO',
            'handlers': ['logfile_info', 'console'],
        },
    }
}


IO_SERVER_URL = "http://localhost:5000"
IO_SECRET = "NV4387G0VESRRN6STZ0VC4KN8JTQA0"



FOCUS_SYNC_ON = os.getenv('FOCUS_SYNC_ON', False)
FOCUS_BASEURL = os.getenv('FOCUS_BASEURL', None)
FOCUS_COMPANY_CODE = os.getenv('FOCUS_COMPANY_CODE', None)
FOCUS_USERNAME = os.getenv('FOCUS_USERNAME', None)
FOCUS_PASSWORD = os.getenv('FOCUS_PASSWORD', None)

FOCUS_API2_BASEURL = os.getenv('FOCUS_API2_BASEURL', None)
FOCUS_API2_TOKEN = os.getenv('FOCUS_API2_TOKEN', None)


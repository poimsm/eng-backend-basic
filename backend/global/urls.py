from django.urls import re_path
from .views import *

app_name = 'global'

urlpatterns = [
    re_path(r'config\/?$', global_config),
]

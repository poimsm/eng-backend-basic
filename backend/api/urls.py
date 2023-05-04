from django.urls import re_path
from rest_framework_simplejwt.views import (
    TokenRefreshView, TokenVerifyView
)
from users.views import CustomTokenObtainPairView

from .views import *

app_name = 'api'

urlpatterns = [
    # @app public
    re_path(r'hola\/?$', hola, name='hola'),
    re_path(r'library/short-video\/?$', library_short_video),
    re_path(r'library/info-card\/?$', library_info_card),
    re_path(r'activities/pack\/?$', activity_pack),
    re_path(r'local-sentence/convert-to-favorite\/?$', local_sens_to_favorites),
    re_path(r'local-sentence/convert-to-sentence\/?$', local_sens_to_sentences),
    re_path(r'flow/screen-flow\/?$', screen_flow),

    # @app protected
    re_path(r'local-sentence/save\/?$', save_local_sens),
    re_path(r'user/sentence\/?$', user_sentences),
    re_path(r'user/stats\/?$', user_stats),
    re_path(r'user/favorites\/?$', user_favorites),
    re_path(r'activities/user/pack\/?$', user_activity_pack),
    re_path(r'library/user/short-video\/?$', user_short_video),
    re_path(r'library/user/info-card\/?$', user_info_card),

    # @authentication
    re_path(r'user/sign-up\/?$', user_sign_up),
    re_path(r'user/sign-in\/?$', user_sign_in),
    re_path(r'user/data\/?$', user_data),
    re_path(r'token/verify\/?$', TokenVerifyView.as_view()),
    re_path(r'token/refresh\/?', TokenRefreshView.as_view()),
]


# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view, renderer_classes
)
from rest_framework.renderers import JSONRenderer
from django.conf import settings


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def global_config(request):

    mobile_app_verison = request.GET.get('version', '0.0.0')

    languages = [
        {
            'lang': 'es',
            'label': 'Spanish',
            'flag': settings.SITE_DOMAIN + '/media/flags/spanish_flag.png'
        },
        {
            'lang': 'zh-Hans',
            'label': 'Chinese',
            'flag': settings.SITE_DOMAIN + '/media/flags/chinese_flag.png'
        },
        {
            'lang': 'pt',
            'label': 'Portuguese',
            'flag': settings.SITE_DOMAIN + '/media/flags/portuguese_flag.png'
        },
        {
            'lang': 'ar',
            'label': 'Arabic',
            'flag': settings.SITE_DOMAIN + '/media/flags/arabic_flag.png'
        },
        {
            'lang': 'hi',
            'label': 'Hindi',
            'flag': settings.SITE_DOMAIN + '/media/flags/hindi_flag.png'
        },
    ]

    # langues = ['es', 'zh-Hans', 'pt', 'ar', 'hi']

    data = {
        'mobile_app_verison': mobile_app_verison,
        'api_version': 'v1',
        'update_required': False,
        'languages': languages
    }

    return Response(data, status=status.HTTP_200_OK)

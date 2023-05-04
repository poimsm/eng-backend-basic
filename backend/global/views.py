
# Framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import (
    api_view, renderer_classes
)
from rest_framework.renderers import JSONRenderer


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def global_config(request):

    mobile_app_verison = request.GET.get('version', '0.0.0')

    data = {
        'mobile_app_verison': mobile_app_verison,
        'api_version': 'v1',
        'update_required': False
    }

    return Response(data, status=status.HTTP_200_OK)

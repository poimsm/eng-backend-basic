# from django.conf import settings
import logging
log = logging.getLogger('api_v1')
from users.models import User

class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('HEADERSSSSS')
        log.debug('LLEGOOOOooooo!!! <-------')
        print(request.headers)
        log.debug('LLEGOOOOooooo!!! <-------')


        print('USSERRRR')
        print(request.user)

        print(request.user.is_authenticated)

        
        if request.user.is_authenticated:
            print('emaillllll')
            print(request.user.email)

        # user = User.objects.get(id=2)
        print("custom middleware before next middleware/view !!!!!")
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

	    # Code to be executed for each response after the view is called
        # 
        print("custom middleware after response or previous middleware")
        
        return response
# from django.contrib.auth.models import User
# from django.utils.timezone import now
# from django.shortcuts import render, redirect

# class VerifiedAccountMiddleware(object):
#     def process_request(self, request):
#         print('VerifiedAccountMiddleware')
#         if request.user.is_authenticated():
#             # check if the user is verified or not
#             if not request.user.is_verified:
#                 return render(request, 'store/pages/not_verified.html', context)
#         return None
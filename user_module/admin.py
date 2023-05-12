from django.contrib import admin

from user_module.models import *

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserReview)

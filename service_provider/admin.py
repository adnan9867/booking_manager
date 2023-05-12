from django.contrib import admin

from service_provider.models import (
    LeaveTime,
    ServiceProviderTasks,
    ServiceProviderLocation,
)

admin.site.register(LeaveTime)
admin.site.register(ServiceProviderTasks)
admin.site.register(ServiceProviderLocation)

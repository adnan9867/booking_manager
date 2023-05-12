from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from booking.models import DispatchedAppointment
from cleany.base.response_mixins import BaseAPIView
from service_provider.models import (
    LeaveTime,
    ServiceProviderTasks,
    ServiceProviderLocation, ManagerTask,
)
from service_provider.serializers import (
    CleanerSerializer,
    UserListSerializer,
    ClearnerSerializerUpdate,
    ClearnerLeaveTimeSerializer,
    CleanerTasksSerializer,
    CustomerSerializer,
    CustomerSerializerUpdate,
    ServiceProviderLocationSerializer,
    ManagerTaskSerializer,
    ManagerTaskSerializerCreate,
)
from user_module.models import User, UserProfile


class CleanerViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CleanerSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["Cleaner"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Cleaner created successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Cleaner"])
    def list(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.filter(role="Cleaner").values_list(
                "user__id", flat=True
            )
            queryset = User.objects.filter(id__in=profile)
            serializer = UserListSerializer(queryset, many=True)
            return self.send_success_response(
                message="Cleaner list", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Cleaner"], request_body=ClearnerSerializerUpdate)
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            query = UserProfile.objects.filter(id=data["id"]).first()
            if not query:
                return self.send_bad_request_response(message="No cleaner found")
            serializer = ClearnerSerializerUpdate(
                query, data=data, context={"request": request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Cleaner updated successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class CustomerViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["Customer"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Cleaner created successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Customer"])
    def list(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.filter(role="Customer").values_list(
                "user__id", flat=True
            )
            queryset = User.objects.filter(id__in=profile)
            serializer = UserListSerializer(queryset, many=True)
            return self.send_success_response(
                message="Customer list", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Customer"], request_body=CustomerSerializerUpdate)
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            query = UserProfile.objects.filter(id=data["id"]).first()
            if not query:
                return self.send_bad_request_response(message="No Customer found")
            serializer = CustomerSerializerUpdate(
                query, data=data, context={"request": request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Cleaner updated successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class ClearnerLeaveTimeViewSet(ModelViewSet, BaseAPIView):
    serializer_class = ClearnerLeaveTimeSerializer
    queryset = LeaveTime.objects.all()

    @swagger_auto_schema(tags=["Cleaner"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Cleaner leave time created successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Cleaner"])
    def list(self, request, *args, **kwargs):
        try:
            user = request.GET.get("service_provider")
            queryset = LeaveTime.objects.filter(service_provider__id=user)
            serializer = ClearnerLeaveTimeSerializer(queryset, many=True)
            return self.send_success_response(
                message="Cleaner list", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Cleaner"], request_body=ClearnerSerializerUpdate)
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("id")
            obj = LeaveTime.objects.filter(id=pk).first()
            if not obj:
                return self.send_bad_request_response(message="Record not found")
            obj.delete()
            return self.send_success_response(message="Record deleted successfully")
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class ManagerTaskViewSet(ModelViewSet, BaseAPIView):
    serializer_class = ManagerTaskSerializer
    queryset = ManagerTask.objects.all()

    @swagger_auto_schema(tags=["Manager Tasks"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = ManagerTaskSerializerCreate(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Manager task created successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Manager Tasks"])
    def list(self, request, *args, **kwargs):
        try:
            queryset = ManagerTask.objects.filter()
            serializer = ManagerTaskSerializer(queryset, many=True)
            return self.send_success_response(
                message="Manager Tasks", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Manager Tasks"])
    def manager_task(self, request, *args, **kwargs):
        try:
            task = ManagerTask.objects.filter(manager=request.user)
            serializer = ManagerTaskSerializer(task, many=True)
            return self.send_success_response(
                message="Manager Tasks", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Manager Tasks"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            query = ManagerTask.objects.filter(id=data["id"]).first()
            if not query:
                return self.send_bad_request_response(message="No Manager task found")
            if query.is_completed:
                return self.send_bad_request_response(message="Task already completed")
            query.is_completed = True
            query.save()
            return self.send_success_response(message="Task completed successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Manager Tasks"])
    def update_task(self, request, *args, **kwargs):
        try:
            data = request.data
            query = ManagerTask.objects.filter(id=data["id"]).first()
            if not query:
                return self.send_bad_request_response(message="No Manager task found")
            serializer = self.serializer_class(query, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return self.send_success_response(message="Task updated successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Manager Tasks"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("id")
            obj = ManagerTask.objects.filter(id=pk).first()
            if not obj:
                return self.send_bad_request_response(message="Record not found")
            obj.delete()
            return self.send_success_response(message="Record deleted successfully")
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class ServiceProviderLocationViewSet(BaseAPIView, ModelViewSet):
    serializer_class = ServiceProviderLocationSerializer
    queryset = ServiceProviderLocation.objects.all()

    @swagger_auto_schema(tags=["Cleaner Location"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Cleaner location created successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Cleaner Location"])
    def list(self, request, *args, **kwargs):
        try:
            booking_id = request.GET.get("booking_id")
            dispatcher = DispatchedAppointment.objects.filter(
                booking__id=booking_id
            ).values_list("service_provider__id", flat=True)
            queryset = ServiceProviderLocation.objects.filter(
                booking__id=booking_id, service_provider__id__in=dispatcher
            )
            serializer = ServiceProviderLocationSerializer(queryset, many=True)
            return self.send_success_response(
                message="Cleaner Location", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


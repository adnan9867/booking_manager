from datetime import timedelta
from dateutil import parser
import stripe
from .models import Service
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from cleany.base.response_mixins import BaseAPIView
from service_provider.models import LeaveTime
from service_provider.serializers import DispatchSerializer, UserListSerializer
from .serializers import *
from .utils import CustomPagination, capture_amount, charge_booking, page_view_count, booking_filters, complete_booking, \
    cancel_booking, dashboard_filter_data, push_notifications, cleaner_booking_filter
import csv
import os
from django.core.exceptions import ObjectDoesNotExist

stripe.api_key = os.environ['STRIPE_SECRET_KEY']


class GetLatestViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User"])
    def list(self, request, *args, **kwargs):
        try:
            user = self.request.user
            if BookingOrderDetails.objects.filter(user=user).exists():
                latest_booking = BookingOrderDetails.objects.filter(user=user).latest('id')
                latest_contactinfo = latest_booking.bod_contact_info
                latest_serviceloc = latest_booking.bod_service_location

                contact_serializer = BODContactInfoSerializer(latest_contactinfo)
                service_serializer = BODServiceLocationSerializer(latest_serviceloc)
                response_data = {
                    'contactinfo': contact_serializer.data,
                    'service_location': service_serializer.data,
                }

            else:
                response_data = {
                    'contactinfo': [],
                    'service_location': [],
                }

            return self.send_success_response(
                message="Pervious Booking Data", data=response_data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class CompanyViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @swagger_auto_schema(tags=["Company"])
    def create(self, request, *args, **kwargs):
        try:
            previous_company = self.queryset.all()
            if previous_company:
                return self.send_bad_request_response(message="Company already exist")
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Company Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Company"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            company = self.queryset.filter(id=pk).first()
            if not company:
                return self.send_bad_request_response(message="Company not exist")
            serializer = self.serializer_class(company, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Company updated Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Company"])
    def list(self, request, *args, **kwargs):
        try:
            query = self.queryset.all()
            serializer = self.serializer_class(query, many=True)
            return self.send_success_response(
                message="Company data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class TaxViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer

    @swagger_auto_schema(tags=["Tax"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Tax Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Tax"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            company = self.queryset.filter(id=pk).first()
            if not company:
                return self.send_bad_request_response(message="Tax not exist")
            serializer = self.serializer_class(company, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Tax Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Tax"])
    def list(self, request, *args, **kwargs):
        try:
            query = self.queryset.all()
            serializer = self.serializer_class(query, many=True)
            return self.send_success_response(message="Tax data", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ServicesViewSet(ModelViewSet, BaseAPIView):
    # permission_classes = [IsAuthenticated]
    queryset = Service.objects.all()
    serializer_class = ServicesSerializer

    @swagger_auto_schema(tags=["Services"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = ServicesSerializerNew(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Services Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Services"], request_body=ServicesUpdateSerializer)
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            company = self.queryset.filter(id=pk).first()
            if not company:
                return self.send_bad_request_response(message="Services not exist")
            serializer = ServicesUpdateSerializer(company, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Services Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Services"])
    def list(self, request, *args, **kwargs):
        try:
            query = self.queryset.all().order_by("-id")
            serializer = self.serializer_class(query, many=True)
            return self.send_success_response(
                message="Services data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Customer Services"])
    def active_services(self, request, *args, **kwargs):
        try:
            query = self.queryset.all().filter(status="Published").order_by("-id")
            serializer = ServicesSerializerCustomer(query, many=True)
            banners = Banners.objects.all().order_by("-id")
            banner_serializer = BannerSerializer(banners, many=True)
            response = {
                "services": serializer.data,
                "banners": banner_serializer.data,
            }
            return self.send_success_response(
                message="Services data", data=response
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Services"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            service = self.queryset.filter(id=pk).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            service.delete()
            return self.send_success_response(message="Service deleted successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Services"], request_body=ServiceStatusSerializer)
    def update_status(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            service = self.queryset.filter(id=pk).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            packages = Package.objects.filter(service=service)
            extras = Extra.objects.filter(service=service)
            if not packages or not extras:
                return self.send_bad_request_response(
                    message="Service not have packages or extras"
                )
            service.status = data["status"]
            service.save()
            return self.send_success_response(
                message="Service status updated successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Services"])
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs["service_id"]
            service = self.queryset.filter(id=pk).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            serializer = self.serializer_class(service)
            return self.send_success_response(
                message="Service data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ServiceBookingViewSet(ModelViewSet, BaseAPIView):
    queryset = Service.objects.all()
    serializer_class = ServicesSerializer

    @swagger_auto_schema(tags=["Booking"])
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs["slug"]
            service = self.queryset.filter(slug=pk).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            page_view_count()
            serializer = self.serializer_class(service)
            return self.send_success_response(
                message="Service data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class PackagesViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Package.objects.all()
    serializer_class = PackageCreateSerializer

    @swagger_auto_schema(tags=["Packages"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Packages Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Packages"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            company = self.queryset.filter(id=pk).first()
            if not company:
                return self.send_bad_request_response(message="Packages not exist")
            serializer = self.serializer_class(company, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Packages Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Packages"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            package = self.queryset.filter(id=pk).first()
            if not package:
                return self.send_bad_request_response(message="Package not exist")
            package.delete()
            return self.send_success_response(message="Package deleted successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ServiceExtrasViewSet(ModelViewSet, BaseAPIView):
    queryset = Extra.objects.all()
    serializer_class = ExtrasViewSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ExtrasViewSerializer, tags=["Extras"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Extras Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Extras"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            company = self.queryset.filter(id=pk).first()
            if not company:
                return self.send_bad_request_response(message="Extra not exist")
            serializer = self.serializer_class(company, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Extra Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Extras"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            extra = self.queryset.filter(id=pk).first()
            if not extra:
                return self.send_bad_request_response(message="Extra not exist")
            extra.delete()
            return self.send_success_response(message="Extra deleted successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class PackageItemsViewSet(ModelViewSet, BaseAPIView):
    queryset = Item.objects.all()
    serializer_class = PackageItemSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Items"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Item Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    @swagger_auto_schema(tags=["Items"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            pk = data["id"]
            item = self.queryset.filter(id=pk).first()
            if not item:
                return self.send_bad_request_response(message="Item  not exist")
            serializer = self.serializer_class(item, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Item Data", data=serializer.data
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Items"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            package = self.queryset.filter(id=pk).first()
            if not package:
                return self.send_bad_request_response(message="Item not exist")
            package.delete()
            return self.send_success_response(message="Item deleted successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingViewSet(ModelViewSet, BaseAPIView):
    queryset = None
    serializer_class = BookingSerializer

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            service_id = kwargs.get("service")
            service = Service.objects.filter(id=service_id).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            data["service_id"] = service.id
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Booking created successfully",
                    data=data["contact_info"]["email"]
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking"])
    def list(self, request, *args, **kwargs):
        try:
            booking_status = request.GET.get("booking_status")
            date_filter = request.GET.get("date_filter")
            to_date = request.GET.get("to_date")
            if to_date:
                to_date = parser.parse(to_date)
            bookings = Booking.objects.filter(status__iexact=booking_status)
            bookings = booking_filters(bookings, date_filter, to_date)
            if request.GET.get("page"):
                paginator = CustomPagination()
                paginator.page_size = request.GET.get("per_page")
                paginator.page = request.GET.get("page")
                query_set = paginator.paginate_queryset(bookings, request)
                serializer = BookingSerializerList(query_set, many=True)
                if paginator.page.paginator.num_pages == int(request.GET.get("page")):
                    return paginator.get_last_page_data(serializer.data)
                else:
                    return paginator.get_paginated_response(serializer.data)
            serializer = BookingSerializerList(bookings, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking"])
    def booking_created_at(self, request, *args, **kwargs):
        try:
            bookings = Booking.objects.filter(status__in=["scheduled", "dispatched"]).order_by('-created_at')
            if request.GET.get("page"):
                paginator = CustomPagination()
                paginator.page_size = request.GET.get("per_page")
                paginator.page = request.GET.get("page")
                query_set = paginator.paginate_queryset(bookings, request)
                serializer = BookingSerializerList(query_set, many=True)
                if paginator.page.paginator.num_pages == int(request.GET.get("page")):
                    return paginator.get_last_page_data(serializer.data)
                else:
                    return paginator.get_paginated_response(serializer.data)
            serializer = BookingSerializerList(bookings, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking"])
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs["pk"]
            booking = Booking.objects.filter(id=pk).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            serializer = BookingSerializerList(booking)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class AdminBookingViewSet(ModelViewSet, BaseAPIView):
    queryset = None
    serializer_class = AdminBookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            service_id = kwargs.get("service")
            service = Service.objects.filter(id=service_id).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            data["service_id"] = service.id
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Booking created successfully"
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserBookingViewSet(ModelViewSet, BaseAPIView):
    queryset = None
    serializer_class = UserBookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            service_id = kwargs.get("service")
            service = Service.objects.filter(id=service_id).first()
            if not service:
                return self.send_bad_request_response(message="Service not exist")
            data["service_id"] = service.id
            serializer = self.serializer_class(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Booking created successfully"
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingDetailViewSet(ModelViewSet, BaseAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingDetailSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking"])
    def list(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("booking_id")
            bookings = Booking.objects.filter(id=pk).first()
            if not bookings:
                return self.send_bad_request_response(message="Booking not exist")
            serializer = BookingDetailSerializer(bookings)
            return self.send_success_response(
                message="Bookings Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class RescheduleBookingViewSet(ModelViewSet, BaseAPIView):
    queryset = Booking.objects.all()
    serializer_class = UpdateBookingSerializer

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            is_all = data.get("is_all")
            current_booking = Booking.objects.get(
                id=data["id"]
            )  # changes //appointed date
            appointment_date = data.get("time")
            # appointment_date = "2021-01-01 00:00:00"
            if is_all == "on":
                all_booking = Booking.objects.filter(
                    bod__id=current_booking.bod.id
                ).order_by("id")
                all_booking_ids = all_booking.values_list("id", flat=True)
                if current_booking.bod.frequency.type == "weekly":
                    appointment_date = datetime.datetime.strptime(
                        appointment_date, "%Y-%m-%d %H:%M:%S"
                    )
                    schedule = Schedule.objects.filter(booking__in=all_booking_ids)
                    schedule_len = len(schedule)
                    index = schedule_len
                    for obj in schedule:
                        days = 7 * (schedule_len - index)
                        obj.start_time = appointment_date + datetime.timedelta(
                            days=days
                        )
                        obj.end_time = appointment_date + timedelta(hours=2)
                        obj.booking.appointment_date_time = (
                                appointment_date + datetime.timedelta(days=days)
                        )
                        obj.booking.save()
                        obj.save()
                        index -= 1
                if current_booking.bod.frequency.type == "once":
                    appointment_date = datetime.datetime.strptime(
                        appointment_date, "%Y-%m-%d %H:%M:%S"
                    )
                    schedule = Schedule.objects.filter(booking__in=all_booking_ids)
                    for obj in schedule:
                        obj.start_time = appointment_date
                        obj.end_time = appointment_date + timedelta(hours=2)
                        obj.booking.appointment_date_time = appointment_date
                        obj.booking.save()
                        obj.save()
                if current_booking.bod.frequency.type == "biweekly":
                    appointment_date = datetime.datetime.strptime(
                        appointment_date, "%Y-%m-%d %H:%M:%S"
                    )
                    schedule = Schedule.objects.filter(booking__in=all_booking_ids)
                    schedule_len = len(schedule)
                    index = schedule_len
                    for obj in schedule:
                        days = 14 * (schedule_len - index)
                        obj.start_time = appointment_date + datetime.timedelta(
                            days=days
                        )
                        obj.end_time = appointment_date + timedelta(hours=2)
                        obj.booking.appointment_date_time = (
                                appointment_date + datetime.timedelta(days=days)
                        )
                        obj.booking.save()
                        obj.save()
                        index -= 1
                if current_booking.bod.frequency.type == "monthly":
                    appointment_date = datetime.datetime.strptime(
                        appointment_date, "%Y-%m-%d %H:%M:%S"
                    )
                    schedule = Schedule.objects.filter(booking__in=all_booking_ids)
                    date_list = list()
                    date_list.append(appointment_date)
                    for obj in schedule:
                        obj.start_time = date_list[-1]
                        obj.end_time = date_list[-1] + timedelta(hours=2)
                        obj.booking.appointment_date_time = date_list[-1]
                        obj.booking.save()
                        obj.save()
                        new_date = date_list[-1] + relativedelta(months=1)
                        date_list.append(new_date)
            else:
                appointment_date = datetime.datetime.strptime(
                    appointment_date, "%Y-%m-%d %H:%M:%S"
                )
                schedule = Schedule.objects.filter(booking=current_booking.id)
                for obj in schedule:
                    obj.start_time = appointment_date
                    obj.end_time = appointment_date + timedelta(hours=2)
                    obj.booking.appointment_date_time = appointment_date
                    obj.booking.save()
                    obj.save()
            BookingNotifications.objects.create(
                bod=current_booking.bod,
                title="Booking Rescheduled",
            )
            return self.send_success_response(
                message="Booking Rescheduled Successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingProblemsViewSet(ModelViewSet, BaseAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingProblemsSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking Problems"])
    def list(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("booking")
            bookings = BookingProblem.objects.filter(booking__id=pk).first()
            if not bookings:
                return self.send_bad_request_response(
                    message="Booking problem not exist"
                )
            serializer = BookingProblemsSerializer(bookings)
            return self.send_success_response(
                message="Bookings Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking Problems"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            booking = Booking.objects.filter(id=data["booking"]).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            data_dict = {
                "message": data["message"],
                "status": data["status"],
            }
            BookingProblem.objects.update_or_create(booking=booking, defaults=data_dict)
            return self.send_success_response(
                message="Booking Problem Added Successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingAttachmentsViewSet(ModelViewSet, BaseAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingAttachmentsSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking Attachments"])
    def list(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("booking")
            bookings = BookingAttachments.objects.filter(booking__id=pk)
            if not bookings:
                return self.send_bad_request_response(
                    message="Booking attachments not exist"
                )
            serializer = BookingAttachmentsSerializer(bookings, many=True)
            return self.send_success_response(
                message="Bookings Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking Attachments"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            booking = Booking.objects.filter(id=data["booking"]).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            BookingAttachments.objects.update_or_create(
                booking=booking,
                file=data["file"],
                share_with_customer=data["share_with_customer"],
                share_with_cleaner=data["share_with_cleaner"],
            )
            return self.send_success_response(
                message="Booking Attachment Added Successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking Attachments"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk")
            booking = BookingAttachments.objects.filter(id=pk).first()
            if not booking:
                return self.send_bad_request_response(
                    message="Booking attachment not exist"
                )
            booking.delete()
            return self.send_success_response(
                message="Booking Attachment Deleted Successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UpdateBookingService(ModelViewSet, BaseAPIView):
    queryset = Booking.objects.all()
    serializer_class = UpdateBookingItemsSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Update Booking Service"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            booking = Booking.objects.filter(id=data["booking"]).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            serializer = UpdateBookingItemsSerializer(
                booking, data=data, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                return self.send_success_response(
                    message="Booking Service Updated Successfully"
                )
            return self.send_success_response(
                message="Booking Service Updated Successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingUpdateViewSet(BaseAPIView, ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = DispatchBookingSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking Dispatch"])
    def list(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.filter().exclude(
                status__in=["cancelled", "completed"]
            )
            serializer = BookingSerializerList(booking, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking Dispatch"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            booking = Booking.objects.filter(id=data["booking"]).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            serializer = DispatchBookingSerializer(
                data=data, context={"request": request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Booking dispatched Successfully"
                )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking Dispatch"])
    def destroy(self, request, *args, **kwargs):
        try:
            pk = kwargs.get("pk")
            dispatch = DispatchedAppointment.objects.filter(id=pk).first()
            if not dispatch:
                return self.send_bad_request_response(message="Dispatch not exist")
            booking = Booking.objects.filter(id=dispatch.booking.id).first()
            booking.status = "scheduled"
            booking.save()
            dispatch.delete()
            return self.send_success_response(message="Dispatch Deleted Successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Booking Dispatch"])
    def dispatch_list(self, request, *args, **kwargs):
        try:
            dispatch = DispatchedAppointment.objects.filter().exclude(
                status="completed"
            )
            serializer = DispatchBookingSerializerNew(dispatch, many=True)
            return self.send_success_response(
                message="Dispatch Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class AdminChatViewSet(BaseAPIView, ModelViewSet):
    queryset = CustomerSupportChat.objects.all()
    serializer_class = AdminChatSerializer

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Admin Chat"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            data["user"] = request.user.id
            serializer = AdminChatSerializer(data=data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(message="Chat Added Successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Admin Chat"])
    def list(self, request, *args, **kwargs):
        try:
            chat = CustomerSupportChat.objects.filter(user__user_in_profile__role="Customer"
                                                      ).distinct('collection').values_list("collection__id",
                                                                                           flat=True)
            collection = CustomerSupportCollection.objects.filter(id__in=chat)
            serializer = CustomerSupportCollectionSerializer(collection, many=True)
            return self.send_success_response(message="Chat Data", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserChatViewSet(BaseAPIView, ModelViewSet):
    queryset = CustomerSupportChat.objects.all()
    serializer_class = UserChatSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["User Chat"])
    def list(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.filter(id=request.GET.get("booking")).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            collection = CustomerSupportCollection.objects.get_or_create(
                booking=booking
            )[0]
            serializer = UserChatSerializer(collection)
            return self.send_success_response(message="Chat Data", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingChatViewSet(BaseAPIView, ModelViewSet):
    queryset = CustomerSupportChat.objects.all()
    serializer_class = UserChatSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Cleaner Chat"])
    def list(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.filter(id=kwargs.get("pk")).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            collection = CustomerSupportCollection.objects.filter(
                booking=booking
            ).first()
            chat = CustomerSupportChat.objects.filter(
                collection=collection)
            serializer = CleanerChatSerializerNew(chat, many=True)
            return self.send_success_response(message="Chat Data", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class CleanerChatViewSet(BaseAPIView, ModelViewSet):
    queryset = CustomerSupportChat.objects.all()
    serializer_class = AdminCleanerChatSerializerNew
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Cleaner Chat"])
    def list(self, request, *args, **kwargs):
        try:
            booking = DispatchedAppointment.objects.filter(service_provider=request.user
                                                           ).values_list('booking__id', flat=True)
            collection = CustomerSupportCollection.objects.filter(booking__in=booking).values_list('id', flat=True)
            chat = CustomerSupportChat.objects.filter(
                collection__in=collection).order_by('id')
            serializer = CleanerChatSerializerNew(chat, many=True)
            return self.send_success_response(message="Chat Data", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class AdminChatDetailViewSet(BaseAPIView, ModelViewSet):
    queryset = CustomerSupportChat.objects.all()
    serializer_class = None
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Admin Chat Detail"])
    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(id=request.GET.get("user")).first()
            if not user or not user.access_dashboard:
                return self.send_bad_request_response(message="User not exist or not have access")
            booking = Booking.objects.filter(id=request.GET.get("booking")).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not exist")
            collection = CustomerSupportCollection.objects.get_or_create(booking=booking)[0]
            serializer = UserChatSerializer(collection)
            return self.send_success_response(message="Chat Data", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingDashboardViewSet(BaseAPIView, ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializerList
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Booking Dashboard"])
    def list(self, request, *args, **kwargs):
        try:
            start_date = request.GET.get("start_date")
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            data_list = []
            for i in range(0, 7):
                booking = Booking.objects.filter(
                    status="scheduled",
                    appointment_date_time__date__lte=start_date,
                    appointment_date_time__date__gte=start_date,
                )
                serializer = BookingSerializerList(booking, many=True)
                data_dict = {
                    "name": "start_date",
                    "value": start_date,
                    "data": serializer.data,
                }
                data_list.append(data_dict)
                start_date = start_date + datetime.timedelta(days=1)
            return self.send_success_response(message="Booking Data", data=data_list)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ChargeViewSet(BaseAPIView, ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = ChargeNowSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Charge"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            payment_mode = data.get("payment_mode")
            if not payment_mode in ['cash', 'card']:
                return self.send_bad_request_response(message="Payment Mode not valid")
            booking = Booking.objects.filter(id=data["booking_id"]).first()
            if not booking:
                return self.send_bad_request_response(message="Booking Not Found")
            if booking.is_cancelled:
                return self.send_bad_request_response(message="Booking is cancelled")
            sale = Sale.objects.filter(booking=booking).first()
            if sale.status == "completed":
                return self.send_bad_request_response(
                    message="Booking dues are completed"
                )
            payment_sale = PaymentSale.objects.filter(sale=sale).first()
            if payment_sale:
                if payment_sale.is_first:
                    capture_amount(payment_sale)
                    sale.status = "completed"
                    payment_sale.is_captured = True
                    payment_sale.save()
                    sale.save()
                    return self.send_success_response(
                        message="Booking Charged successfully"
                    )
            if sale.amount < float(data["amount"]):
                return self.send_bad_request_response(
                    message="Charge amount should be less than total amount"
                )
            paid_amount = sale.paid + float(data["amount"])
            if paid_amount > sale.amount:
                return self.send_bad_request_response(
                    message="Charge amount should be less than remaining amount"
                )
            if paid_amount == 'cash':
                sale.paid += float(data["amount"])
                sale.status = "partial"
                if sale.amount <= sale.paid:
                    sale.status = "completed"
                sale.save()
                PaymentSale.objects.create(
                    sale=sale, amount=float(data["amount"]), mode='cash'
                )
            charge = charge_booking(booking.bod, int(data["amount"]))
            sale.paid += float(data["amount"])
            sale.status = "partial"
            if sale.amount == sale.paid:
                sale.status = "completed"
            sale.save()
            PaymentSale.objects.create(
                sale=sale, amount=float(data["amount"]), capture=charge
            )
            return self.send_success_response(message="Booking charged successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class DashboardAPIsViewSet(BaseAPIView, ModelViewSet):
    queryset = None
    serializer_class = BookingSerializer

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Dashboard Analytics"])
    def list(self, request, *args, **kwargs):
        try:
            customer_filter = dashboard_filter_data(request.GET.get("customer_filter") or None)
            booking_filter = dashboard_filter_data(request.GET.get("booking_filter") or None)
            amount_filter = dashboard_filter_data(request.GET.get("amount_filter") or None)
            hours_filter = dashboard_filter_data(request.GET.get("hours_filter") or None)
            page_view_filter = dashboard_filter_data(request.GET.get("page_view_filter") or None)
            service_filter = dashboard_filter_data(request.GET.get("service_filter") or None)
            cleaner_filter = dashboard_filter_data(request.GET.get("cleaner_filter") or None)
            data_list = []
            service_count = Service.objects.filter()
            if service_filter[0]:
                service_count = service_count.filter(created_at__gte=service_filter[1],
                                                     created_at__lte=service_filter[0])
            data_dict = {
                "name": "Services Count",
                "value": service_count.count(),
            }
            data_list.append(data_dict)
            customer_count = UserProfile.objects.filter(role="Customer")
            if customer_filter[0]:
                customer_count = customer_count.filter(created_at__gte=customer_filter[1],
                                                       created_at__lte=customer_filter[0])
            data_dict = {
                "name": "Customer Count",
                "value": customer_count.count(),
            }
            data_list.append(data_dict)
            cleaner_count = UserProfile.objects.filter(role="Cleaner")
            if customer_filter[0]:
                cleaner_count = cleaner_count.filter(created_at__gte=cleaner_filter[1],
                                                     created_at__lte=cleaner_filter[0])
            data_dict = {
                "name": "Cleaner Count",
                "value": cleaner_count.count(),
            }
            data_list.append(data_dict)
            page_views = PageViewsCount.objects.filter()
            if page_view_filter[0]:
                page_views = page_views.filter(created_at__gte=page_view_filter[1],
                                               created_at__lte=page_view_filter[0])
            data_dict = {
                "name": "Page Views",
                "value": page_views.count(),
            }
            data_list.append(data_dict)
            booking_count = Booking.objects.filter()
            if booking_filter[0]:
                booking_count = booking_count.filter(created_at__gte=booking_filter[1],
                                                     created_at__lte=booking_filter[0])
            data_dict = {
                "name": "Booking Count",
                "value": booking_count.count(),
            }
            data_list.append(data_dict)
            total_amount = PaymentSale.objects.filter()
            if amount_filter[0]:
                total_amount = total_amount.filter(created_at__gte=amount_filter[1],
                                                   created_at__lte=amount_filter[0])
            data_dict = {
                "name": "Total Gross",
                "value": total_amount.filter().aggregate(Sum("amount"))["amount__sum"],
            }
            data_list.append(data_dict)
            total_hours = BookingOrderDetails.objects.filter()
            if hours_filter[0]:
                total_hours = total_hours.filter(created_at__gte=hours_filter[1],
                                                 created_at__lte=hours_filter[0])
            data_dict = {"name": "Clocked Hours",
                         "value": total_hours.filter().aggregate(Sum("total_hours"))["total_hours__sum"]}
            data_list.append(data_dict)
            data_dict = {"name": "Hot Leads", "value": 4}
            data_list.append(data_dict)
            return self.send_success_response(message="Dashboard Data", data=data_list)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingNotificationViewSet(BaseAPIView, ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingNotificationSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Notifications"])
    def list(self, request, *args, **kwargs):
        try:
            notifications = BookingNotifications.objects.filter(mark_as_read=False,
                                                                title__in=['New Booking Confirmation',
                                                                           "Booking Rescheduled"]).order_by('-id')
            serializer = BookingNotificationSerializer(notifications, many=True)
            return self.send_success_response(
                message="Notification Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class MobileNotificationViewSet(BaseAPIView, ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingNotificationSerializerNew
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Notifications"])
    def list(self, request, *args, **kwargs):
        try:
            notifications = BookingNotifications.objects.filter(mark_as_read=False,
                                                                title__in=['Booking Dispatched'],
                                                                user=request.user).order_by('-id')
            serializer = BookingNotificationSerializer(notifications, many=True)
            return self.send_success_response(
                message="Notification Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BookingReportsViewSet(BaseAPIView, ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializerList

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Reports"])
    def list(self, request, *args, **kwargs):
        try:
            date_filter = request.GET.get("date_filter", None)
            to_date = request.GET.get("to_date", None)
            if to_date:
                to_date = parser.parse(to_date)
            booking_status = request.GET.get("booking_status")
            sale = (
                Sale.objects.filter()
                .exclude(status="completed")
                .values_list("booking__id", flat=True)
            )
            bookings = Booking.objects.filter(
                status__iexact=booking_status, id__in=sale
            ).order_by("-id")
            if date_filter:
                bookings = booking_filters(bookings, date_filter, to_date)
            if request.GET.get("page"):
                paginator = CustomPagination()
                paginator.page_size = request.GET.get("per_page")
                paginator.page = request.GET.get("page")
                query_set = paginator.paginate_queryset(bookings, request)
                serializer = BookingSerializerList(query_set, many=True)
                if paginator.page.paginator.num_pages == int(request.GET.get("page")):
                    return paginator.get_last_page_data(serializer.data)
                else:
                    return paginator.get_paginated_response(serializer.data)
            serializer = BookingSerializerList(bookings, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserCurrentBookingView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializerList

    @swagger_auto_schema(tags=["User Side"])
    def list(self, request, *args, **kwargs):
        try:
            booking = (
                Booking.objects.filter(
                    bod__user=request.user, status__in=["scheduled", "dispatched"]
                )
                .order_by("id")
                .first()
            )
            serializer = self.serializer_class(booking)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserBookingView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializerList

    @swagger_auto_schema(tags=["User Side"])
    def list(self, request, *args, **kwargs):
        try:
            booking_status = request.GET.get("booking_status")
            date_filter = request.GET.get("date_filter")
            to_date = request.GET.get("to_date")
            if to_date:
                to_date = parser.parse(to_date)
            bookings = Booking.objects.filter(bod__user=request.user, status__iexact=booking_status)
            bookings = booking_filters(bookings, date_filter, to_date)
            if request.GET.get("page"):
                paginator = CustomPagination()
                paginator.page_size = request.GET.get("per_page")
                paginator.page = request.GET.get("page")
                query_set = paginator.paginate_queryset(bookings, request)
                serializer = BookingSerializerList(query_set, many=True)
                if paginator.page.paginator.num_pages == int(request.GET.get("page")):
                    return paginator.get_last_page_data(serializer.data)
                else:
                    return paginator.get_paginated_response(serializer.data)
            else:
                bookings = Booking.objects.filter(bod__user=request.user)

            serializer = BookingSerializerList(bookings, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserAdminBookingView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializerList

    @swagger_auto_schema(tags=["Booking"])
    def list(self, request, *args, **kwargs):
        try:
            user = request.GET.get("user")
            bookings = Booking.objects.filter(
                bod__user__id=user, status__in=["scheduled", "dispatched"]
            )
            if request.GET.get("page"):
                paginator = CustomPagination()
                paginator.page_size = request.GET.get("per_page")
                paginator.page = request.GET.get("page")
                query_set = paginator.paginate_queryset(bookings, request)
                serializer = BookingSerializerList(query_set, many=True)
                if paginator.page.paginator.num_pages == int(request.GET.get("page")):
                    return paginator.get_last_page_data(serializer.data)
                else:
                    return paginator.get_paginated_response(serializer.data)
            serializer = BookingSerializerList(bookings, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class CleanerBookingView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializerList

    @swagger_auto_schema(tags=["Cleaner Side"])
    def list(self, request, *args, **kwargs):
        try:
            appointments = DispatchedAppointment.objects.filter(
                service_provider=request.user
            ).values_list("booking__id", flat=True)
            bookings = Booking.objects.filter(
                status__in=["scheduled", "dispatched"], id__in=appointments
            )
            bookings = cleaner_booking_filter(bookings)
            if request.GET.get("page"):
                paginator = CustomPagination()
                paginator.page_size = request.GET.get("per_page")
                paginator.page = request.GET.get("page")
                query_set = paginator.paginate_queryset(bookings, request)
                serializer = BookingSerializerListCleaner(query_set, many=True)
                if paginator.page.paginator.num_pages == int(request.GET.get("page")):
                    return paginator.get_last_page_data(serializer.data)
                else:
                    return paginator.get_paginated_response(serializer.data)
            serializer = BookingSerializerListCleaner(bookings, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class PayrollViewSet(BaseAPIView, ModelViewSet):
    queryset = Payroll.objects.all()
    serializer_class = PayrollSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Payroll"])
    def list(self, request, *args, **kwargs):
        try:
            start_date = request.GET.get("start_date" or None)
            end_date = request.GET.get("end_date" or None)
            service_provider = request.GET.get("service_provider" or None)
            payroll = Payroll.objects.filter()
            if start_date and end_date:
                start_date = parser.parse(start_date)
                end_date = parser.parse(end_date)
                payroll = payroll.filter(
                    created_at__range=[start_date, end_date]
                )
            if service_provider:
                payroll = payroll.filter(sp__id=service_provider)
            serializer = self.serializer_class(payroll, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class InvoiceViewSet(BaseAPIView, ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Invoice"])
    def list(self, request, *args, **kwargs):
        try:
            payroll = Invoice.objects.filter()
            serializer = self.serializer_class(payroll, many=True)
            return self.send_success_response(
                message="Booking Data", data=serializer.data
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserCardDetails(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = BodSerializer

    @swagger_auto_schema(tags=["User Card Details"])
    def list(self, request, *args, **kwargs):
        try:
            token = UserStripe.objects.filter(user=request.user.email).last()
            if not token:
                return self.send_bad_request_response(message="Stripe token not found.")
            customer_ = stripe.Customer.retrieve(token.stripe_customer)
            customer = stripe.Customer.retrieve_source(
                token.stripe_customer, customer_.default_source
            )
            data = {
                "card": customer["last4"],
                "exp_month": customer["exp_month"],
                "exp_year": customer["exp_year"],
                "brand": customer["brand"],
            }
            return self.send_success_response(data=data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ChargeTipViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = ChargeTipSerializer

    @swagger_auto_schema(tags=["Charge Tip"])
    def create(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.filter(id=request.data.get("booking_id")).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not found.")
            token = UserStripe.objects.filter(user=booking.bod.user.email).last()
            if not token:
                return self.send_bad_request_response(message="Stripe token not found.")
            charge = stripe.Charge.create(
                amount=request.data.get("amount") * 100,
                currency="usd",
                customer=token.stripe_customer,
                description="Tip",
            )
            ChargeTip.objects.create(
                booking=booking,
                tip_amount=request.data.get("amount"),
                charge_id=charge.id,
            )
            return self.send_success_response(message="Success! Tip charged.")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class CancelBookingView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CancelBookingSerializer

    @swagger_auto_schema(tags=["Booking"])
    def create(self, request, *args, **kwargs):
        try:
            booking = Booking.objects.filter(id=request.data.get("booking_id")).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not found.")
            if booking.status == "completed":
                return self.send_bad_request_response(message="Booking already completed.")
            if booking.is_cancelled:
                return self.send_bad_request_response(message="Booking already cancelled.")
            booking.is_cancelled = True
            booking.status = "cancelled"
            booking.save()
            if request.data.get("cancel_all", None) and request.data.get("cancel_all", None) == "True":
                Booking.objects.filter(bod=booking.bod).update(is_cancelled=True, status="cancelled")
            cancel_booking(data=request.data, booking=booking)
            return self.send_success_response(message="Success! Booking cancelled.")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class EmailTypesViewSet(BaseAPIView, ModelViewSet):
    queryset = EmailTypes.objects.all()
    serializer_class = EmailTypesSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Email Types"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_success_response(message="Success! Email Type Created.")
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Email Types"])
    def list(self, request, *args, **kwargs):
        try:
            subject = request.GET.get('email_type') or None
            email_types = EmailTypes.objects.all().order_by('-id')
            if subject:
                email_types = email_types.filter(email_type__iexact=subject)
            serializer = self.serializer_class(email_types, many=True)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Email Types"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            email_type = EmailTypes.objects.filter(id=data.get('id')).first()
            if not email_type:
                return self.send_bad_request_response(message="Email type not found.")
            serializer = self.serializer_class(email_type, data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(message="Success! Email type updated.")
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class MarkBookingCompleteView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = MarkBookingCompleteSerializer

    @swagger_auto_schema(tags=["Booking"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            booking = Booking.objects.filter(id=request.data.get("booking_id")).first()
            if not booking:
                return self.send_bad_request_response(message="Booking not found.")
            if booking.status == "complete":
                return self.send_bad_request_response(message="Booking already completed.")
            if booking.is_cancelled:
                return self.send_bad_request_response(message="Booking already cancelled.")
            booking.status = "complete"
            booking.save()
            complete_booking(data, booking.bod)
            return self.send_success_response(message="Success! Booking completed.")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class EmailLogsViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = EmailLogsSerializer

    @swagger_auto_schema(tags=["Email Logs"])
    def list(self, request, *args, **kwargs):
        try:
            user = request.GET.get("user_id")
            email_logs = EmailLogs.objects.filter(customer__id=user).order_by('-id')
            serializer = self.serializer_class(email_logs, many=True)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class RetrieveCustomer(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializerCustomerNew

    @swagger_auto_schema(tags=["Customer"])
    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.GET.get("user_id")
            customer = User.objects.filter(id=user).first()
            serializer = self.serializer_class(customer)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ManagerViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializerCustomerNew

    @swagger_auto_schema(tags=["Manager"])
    def list(self, request, *args, **kwargs):
        try:
            manager_ids = UserProfile.objects.filter(role="Manager").values_list('user__id', flat=True)
            managers = User.objects.filter(id__in=manager_ids).order_by('-id')
            serializer = self.serializer_class(managers, many=True)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class PaymentSaleView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = PaymentSaleSerializer

    @swagger_auto_schema(tags=["Payment Sale"])
    def list(self, request, *args, **kwargs):
        try:
            payments = PaymentSale.objects.all().order_by('-id')
            serializer = self.serializer_class(payments, many=True)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class PayrollCsvViewSet(BaseAPIView, ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = None

    @swagger_auto_schema(tags=["Payroll"])
    def list(self, request, *args, **kwargs):
        try:
            start_date = request.GET.get("start_date" or None)
            end_date = request.GET.get("end_date" or None)
            service_provider = request.GET.get("service_provider" or None)
            payroll = Payroll.objects.filter()
            if start_date and end_date:
                start_date = parser.parse(start_date)
                end_date = parser.parse(end_date)
                payroll = payroll.filter(
                    created_at__range=[start_date, end_date]
                )
            if service_provider:
                payroll = payroll.filter(sp__id=service_provider)
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
            )
            write = csv.writer(response)
            serializer = PayrollSerializer(payroll, many=True)
            write.writerow(['service provider', 'hourly wage', 'hours worked', 'amount', 'paid', 'total tips'])
            for i in range(len(serializer.data)):
                write.writerow(
                    [serializer.data[i]['sp']['user_profile']['first_name'] + " " +
                     serializer.data[i]['sp']['user_profile']["last_name"],
                     serializer.data[i]['hourly_wage'],
                     serializer.data[i]['total_hours'],
                     serializer.data[i]['total_amount'],
                     serializer.data[i]['paid_amount'],
                     serializer.data[i]['tip_amount']
                     ])
            total_amount = payroll.aggregate(Sum('total_amount'))['total_amount__sum']
            total_paid = payroll.aggregate(Sum('paid_amount'))['paid_amount__sum']
            write.writerow(['total_amount', total_amount])
            write.writerow(['total_paid', total_paid])
            return response
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class CustomerCsvViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = None

    @swagger_auto_schema(tags=["Customer CSV"])
    def list(self, request, *args, **kwargs):
        try:
            user_ids = UserProfile.objects.filter(role="Customer").values_list('user__id', flat=True)
            user = User.objects.filter(id__in=user_ids)
            response = HttpResponse(
                content_type='text/csv',
                headers={'Content-Disposition': 'attachment; filename="somefilename.csv"'},
            )
            write = csv.writer(response)
            serializer = UserListSerializer(user, many=True)
            write.writerow(['email', 'role', 'first_name',
                            'last_name', 'language', 'address',
                            'city', 'state', 'zip_code', ])
            for i in range(len(serializer.data)):
                write.writerow(
                    [serializer.data[i]['email'] + " " +
                     serializer.data[i]['user_profile']["role"],
                     serializer.data[i]['user_profile']["first_name"],
                     serializer.data[i]['user_profile']["last_name"],
                     serializer.data[i]['user_profile']["language"],
                     serializer.data[i]['user_profile']["address"],
                     serializer.data[i]['user_profile']['city'],
                     serializer.data[i]['user_profile']['state'],
                     serializer.data[i]['user_profile']['zip_code'],
                     ])
            return response
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class PayrollLedgerViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PayrollLedger.objects.all()
    serializer_class = PayrollLedgerSerializer

    @swagger_auto_schema(tags=["Payroll Ledger"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = PayrollLedgerSerializerCreate(data=data)
            if serializer.is_valid():
                total_amount = Payroll.objects.filter(id__in=data['payroll']). \
                    aggregate(Sum('total_amount'))['total_amount__sum']
                previous_paid = PayrollLedger.objects.filter(payroll__id__in=data['payroll']). \
                    aggregate(Sum('total_amount'))['total_amount__sum']
                if previous_paid:
                    if previous_paid + data['total_amount'] > total_amount:
                        return self.send_bad_request_response(message="Amount is greater than total payroll amount")
                else:
                    if data['total_amount'] > total_amount:
                        return self.send_bad_request_response(message="Amount is greater than total payroll amount")
                serializer.save()
                return self.send_success_response(data=serializer.data,
                                                  message="Payroll Ledger Created Successfully")
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["Payroll Ledger"])
    def list(self, request, *args, **kwargs):
        try:
            payroll = request.GET.get("payroll" or None)
            ledger = PayrollLedger.objects.select_related('service_provider').filter()
            if payroll:
                ledger = ledger.filter(payroll__id=payroll)
            serializer = self.serializer_class(ledger, many=True)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class BannerViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Banners.objects.all()
    serializer_class = BannerSerializer

    @swagger_auto_schema(tags=["Banner"])
    def list(self, request, *args, **kwargs):
        try:

            banner = Banners.objects.filter()
            serializer = self.serializer_class(banner, many=True)
            return self.send_success_response(data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

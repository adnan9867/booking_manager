from django.db import transaction
from django.db.models import Sum
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from booking.models import *
from booking.utils import (
    calculate_booking_bills,
    schedule_booking,
    stripe_payment,
    booking_notifications,
    stripe_payment_user, booking_confirmation,
)
from user_module.models import UserProfile


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"


class TaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tax
        fields = "__all__"


class ServicesSerializer(serializers.ModelSerializer):
    service_total_booking = serializers.SerializerMethodField("get_total_booking")
    banner = serializers.SerializerMethodField('get_banner')
    packages = serializers.SerializerMethodField("get_packages")
    extras = serializers.SerializerMethodField("get_extras")
    tax = serializers.SerializerMethodField("get_tax", read_only=True)

    class Meta:
        model = Service
        fields = "__all__"

    def get_total_booking(self, obj):
        return BookingItemDetails.objects.filter(item__package__service=obj).count()

    def get_banner(self, obj):
        banner = Banners.objects.filter(service=obj)
        return BannerSerializer(banner, many=True).data

    def get_packages(self, obj):
        packages = Package.objects.filter(service=obj.id)
        return PackagesSerializer(packages, many=True).data

    def get_extras(self, obj):
        extras = Extra.objects.filter(service=obj.id)
        return ExtrasSerializer(extras, many=True).data

    def get_tax(self, obj):
        tax = Tax.objects.filter(service=obj.id)
        return TaxSerializer(tax, many=True).data


class ServicesSerializerCustomer(serializers.ModelSerializer):
    service_total_booking = serializers.SerializerMethodField("get_total_booking")

    class Meta:
        model = Service
        fields = "__all__"

    def get_total_booking(self, obj):
        return BookingItemDetails.objects.filter(item__package__service=obj).count()


class ServicesSerializerNew(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ServicesUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        exclude = ["company", "status", "tax"]


class ServiceStatusSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = Service
        fields = ["id", "status"]


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        exclude = ["package"]


class ExtrasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = "__all__"


class PackageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = "__all__"


class PackageItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class PackagesSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, write_only=True)
    item = serializers.SerializerMethodField("get_items")

    class Meta:
        model = Package
        fields = "__all__"

    def create(self, validated_data):
        items = validated_data.pop("items")
        package = Package.objects.create(**validated_data)
        for item in items:
            Item.objects.create(package=package, **item)
        return package

    def get_items(self, obj):
        items = Item.objects.filter(package=obj)
        return ItemSerializer(items, many=True).data


class PackageListSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField("get_items")

    class Meta:
        model = Package
        fields = "__all__"

    def get_items(self, obj):
        items = Item.objects.filter(package=obj)
        return ItemSerializer(items, many=True).data


class ExtrasViewSerializer(serializers.ModelSerializer):
    quantity = serializers.SerializerMethodField("get_quantity")

    class Meta:
        model = Extra
        fields = "__all__"

    def get_quantity(self, obj):
        try:
            bod = self.context["bod"]
            bod = BODExtraDetails.objects.filter(bod=bod, extra=obj).first()
            return bod.quantity
        except Exception as e:
            return None


class BODContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BODContactInfo
        fields = "__all__"


class BODServiceLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BODServiceLocation
        fields = "__all__"


class ExtraSchemaSerializer(serializers.Serializer):  # noqa
    extra_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(required=True)


class ItemBookingSerializer(serializers.Serializer):  # noqa
    item_id = serializers.IntegerField(required=True)
    package = serializers.IntegerField(required=True)


class ItemSerializerNew(serializers.ModelSerializer):
    item_id = serializers.IntegerField(required=True)

    class Meta:
        model = Item
        fields = ["item_id"]


class ExtrasSerializerNew(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=True)
    extra_id = serializers.IntegerField(required=True)

    class Meta:
        model = Extra
        fields = ["extra_id", "quantity"]


class UpdateBookingItemsSerializer(serializers.ModelSerializer):
    booking = serializers.IntegerField(required=True)
    service_id = serializers.IntegerField(required=True)
    item = ItemSerializerNew(many=True, write_only=True)
    extra = ExtrasSerializerNew(many=True, write_only=True)

    class Meta:
        model = Booking
        fields = ["id", "booking", "service_id", "item", "extra"]

    def update(self, instance, validated_data):
        with transaction.atomic():
            sale = Sale.objects.get(booking=instance)
            payment = PaymentSale.objects.get(sale=sale)
            if payment.capture:
                raise serializers.ValidationError(
                    _("Payment is already captured. You can't update booking.")
                )
            request = self.context["request"]
            data = request.data
            BookingItemDetails.objects.filter(booking=instance).delete()
            BookingExtraDetails.objects.filter(booking=instance).delete()
            calculate_booking_bills(
                order_details=instance.bod,
                extras=data.get("extra"),
                items=data.get("item"),
                service_id=data.get("service_id"),
            )
            return instance


class BookingSerializer(serializers.ModelSerializer):
    contact_info = BODContactInfoSerializer(read_only=True)
    service_location = BODServiceLocationSerializer(read_only=True)
    extras = ExtraSchemaSerializer(many=True, write_only=True)
    items = ItemBookingSerializer(many=True, write_only=True)
    booking_type = serializers.CharField(required=True)
    service_id = serializers.CharField(required=True)
    start_time = serializers.TimeField(required=True)
    start_date = serializers.DateField(required=True)
    latitude = serializers.CharField(required=False)
    longitude = serializers.CharField(required=False)
    additional_info = serializers.CharField(required=False)
    card_token = serializers.CharField(required=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "contact_info",
            "service_location",
            "extras",
            "items",
            "booking_type",
            "service_id",
            "start_time",
            "start_date",
            "additional_info",
            "card_token",
            "longitude",
            "latitude"
        ]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context["request"]
            data = request.data
            user = User.objects.filter(email=data["contact_info"]["email"]).first()
            if not user:
                user = User.objects.get_or_create(
                    email=data["contact_info"]["email"], access_dashboard=False
                )[0]
                UserProfile.objects.create(
                    user=user,
                    first_name=data["contact_info"]["first_name"],
                    last_name=data["contact_info"]["last_name"],
                    phone_number=data["contact_info"]["phone"],
                    role="Customer",
                )
            service = Service.objects.filter(id=data["service_id"]).first()
            if not service:
                raise serializers.ValidationError(_("Service not found"))
            contact_info = BODContactInfo.objects.create(
                first_name=data["contact_info"]["first_name"],
                last_name=data["contact_info"]["last_name"],
                email=data["contact_info"]["email"],
                phone=data["contact_info"]["phone"],
                how_to_enter_on_premise=data["contact_info"]["how_to_enter_on_premise"],
            )
            frequency = Frequency.objects.create(
                service=service,
                type=data["booking_type"],
                title="test_title_frequency",
                start_date=data["start_date"],
            )
            location_data = data["service_location"]
            service_location = BODServiceLocation.objects.create(
                street_address=location_data["street_address"],
                apt_suite=location_data["apt_suite"],
                city=location_data["city"],
                state="nyc",
                zip_code=location_data["zip_code"],
                let_long=location_data["let_long"],
            )
            order_details = BookingOrderDetails.objects.create(
                bod_contact_info=contact_info,
                frequency=frequency,
                bod_service_location=service_location,
                user=user,
                colour=service.id,
                start_time=data["start_time"],
                additional_info=data["additional_info"],
            )
            BookingNotifications.objects.create(
                bod=order_details,
                title="New Booking Confirmation",
            )
            calculate_booking_bills(
                order_details,
                items=data["items"],
                extras=data["extras"],
                service_id=service.id,
            )
            booking = schedule_booking(order_details.id, data)
            stripe_payment(
                order_detail=order_details,
                email=data["contact_info"]["email"],
                amount=order_details.total_amount,
                payment=booking,
                card_token=data["card_token"],
            )
            booking_notifications(order_details)
            booking_confirmation(name=user.first_name,
                                 email=user.email,
                                 booking_date=booking.sale.booking.appointment_date_time
                                 )
            # try:
            #     twilio_message = MessageClient()
            #     twilio_message.send_message(
            #         body="Your booking has been confirmed",
            #         to=user.phone_number,
            #     )
            # except Exception as e:
            #     print(e)
            return booking


class AdminBookingSerializer(serializers.ModelSerializer):
    contact_info = BODContactInfoSerializer(read_only=True)
    service_location = BODServiceLocationSerializer(read_only=True)
    extras = ExtraSchemaSerializer(many=True, write_only=True)
    items = ItemBookingSerializer(many=True, write_only=True)
    booking_type = serializers.CharField(required=True)
    service_id = serializers.CharField(required=True)
    start_time = serializers.TimeField(required=True)
    start_date = serializers.DateField(required=True)
    additional_info = serializers.CharField(required=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "contact_info",
            "service_location",
            "extras",
            "items",
            "booking_type",
            "service_id",
            "start_time",
            "start_date",
            "additional_info",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context["request"]
            data = request.data
            user = User.objects.filter(email=data["contact_info"]["email"]).first()
            if not user:
                user = User.objects.get_or_create(
                    email=data["contact_info"]["email"], access_dashboard=False
                )[0]
                UserProfile.objects.create(
                    user=user,
                    first_name=data["contact_info"]["first_name"],
                    last_name=data["contact_info"]["last_name"],
                    phone_number=data["contact_info"]["phone"],
                    role="customer",
                )
            service = Service.objects.filter(id=data["service_id"]).first()
            if not service:
                raise serializers.ValidationError(_("Service not found"))
            contact_info = BODContactInfo.objects.create(
                first_name=data["contact_info"]["first_name"],
                last_name=data["contact_info"]["last_name"],
                email=data["contact_info"]["email"],
                phone=data["contact_info"]["phone"],
                how_to_enter_on_premise=data["contact_info"]["how_to_enter_on_premise"],
            )
            frequency = Frequency.objects.create(
                service=service,
                type=data["booking_type"],
                title="test_title_frequency",
                start_date=data["start_date"],
            )
            location_data = data["service_location"]
            service_location = BODServiceLocation.objects.create(
                street_address=location_data["street_address"],
                apt_suite=location_data["apt_suite"],
                city=location_data["city"],
                state="nyc",
                zip_code=location_data["zip_code"],
                let_long=location_data["let_long"],
            )
            order_details = BookingOrderDetails.objects.create(
                bod_contact_info=contact_info,
                frequency=frequency,
                bod_service_location=service_location,
                user=user,
                colour=service.id,
                start_time=data["start_time"],
                additional_info=data["additional_info"],
            )
            calculate_booking_bills(
                order_details,
                items=data["items"],
                extras=data["extras"],
                service_id=service.id,


            )
            booking = schedule_booking(order_details.id)
            stripe_payment_user(
                order_detail=order_details,
                email=data["contact_info"]["email"],
                amount=order_details.total_amount,
                payment=booking,
                user=user,
            )
            booking_notifications(order_details)
            booking_confirmation(name=user.first_name,
                                 email=user.email,
                                 booking_date=booking.sale.booking.appointment_date_time
                                 )
            # try:
            #     twilio_message = MessageClient()
            #     twilio_message.send_message(
            #         body="Your booking has been confirmed",
            #         to=user.phone_number,
            #     )
            # except Exception as e:
            #     print(e)
            return booking


class UserBookingSerializer(serializers.ModelSerializer):
    contact_info = BODContactInfoSerializer(read_only=True)
    service_location = BODServiceLocationSerializer(read_only=True)
    extras = ExtraSchemaSerializer(many=True, write_only=True)
    items = ItemBookingSerializer(many=True, write_only=True)
    booking_type = serializers.CharField(required=True)
    latitude = serializers.CharField(required=True)
    longitude = serializers.CharField(required=True)
    service_id = serializers.CharField(required=True)
    start_time = serializers.TimeField(required=True)
    start_date = serializers.DateField(required=True)
    additional_info = serializers.CharField(required=True)
    card_token = serializers.CharField(allow_blank = True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "contact_info",
            "service_location",
            "extras",
            "items",
            "booking_type",
            "service_id",
            "start_time",
            "start_date",
            "additional_info",
            "latitude",
            "longitude",
            "card_token"
        ]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context["request"]
            data = request.data
            user = request.user
            if not user:
                user = User.objects.get_or_create(
                    email=data["contact_info"]["email"], access_dashboard=False
                )[0]
                UserProfile.objects.create(
                    user=user,
                    first_name=data["contact_info"]["first_name"],
                    last_name=data["contact_info"]["last_name"],
                    phone_number=data["contact_info"]["phone"],
                    role="customer",
                )
            service = Service.objects.filter(id=data["service_id"]).first()
            if not service:
                raise serializers.ValidationError(_("Service not found"))
            contact_info = BODContactInfo.objects.create(
                first_name=data["contact_info"]["first_name"],
                last_name=data["contact_info"]["last_name"],
                email=data["contact_info"]["email"],
                phone=data["contact_info"]["phone"],
                how_to_enter_on_premise=data["contact_info"]["how_to_enter_on_premise"],
            )
            frequency = Frequency.objects.create(
                service=service,
                type=data["booking_type"],
                title="test_title_frequency",
                start_date=data["start_date"],
            )
            location_data = data["service_location"]
            service_location = BODServiceLocation.objects.create(
                street_address=location_data["street_address"],
                apt_suite=location_data["apt_suite"],
                city=location_data["city"],
                state="nyc",
                zip_code=location_data["zip_code"],
                let_long=location_data["let_long"],
            )
            order_details = BookingOrderDetails.objects.create(
                bod_contact_info=contact_info,
                frequency=frequency,
                bod_service_location=service_location,
                user=user,
                colour=service.id,
                start_time=data["start_time"],
                additional_info=data["additional_info"],
            )
            BookingNotifications.objects.create(
                bod=order_details,
                title="New Booking Confirmation",
            )
            calculate_booking_bills(
                order_details,
                items=data["items"],
                extras=data["extras"],
                service_id=service.id,
            )
            booking = schedule_booking(order_details.id,data)
            # if data.get("card_token") !="":

            stripe_payment_user(
                order_detail=order_details,
                email=data["contact_info"]["email"],
                amount=order_details.total_amount,
                payment=booking,
                card_token = data["card_token"],
                user=user,
                )
            booking_confirmation(name=user.first_name,
                                 email=user.email,
                                 booking_date=booking.sale.booking.appointment_date_time
                                 )
            booking_notifications(order_details)
            # try:
            #     twilio_message = MessageClient()
            #     twilio_message.send_message(
            #         body="Your booking has been confirmed",
            #         to=user.phone_number,
            #     )
            # except Exception as e:
            #     print(e)

            return booking


class ServiceSerializer(serializers.ModelSerializer):
    tax_amount = serializers.SerializerMethodField('get_tax_amount')

    class Meta:
        model = Service
        fields = "__all__"

    def get_tax_amount(self, obj):
        try:
            return obj.tax.tax_rate
        except Exception as e:
            return None


class FrequencySerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = Frequency
        fields = "__all__"


class BookingSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"


class BodSerializer(serializers.ModelSerializer):
    frequency = FrequencySerializer(read_only=True)
    bod_contact_info = BODContactInfoSerializer(read_only=True)
    bod_service_location = BODServiceLocationSerializer(read_only=True)

    class Meta:
        model = BookingOrderDetails
        fields = "__all__"


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class BookingSerializerList(serializers.ModelSerializer):
    payment_status = serializers.SerializerMethodField("get_payments")
    dispatch_id = serializers.SerializerMethodField("get_dispatch_id")
    service_provider = serializers.SerializerMethodField("get_service_provider")
    schedule = serializers.SerializerMethodField("get_schedule")
    bod = BodSerializer()
    outstanding = serializers.SerializerMethodField("get_outstanding_amount")
    collection = serializers.SerializerMethodField('get_collection')
    dispatch = serializers.SerializerMethodField('get_dispatch')

    class Meta:
        model = Booking
        fields = "__all__"

    def get_payments(self, obj):
        try:
            sale = Sale.objects.get(booking=obj)
            return sale.status
        except Exception as e:
            return None

    def get_service_provider(self, obj):
        try:
            dispatcher = DispatchedAppointment.objects.get(booking=obj)
            return dispatcher.service_provider.id
        except:
            return None

    def get_dispatch_id(self, obj):
        try:
            dispatcher = DispatchedAppointment.objects.get(booking=obj)
            return dispatcher.id
        except:
            return None

    def get_schedule(self, obj):
        try:
            schedule = Schedule.objects.get(booking=obj)
            return ScheduleSerializer(schedule).data
        except:
            return None

    def get_outstanding_amount(self, obj):
        try:
            sale = Sale.objects.filter(booking=obj).first()
            if sale:
                payment_sale = PaymentSale.objects.filter(sale=sale)
                captured_amount = payment_sale.filter(is_captured=True).aggregate(
                    Sum("amount")
                )["amount__sum"]
                is_first = False
                if captured_amount:
                    is_first = captured_amount == payment_sale.first().is_first
                if not captured_amount:
                    captured_amount = 0
                data_dict = {
                    "total_amount": sale.amount,
                    "status": sale.status,
                    "paid_amount": captured_amount,
                    "is_first": is_first,
                }
                return data_dict
        except Exception as e:
            return None

    def get_collection(self, obj):
        try:
            collection = CustomerSupportCollection.objects.get(booking=obj)
            return collection.id
        except Exception as e:
            return None

    def get_dispatch(self, obj):
        try:
            dispatch = DispatchedAppointment.objects.get(booking=obj)
            return DispatchBookingSerializer(dispatch).data
        except Exception as e:
            return None


class ExtraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Extra
        fields = "__all__"


class BookingExtraDetailsSerializer(serializers.ModelSerializer):
    extra = ExtraSerializer(read_only=True)

    class Meta:
        model = BookingExtraDetails
        fields = "__all__"


class ItemSerializerNewCleaner(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class BookingPackageDetailsSerializer(serializers.ModelSerializer):
    item = ItemSerializerNewCleaner(read_only=True)

    class Meta:
        model = BookingItemDetails
        fields = "__all__"


class BookingSerializerListCleaner(serializers.ModelSerializer):
    packages = serializers.SerializerMethodField("get_packages")
    extras = serializers.SerializerMethodField("get_extras")
    dispatch_id = serializers.SerializerMethodField("get_dispatch")
    service_provider = serializers.SerializerMethodField("get_service_provider")
    schedule = serializers.SerializerMethodField("get_schedule")
    bod = BodSerializer()
    outstanding = serializers.SerializerMethodField("get_outstanding_amount")
    collection = serializers.SerializerMethodField('get_collection')
    dispatch = serializers.SerializerMethodField('get_dispatch')

    class Meta:
        model = Booking
        fields = "__all__"

    def get_extras(self, obj):
        try:
            extras = BookingExtraDetails.objects.filter(booking=obj)
            return BookingExtraDetailsSerializer(extras, many=True).data
        except Exception as e:
            return None

    def get_packages(self, obj):
        try:
            packages = BookingItemDetails.objects.filter(booking=obj)
            return BookingPackageDetailsSerializer(packages, many=True).data
        except Exception as e:
            return None

    def get_service_provider(self, obj):
        try:
            dispatcher = DispatchedAppointment.objects.get(booking=obj)
            return dispatcher.service_provider.id
        except:
            return None

    def get_dispatch(self, obj):
        try:
            dispatcher = DispatchedAppointment.objects.get(booking=obj)
            return dispatcher.id
        except:
            return None

    def get_schedule(self, obj):
        try:
            schedule = Schedule.objects.get(booking=obj)
            return ScheduleSerializer(schedule).data
        except:
            return None

    def get_outstanding_amount(self, obj):
        try:
            sale = Sale.objects.filter(booking=obj).first()
            if sale:
                payment_sale = PaymentSale.objects.filter(sale=sale)
                captured_amount = payment_sale.filter(is_captured=True).aggregate(
                    Sum("amount")
                )["amount__sum"]
                is_first = False
                if captured_amount:
                    is_first = captured_amount == payment_sale.first().is_first
                if not captured_amount:
                    captured_amount = 0
                data_dict = {
                    "total_amount": sale.amount,
                    "status": sale.status,
                    "paid_amount": captured_amount,
                    "is_first": is_first,
                }
                return data_dict
        except Exception as e:
            return None

    def get_collection(self, obj):
        try:
            collection = CustomerSupportCollection.objects.get(booking=obj)
            return collection.id
        except Exception as e:
            return None

    def get_dispatch(self, obj):
        try:
            dispatch = DispatchedAppointment.objects.get(booking=obj)
            return DispatchBookingSerializer(dispatch).data
        except Exception as e:
            return None


class BookingSerializerListNew(serializers.ModelSerializer):
    bod = BodSerializer()

    class Meta:
        model = Booking
        fields = "__all__"


class BookingDetailSerializer(serializers.ModelSerializer):
    dispatch = serializers.SerializerMethodField("get_dispatch")
    dashboard = serializers.SerializerMethodField("get_dashboard")
    outstanding = serializers.SerializerMethodField("get_outstanding")
    is_capture = serializers.SerializerMethodField("get_is_capture")
    bod = BodSerializer()
    service = serializers.SerializerMethodField("get_service")
    discount = serializers.SerializerMethodField("get_discount")
    items = serializers.SerializerMethodField("get_items")
    extras = serializers.SerializerMethodField("get_extras")
    bookings = serializers.SerializerMethodField("get_bookings")

    class Meta:
        model = Booking
        fields = "__all__"

    def get_dashboard(self, obj):
        try:
            return obj.bod.user.access_dashboard
        except Exception as e:
            return None

    def get_dispatch(self, obj):
        try:
            dispatcher = DispatchedAppointment.objects.filter(booking=obj)
            return DispatchBookingSerializer(dispatcher, many=True).data
        except Exception as e:
            return None

    def get_outstanding(self, obj):
        try:
            sale = Sale.objects.filter(booking=obj).first()
            if sale:
                payment_sale = PaymentSale.objects.filter(sale=sale)
                captured_amount = payment_sale.filter(is_captured=True).aggregate(
                    Sum("amount")
                )["amount__sum"]
                is_first = False
                if captured_amount:
                    is_first = captured_amount == payment_sale.first().is_first
                data_dict = {
                    "total_amount": sale.amount,
                    "status": sale.status,
                    "paid_amount": captured_amount,
                    "is_first": is_first,
                }
                return data_dict
        except Exception as e:
            return None

    def get_items(self, obj):
        booking_item = BODItemDetails.objects.filter(bod=obj.bod).values_list(
            "item__id", flat=True
        )
        items = Item.objects.filter(id__in=booking_item)
        return ItemSerializer(items, many=True).data

    def get_is_capture(self, obj):
        try:
            sale = Sale.objects.get(booking=obj)
            payment = PaymentSale.objects.get(sale=sale)
            if payment.capture:
                return True
            return False
        except:
            return False

    def get_service(self, obj):
        try:
            return ServiceSerializer(obj.bod.frequency.service).data
        except:
            return None

    def get_extras(self, obj):
        extras = BODExtraDetails.objects.filter(bod=obj.bod).values_list(
            "extra__id", flat=True
        )
        extras = Extra.objects.filter(id__in=extras)
        return ExtrasViewSerializer(extras, many=True, context={"bod": obj.bod}).data

    def get_discount(self, obj):
        try:
            items = BODItemDetails.objects.filter(bod=obj.bod)
            total_discount = 0
            for obj in items:
                discount_percentage = obj.item.discount_percent
                discount = (obj.item.price * discount_percentage) / 100
                total_discount += discount
            return total_discount
        except:
            return None

    def get_bookings(self, obj):
        try:
            bookings = Booking.objects.filter(bod=obj.bod).exclude(id=obj.id)
            return BookingSimpleSerializer(bookings, many=True).data
        except:
            return None


class BookingProblemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingProblem
        fields = "__all__"


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class BookingAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingAttachments
        fields = "__all__"


class UpdateBookingSerializer(serializers.ModelSerializer):
    time = serializers.DateField(required=True)
    is_all = serializers.BooleanField(required=True)

    class Meta:
        model = Booking
        fields = ["id", "time", "is_all"]


class ServiceProviderSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField("get_user_profile")

    class Meta:
        model = User
        fields = ["id", "email", "user_profile"]

    def get_user_profile(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj).first()
            return UserProfileSerializer(profile).data
        except:
            return None


class DispatchBookingSerializer(serializers.ModelSerializer):
    service_provider = serializers.SerializerMethodField("get_service_provider")

    class Meta:
        model = DispatchedAppointment
        fields = "__all__"

    def create(self, validated_data):
        data = self.context["request"].data
        service_provider = User.objects.get(id=data["service_provider"])
        booking = Booking.objects.get(id=data["booking"])
        dispatch = DispatchedAppointment.objects.create(
            booking=booking,
            service_provider=service_provider,
        )
        booking.status = "dispatched"
        booking.save()
        return dispatch

    def get_service_provider(self, obj):
        try:
            return ServiceProviderSerializer(obj.service_provider).data
        except:
            return None


class DispatchBookingSerializerNew(serializers.ModelSerializer):
    booking = BookingSerializerList()

    class Meta:
        model = DispatchedAppointment
        fields = "__all__"


class AdminChatSerializer(serializers.ModelSerializer):
    collection = serializers.IntegerField(read_only=True)
    parent_id = serializers.IntegerField(read_only=True)
    user = serializers.IntegerField(read_only=True)

    class Meta:
        model = CustomerSupportChat
        fields = "__all__"

    def create(self, validated_data):
        request = self.context["request"]
        data = request.data
        profile = UserProfile.objects.filter(user=request.user).first()
        user = User.objects.filter(id=data["user"]).first()
        if profile.role not in ["Admin", "Manager", "Cleaner"]:
            collection = CustomerSupportCollection.objects.filter(
                id=data["collection"]
            ).first()
            if not collection:
                raise serializers.ValidationError("Collection not found")
            user = request.user
        elif profile.role == "Cleaner":
            collection = CustomerSupportCollection.objects.get(
                id=data["collection"]
            )
            user = request.user
        else:
            if not user or not user.access_dashboard:
                raise serializers.ValidationError(
                    "User is not allowed to access dashboard"
                )
            if "collection" in data and data["collection"] != "":
                collection = CustomerSupportCollection.objects.get(
                    id=data["collection"]
                )
                user = User.objects.filter(id=request.user.id).first()
            else:
                collection = CustomerSupportCollection.objects.filter(
                    id=data["collection"]
                ).first()
                if not collection:
                    raise serializers.ValidationError("Collection not found")
                user = request.user
        data["collection"] = collection
        chat = CustomerSupportChat.objects.create(
            collection=data["collection"],
            message=data["message"],
            user=user,
        )
        return chat


class UserProfileSerializerNew(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileSerializerCleaner(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'role']


class UserProfileSerializerCustomer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileSerializerBooking(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField("get_user_profile")

    class Meta:
        model = User
        fields = ["id", "email", "user_profile"]

    def get_user_profile(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj).first()

            return UserProfileSerializerCleaner(profile).data
        except:
            return None


class UserProfileSerializerCustomerNew(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField("get_user_profile")

    class Meta:
        model = User
        fields = ["id", "email", "user_profile"]

    def get_user_profile(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj).first()

            return UserProfileSerializerCustomer(profile).data
        except:
            return None


class AdminChatSerializerNew(serializers.ModelSerializer):
    user = UserProfileSerializerBooking()

    class Meta:
        model = CustomerSupportChat
        fields = "__all__"

    def get_user(self, obj):
        try:
            return UserProfileSerializerNew(obj.user).data
        except:
            return None


class AdminCleanerChatSerializerNew(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField('get_user_id')
    user_email = serializers.SerializerMethodField('get_user_email')
    user_role = serializers.SerializerMethodField('get_user_role')
    user_first_name = serializers.SerializerMethodField('get_user_first_name')
    user_last_name = serializers.SerializerMethodField('get_user_last_name')

    class Meta:
        model = CustomerSupportChat
        fields = "__all__"

    def get_user_id(self, obj):
        try:
            return obj.user.id
        except:
            return None

    def get_user_email(self, obj):
        try:
            return obj.user.email
        except:
            return None

    def get_user_role(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj.user).first()
            return profile.role
        except:
            return None

    def get_user_first_name(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj.user).first()
            return profile.first_name
        except:
            return None

    def get_user_last_name(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj.user).first()
            return profile.last_name
        except:
            return None


class CleanerChatSerializerNew(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField("get_user")
    user_first_name = serializers.SerializerMethodField("get_user_first_name")
    user_last_name = serializers.SerializerMethodField("get_user_last_name")
    user_role = serializers.SerializerMethodField("get_user_role")

    class Meta:
        model = CustomerSupportChat
        fields = "__all__"

    def get_user(self, obj):
        try:
            return obj.user.id
        except:
            return None

    def get_user_first_name(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj.user).first()
            return profile.first_name
        except:
            return None

    def get_user_last_name(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj.user).first()
            return profile.last_name
        except:
            return None

    def get_user_role(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj.user).first()
            return profile.role
        except:
            return None


class CustomerSupportCollectionSerializer(serializers.ModelSerializer):
    chats = serializers.SerializerMethodField("get_chats")
    user = serializers.SerializerMethodField("get_user")

    class Meta:
        model = CustomerSupportCollection
        fields = "__all__"

    def get_chats(self, obj):
        try:
            chats = CustomerSupportChat.objects.filter(collection=obj)
            return AdminChatSerializerNew(chats, many=True).data
        except:
            return None

    def get_user(self, obj):
        try:
            user = CustomerSupportChat.objects.filter(collection=obj,
                                                      user__user_in_profile__role="Customer").first()
            return UserProfileSerializerBooking(user.user).data
        except Exception as e:
            return None


class ChargeNowSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)
    payment_mode = serializers.CharField(write_only=True)

    class Meta:
        model = Booking
        fields = ["booking_id", "amount", 'payment_mode']


class BookingNotificationSerializer(serializers.ModelSerializer):
    booking_id = serializers.SerializerMethodField("get_booking_id")
    user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = BookingNotifications
        fields = "__all__"

    def get_booking_id(self, obj):
        try:
            booking = Booking.objects.filter(bod=obj.bod).first()
            return booking.id
        except:
            return None

    def get_user(self, obj):
        try:
            return UserProfileSerializerBooking(obj.bod.user).data
        except Exception as e:
            return None


class BookingNotificationSerializerNew(serializers.ModelSerializer):
    user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = BookingNotifications
        fields = "__all__"

    def get_user(self, obj):
        try:
            return UserProfileSerializerBooking(obj.bod.user).data
        except Exception as e:
            return None


class UserChatSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField("get_chat")

    class Meta:
        model = CustomerSupportCollection
        fields = "__all__"

    def get_chat(self, obj):
        try:
            chats = CustomerSupportChat.objects.filter(collection=obj).order_by('id')
            return AdminCleanerChatSerializerNew(chats, many=True).data
        except:
            return None


class CleanerChatSerializer(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField("get_chat")

    class Meta:
        model = CustomerSupportCollection
        fields = "__all__"

    def get_chat(self, obj):
        try:
            chats = CustomerSupportChat.objects.filter(collection=obj)
            return AdminChatSerializerNew(chats, many=True).data
        except:
            return None


class UserChatSerializerCleaner(serializers.ModelSerializer):
    chat = serializers.SerializerMethodField("get_chat")

    class Meta:
        model = CustomerSupportCollection
        fields = "__all__"

    def get_chat(self, obj):
        try:
            chats = CustomerSupportChat.objects.filter(collection=obj)
            return CleanerChatSerializerNew(chats, many=True).data
        except:
            return None


class PayrollSerializer(serializers.ModelSerializer):
    sp = UserProfileSerializerBooking()

    class Meta:
        model = Payroll
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    sp = UserProfileSerializerBooking()

    class Meta:
        model = Invoice
        fields = "__all__"


class ChargeTipSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(write_only=True)
    amount = serializers.FloatField(write_only=True)

    class Meta:
        model = ChargeTip
        fields = ['booking_id', 'amount']


class CancelBookingSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = ['booking_id']


class EmailTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTypes
        fields = "__all__"


class MarkBookingCompleteSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField(write_only=True)


class EmailLogsSerializer(serializers.ModelSerializer):
    customer = UserProfileSerializerBooking()

    class Meta:
        model = EmailLogs
        fields = "__all__"


class EmailTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTypes
        fields = "__all__"


class PaymentSaleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_user")

    class Meta:
        model = PaymentSale
        fields = "__all__"

    def get_user(self, obj):
        try:
            return UserProfileSerializerBooking(obj.sale.booking.bod.user).data
        except:
            return None


class PayrollLedgerSerializer(serializers.ModelSerializer):
    service_provider = UserProfileSerializerBooking(read_only=True)
    payroll = PayrollSerializer(many=True)

    class Meta:
        model = PayrollLedger
        fields = "__all__"


class PayrollLedgerSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = PayrollLedger
        fields = "__all__"


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banners
        fields = "__all__"

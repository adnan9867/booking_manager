from pyfcm import FCMNotification
from dateutil.relativedelta import relativedelta
from django.core.mail import EmailMessage
from django.template.loader import get_template
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django import template

from booking.models import *
from django.utils import timezone as datetime, timezone
import stripe

from cleany import settings

stripe.api_key = "sk_test_51LuzvBImI0pxinz8a54b3xfox3caY1xrR1sk\
                         r5rmmwNDFeJ32tuPbKp4wPOxynTP9xMcQ5GqeCiNysxI2HEzMbOh00ejP1f3IM"


def calculate_booking_bills(
        order_details: BookingOrderDetails, extras: list, items: list, service_id: int
):
    total_hours = 0
    total_amount = 0
    service = Service.objects.filter(id=service_id).first()
    tax = service.tax.tax_rate
    for extra in extras:
        extras_bill = 0
        extra_obj = Extra.objects.filter(id=extra["extra_id"]).first()
        extras_bill += extra_obj.price * extra["quantity"]
        total_hours += extra_obj.time_hrs * extra["quantity"]
        total_amount += extras_bill
        BODExtraDetails.objects.create(
            extra=extra_obj,
            bod=order_details,
            price=extras_bill,
            quantity=extra["quantity"],
        )
    for obj in items:
        package_bill = 0
        item = Item.objects.filter(id=obj["item_id"]).first()
        package_bill += item.price
        discount = (package_bill * item.discount_percent / 100)
        package_bill = float(package_bill) - float(discount)
        total_hours += item.time_hrs
        BODItemDetails.objects.create(item=item, bod=order_details, price=package_bill)
        total_amount = float(total_amount) + package_bill
    tax_amount = (total_amount * tax) / 100
    order_details.total_hours = total_hours
    order_details.total_amount = total_amount + tax_amount
    order_details.save()
    return True


def schedule_booking(order_detail: int, data):
    instance = BookingOrderDetails.objects.get(id=order_detail)
    days = 0
    count = 0
    s = 0
    payment = None
    if instance.frequency.type == "weekly":
        days = 24
    if instance.frequency.type == "biweekly":
        days = 12
    if instance.frequency.type == "monthly":
        days = 6
    if instance.frequency.type == "daily":
        days = 1

    appointment_date_time = (
            str(instance.frequency.start_date) + " " + str(instance.start_time)
    )
    appointment_date_time = datetime.datetime.strptime(
        appointment_date_time, "%Y-%m-%d %H:%M"
    )
    for i in range(0, days):
        new_booking_service_location = ServiceLocation(
            street_address=instance.bod_service_location.street_address,
            apt_suite=instance.bod_service_location.apt_suite,
            city=instance.bod_service_location.city,
            state=instance.bod_service_location.state,
            zip_code=instance.bod_service_location.zip_code,
        )

        new_booking = Booking(
            type=instance.type,
            start_time=instance.start_time,
            total_hours=instance.total_hours,
            appointment_date_time=appointment_date_time,
            latest_reschedule=instance.latest_reschedule,
            latest_cancel=instance.latest_cancel,
            additional_info=instance.additional_info,
            bod=instance,  # FK
            service_location=new_booking_service_location,  # FK
            status="scheduled",
            total_amount=instance.total_amount,
            latitude=data["latitude"],
            longitude=data["longitude"],
        )
        new_booking_service_location.save()

        new_booking.save()
        if s == 0:
            sale = Sale.objects.create(
                booking=new_booking,
                amount=instance.total_amount,
                paid=instance.total_amount,
                status="pending",
            )
            sale.save()
            payment = PaymentSale(
                sale=sale, amount=instance.total_amount, is_first=True
            )
            payment.save()

        else:
            sale = Sale(
                booking=new_booking, amount=instance.total_amount, status="pending"
            )
            sale.save()
        s = 1
        count += 1

        if instance.frequency.type == "weekly":
            appointment_date_time = appointment_date_time + datetime.timedelta(days=7)
        if instance.frequency.type == "biweekly":
            appointment_date_time = appointment_date_time + datetime.timedelta(days=14)
        if instance.frequency.type == "monthly":
            appointment_date_time = appointment_date_time + relativedelta(months=+1)
    for booking in instance.booking_set.all().order_by(
            "id"
    ):  # creating packs detail for all booking instance
        for bod_item in instance.boditemdetails_set.all():
            new_booking_item_detail = BookingItemDetails(
                item=bod_item.item, booking=booking, price=bod_item.price
            )
            new_booking_item_detail.save()

            for bod_extra in instance.bodextradetails_set.all():
                new_booking_extra_detail = BookingExtraDetails(
                    extra=bod_extra.extra,
                    booking=booking,
                    price=bod_extra.price,
                    quantity=bod_extra.quantity,
                )
                new_booking_extra_detail.save()
        new_schedule = Schedule(
            booking=booking,
            start_time=booking.appointment_date_time,
            colour=instance.colour,
            end_time=booking.appointment_date_time
                     + timezone.timedelta(hours=instance.total_hours)
            # change this to calculated hour.
        )
        new_schedule.save()
        if (
                instance.user
        ):  # if no user exist and the order is anonymous then write code to handle this:
            new_schedule.user = instance.user  # cleaner will be added when dispatched.
        new_schedule.save()

    instance.status = "scheduled"
    instance.save()
    return payment


def stripe_payment(
        card_token,
        email: str,
        amount: int,
        order_detail: BookingOrderDetails,
        payment: PaymentSale,
):
    try:
        user = User.objects.filter(email=email).first()
        if user:
            email = user.email
        customer = stripe.Customer.create(
            source=card_token,
            email=email,
            description="Customer for " + email,
        )
        charge = stripe.Charge.create(
            customer=customer.id,
            amount=int(amount) * 100,
            currency="usd",
            description="Charge for " + email,
            capture="false",
        )
        UserStripe.objects.create(
            user=user,
            email=order_detail.bod_contact_info.email,
            stripe_customer=customer.id,
            bod=order_detail.id,
        )
        payment.capture = charge.id
        payment.is_captured = False
        payment.save()
        return True
    except Exception as e:
        raise Exception(e)


def stripe_payment_user(
        email: str,
        amount: int,
        order_detail: BookingOrderDetails,
        card_token: str,
        payment: PaymentSale,
        user: User,
):
    try:
        if card_token:
            customer = stripe.Customer.create(
                source=card_token,
                email=email,
                description="Customer for " + email,
            )
            UserStripe.objects.create(
                user=user,
                email=order_detail.bod_contact_info.email,
                stripe_customer=customer.id,
                bod=order_detail.id,
            )

            charge = stripe.Charge.create(
                customer = customer.id,
                amount = int(amount) * 100,
                currency = "usd",
                description = "Charge for " + email, )
            payment.capture = charge.id
            payment.sale.status = "completed"
            payment.sale.save()
            payment.paid = payment.amount
            payment.is_captured = True
            payment.save()
            return True
        else:
         token = UserStripe.objects.filter(user=user.email).first()
         charge = stripe.Charge.create(
            customer=token.stripe_customer,
            amount=int(amount) * 100,
            currency="usd",
            description="Charge for " + email,)
        payment.capture = charge.id
        payment.sale.status = "completed"
        payment.sale.save()
        payment.paid = payment.amount
        payment.is_captured = True
        payment.save()
        return True
    except Exception as e:
        raise Exception(e)


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        try:
            previous_page = self.page.previous_page_number()
        except:
            previous_page = 0

        return Response(
            {
                "next_page": self.page.next_page_number(),
                "prev_page": previous_page,
                "total_count": self.page.paginator.count,
                "current_page": self.page.next_page_number() - 1,
                "total_page": self.page.paginator.num_pages,
                "success": True,
                "data": data,
                "last_page": False,
            }
        )

    def get_last_page_data(self, data):
        try:
            previous_page = self.page.previous_page_number()
        except:
            previous_page = 0

        return Response(
            {
                "next_page": self.page.paginator.num_pages,
                "prev_page": previous_page,
                "total_count": self.page.paginator.count,
                "current_page": self.page.paginator.num_pages,
                "total_page": self.page.paginator.num_pages,
                "success": True,
                "data": data,
                "last_page": True,
            }
        )


def capture_amount(payment_sale: PaymentSale):
    stripe.Charge.capture(payment_sale.capture)  # noqa


def charge_booking(order_detail: BookingOrderDetails, amount: int):
    stripe_customer = UserStripe.objects.filter(bod=order_detail.id).first()
    if not stripe_customer:
        raise Exception("Customer not found")

    charge = stripe.Charge.create(
        customer=stripe_customer.stripe_customer,
        amount=amount * 100,
        currency="usd",
        description="Charge for ",
    )
    return charge.id


def page_view_count():
    try:
        PageViewsCount.objects.create()
    except:
        pass


def create_profile(role: str, user: User):
    UserProfile.objects.create(user=user, role=role)


def booking_notifications(instance: BookingOrderDetails):
    try:
        notif = BookingNotifications(
            bod=instance,
            title="New Booking has been created",
        )
        notif.save()
    except Exception as e:
        print(e)


def email_logs(user: User, title: str):
    try:
        email_log = EmailLogs(user=user, title=title)
        email_log.save()
    except Exception as e:
        print(e)


def booking_filters(bookings, date_filter, to_date=None):
    start_date = datetime.datetime.now().date()
    end_date = None
    if date_filter == "t_week":
        end_date = start_date + datetime.timedelta(days=7)
    elif date_filter == "t_month":
        end_date = start_date + datetime.timedelta(days=30)
    elif date_filter == "t_year":
        end_date = start_date + datetime.timedelta(days=365)
    elif date_filter == 't_quarter':
        end_date = start_date + datetime.timedelta(days=90)
    elif date_filter == 'today':
        end_date = start_date + datetime.timedelta(days=1)
    elif date_filter == 'yesterday':
        end_date = start_date - datetime.timedelta(days=1)
    elif date_filter == 'tomorrow':
        end_date = start_date + datetime.timedelta(days=2)
    elif date_filter == 'l_week':
        end_date = start_date - datetime.timedelta(days=7)
    elif date_filter == 'l_month':
        end_date = start_date - datetime.timedelta(days=30)
    elif date_filter == 'l_year':
        end_date = start_date - datetime.timedelta(days=365)
    elif date_filter == 'l_quarter':
        end_date = start_date - datetime.timedelta(days=90)
    elif date_filter in ['t_week_to_date', 't_month_to_date', 't_year_to_date', 't_quarter_to_date']:
        end_date = to_date
    bookings = bookings.filter(appointment_date_time__range=[start_date, end_date]).order_by('appointment_date_time')
    return bookings


def cleaner_booking_filter(bookings):
    start_date = datetime.datetime.now().date()
    end_date = start_date + datetime.timedelta(days=30)
    bookings = bookings.filter(appointment_date_time__range=[start_date, end_date]).order_by('appointment_date_time')
    return bookings


def get_this_month():
    today = datetime.datetime.now()
    return today.month


def booking_confirmation(name, booking_date, email):
    """
    Send email to user
    """
    rtx = {"name": name, "booking_date": booking_date}

    message = get_template("booking_confirmation.html").render(rtx)
    email = EmailMessage(
        subject="Booking Confirmation",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


def send_email_customer(name, status, email):
    """
    Send email to user
    """
    rtx = {"name": name, "status": status}

    message = get_template("notify_customer.html").render(rtx)
    email = EmailMessage(
        subject="Booking Completion",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


def send_email_customer_feedback(name, status, email):
    """
    Send email to user
    """
    rtx = {"name": name, "status": status}

    message = get_template("booking_feedback.html").render(rtx)
    email = EmailMessage(
        subject="Booking Feedback",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


def send_email_customer_tip(name, status, email):
    """
    Send email to user
    """
    rtx = {"name": name, "status": status}

    message = get_template("booking_tipe.html").render(rtx)
    email = EmailMessage(
        subject="Booking Tip",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


def complete_booking(data: dict, bod: BookingOrderDetails):
    notify_customer = data['notify_customer']
    feed_back = data['feed_back']
    request_tip = data['request_tip']
    profile = UserProfile.objects.filter(user=bod.user).first()
    if profile:
        if notify_customer == 'yes':
            send_email_customer(name=profile.first_name, status="completed", email=bod.user.email)
        if feed_back == 'yes':
            send_email_customer_feedback(name=bod.user.first_name, status="completed", email=bod.user.email)
        if request_tip == 'yes':
            send_email_customer_tip(name=bod.user.first_name, status="completed", email=bod.user.email)


def cancel_booking(data: dict, booking: Booking):
    notify_customer = data['notify_customer']
    notify_service_provider = data['notify_service_provider']
    profile = UserProfile.objects.filter(user=booking.bod.user).first()
    if profile:
        if notify_customer == 'yes':
            send_email_customer(name=profile.first_name, status="cancelled", email=booking.bod.user.email)
        if notify_service_provider == 'yes':
            service_provider = DispatchedAppointment.objects.filter(booking=booking)
            for sp in service_provider:
                profile = UserProfile.objects.filter(user=sp.service_provider).first()
                if profile:
                    send_email_customer(name=profile.first_name, status="cancelled", email=sp.service_provider.email)


def booking_confirmation_test():
    """
    Send email to user
    """
    rtx = {"userfirstname": "Ad", "bill": 77, "nationality": "Nigeria", "booking_date": "2021-05-05"}
    er = EmailTypes.objects.filter().first()
    # message = get_template(er.body).render(rtx)
    html_template_str = er.body
    t = template.Template(html_template_str)
    c = template.Context({"userfirstname": "Ad", "bill": 77, "nationality": "Nigeria", "booking_date": "2021-05-05"})
    html = t.render(c)

    email = EmailMessage(
        subject="Booking Confirmation",
        body=html,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["adnanshraf.9011@gmail.com"],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


def dashboard_filter_data(filters):
    import pytz
    tz = pytz.timezone("UTC")
    start_date = None
    end_date = None
    if filters == "7_days":
        start_date = datetime.datetime.now(tz=tz)
        end_date = start_date - datetime.timedelta(days=7)
    if filters == "30_days":
        start_date = datetime.datetime.now()
        end_date = start_date - datetime.timedelta(days=30)
    if filters == "90_days":
        start_date = datetime.datetime.now()
        end_date = start_date - datetime.timedelta(days=90)
    return start_date, end_date


def push_notifications(user: User, message_title: str, message_body: str, data):
    push_service = FCMNotification(
        api_key="AAAA8BtKFRE:APA91bEqSxCmdIepghMb4HKcwVTnzvj6DHVIAYoxXieWmooy_QnALyZb9NotK-8QO5WLKwgTIoLr4nYQqQPYpvthv6mPfp7xzuvwpe-byFACRoIXp-vooT6NG8-0HIIV2n4zBYPiyvdR")
    push_service.notify_single_device(registration_id=user.device_token,
                                      message_title=message_title,
                                      message_body=message_body,
                                      data_message=data
                                      )

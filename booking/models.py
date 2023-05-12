import datetime

from django.db import models
from django.http import Http404

from user_module.models import User, UserProfile


class Company(models.Model):
    """Company/Zone profile. e.g.: Cleany NYC, Cleany Miami. Currently only one Company per installation"""

    title = models.CharField(max_length=48)
    logo = models.ImageField(null=True, blank=True, upload_to="company_logo")
    street_address = models.CharField(max_length=128)
    city = models.CharField(max_length=48)
    zip_code = models.IntegerField()
    state = models.CharField(max_length=48)
    phone = models.CharField(max_length=24)
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    company_timezone = models.CharField(max_length=48, null=True, blank=True)
    website = models.CharField(max_length=48, null=True, blank=True)
    facebook = models.CharField(max_length=128, null=True, blank=True)
    linkedin = models.CharField(max_length=128, null=True, blank=True)
    twitter = models.CharField(max_length=128, null=True, blank=True)
    instagram = models.CharField(max_length=128, null=True, blank=True)
    weather = models.CharField(max_length=128, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tax(models.Model):
    """
    Company global tax class.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, default="State Tax")
    tax_code = models.CharField(max_length=64, unique=True)  # e.g.: California
    tax_code_short = models.CharField(max_length=24)  # e.g.: CA
    tax_code_number = models.CharField(max_length=128, null=True, blank=True)
    tax_rate = models.PositiveIntegerField()  # e.g.: 5. cannot go more than 100
    additional_info = models.CharField(
        max_length=256, null=True, blank=True
    )  # everyone sees this.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if 0 >= self.tax_rate > 100:
            raise Http404("Failed! Tax rate should 1 to 100.")
        return super(Tax, self).save(*args, **kwargs)


class Service(models.Model):
    """Company Services (like podiumo service page). Every service will have many extras, packages under them."""  # noqa

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)  # for internal uses for only the admin
    slug = models.SlugField(
        max_length=128, help_text="URI slug for this service page", unique=True
    )  # URI slug for this service page.
    title = models.CharField(max_length=128)  # public
    description = models.TextField(null=True, blank=True)
    status_choices = [
        ("Draft", "Draft"),
        ("Published", "Published"),
    ]
    status = models.CharField(choices=status_choices, max_length=24, default="Draft")
    image_1 = models.ImageField(null=True, blank=True, upload_to="service_image1")
    image_2 = models.ImageField(null=True, blank=True, upload_to="service_image1")
    tax = models.ForeignKey(
        Tax, on_delete=models.RESTRICT, null=True, blank=True
    )  # restricting the tax to be deleted when at least one service uses ths.
    type_choices = [
        ("Regular", "Regular"),
        ("Quote", "Quote"),
    ]
    type = models.CharField(max_length=24, choices=type_choices, default="Regular")
    colour = models.CharField(max_length=128, default="#FFA500")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Package(models.Model):
    """Package under a particular service. Many package can exist for a service and a Package can have many Items."""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE
    )  # many package can exist for a Service
    title = models.CharField(max_length=128)
    image_12pack= models.ImageField(null=True, blank=True, upload_to="service_image1")

    type_choices = [
        ("select", "Select"),
        ("card", "Card"),
    ]
    front_end_field_type = models.CharField(
        max_length=24, choices=type_choices, default="select"
    )
    # Defines how this field will be displayed on the frontend. Still in planning stage.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Item(models.Model):
    """Item under a Package. Many item can exist for a package."""

    package = models.ForeignKey(
        Package, on_delete=models.CASCADE
    )  # many Item can exist for a Package
    title = models.CharField(max_length=128)
    time_hrs = models.DecimalField(max_digits=36, decimal_places=2, default=0)
    price = models.DecimalField(max_digits=36, decimal_places=2, default=0)
    discount_percent = models.PositiveIntegerField(
        default=0
    )  # cannot be greater than 100
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if 0 > self.discount_percent > 100:
            raise Http404("Failed! Discount should 0 to 100.")
        if 0 >= self.price:
            raise Http404("Failed! Price should be greater than zero.")
        return super(Item, self).save(*args, **kwargs)


class Extra(models.Model):
    """Extra under a Service. Many Extra can exist for a Service."""

    service = models.ForeignKey(
        Service, on_delete=models.CASCADE
    )  # many Extra can exist for a Service
    title = models.CharField(max_length=128)
    time_hrs = models.DecimalField(max_digits=36, decimal_places=2, default=0)
    image_12 = models.ImageField(null=True, blank=True, upload_to="service_image1")
    tool_tip = models.CharField(max_length=256, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if 0 >= self.price:
            raise Http404("Failed! Price should be greater than zero.")
        if 0 >= self.time_hrs:
            raise Http404("Failed! time should be greater than zero.")
        return super(Extra, self).save(*args, **kwargs)


class BODContactInfo(models.Model):
    """
    Booking contact info. e.g.: name, email, phone, how to enter to the premises guide.
    """

    first_name = models.CharField(max_length=48)
    last_name = models.CharField(max_length=48)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=24, null=False, blank=False)
    how_to_enter_on_premise = models.CharField(max_length=256, null=True, blank=True)
    do_parking_spot = models.BooleanField(default=False)
    do_you_pets = models.BooleanField(default=False)
    how_do_you_hear_about_us = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_full_name(self):
        return self.first_name + " " + self.last_name


class BookingAbstract(models.Model):
    """
    The booking Abstract model.
    """

    type_choices = [
        ("Residential", "Residential"),
        ("Commercial", "Commercial"),
        ("Other", "Other"),
    ]
    type = models.CharField(max_length=24, choices=type_choices, null=True, blank=True)
    start_time = models.CharField(
        max_length=24
    )  # must have : between value like 18:50. At what o clock. appointment_start_time
    total_hours = models.FloatField(null=True, blank=True)
    # must have : between value like 18:50. At what o clock. appointment_start_time
    total_amount = models.FloatField(default=0.00)
    latest_reschedule = models.IntegerField(
        help_text="In hours. 0 means at any time.", default=24
    )  # in hours. On frontend calculate the hour and maybe show more human friendly value!\
    # e.g. 1day, 2day. 0 means at anytime. how late can be reschedule from client end.
    latest_cancel = models.IntegerField(
        help_text="In hours. 0 means at any time.", default=24
    )  # in hours. how late can be cancelled from client end.
    additional_info = models.TextField(
        help_text="Any particular instructions. Or notes?", blank=True, null=True
    )  # extra notes/additional info, can see all party.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Frequency(models.Model):
    """
    Weekly or monthly or daily such types of data for a particular booking(bod). With discount field for auto calculation.
    Only one instance get created for one bod. This model defines if a booking(bod) is recurring or onetime. And also
    links with the service instance.
    """

    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    type_choices = [
        ("once", "Once"),
        ("weekly", "Weekly"),
        ("biweekly", "Biweekly"),
        ("monthly", "Monthly"),
    ]
    type = models.CharField(max_length=48, choices=type_choices)  # unique=True
    title = models.CharField(max_length=256)  # The name that will be shown to the user.
    discount_percent = models.PositiveIntegerField(default=0)  # max can be 100
    discount_amount = models.PositiveIntegerField(default=0)
    # Any but within this two field we have to implement logic so that value never goes negative and works \
    # together perfectly. maybe allow only to use only one field at a time.
    start_date = models.DateField()
    # first appointment date. for single recurrence and multiple both.
    recur_end_date = models.DateTimeField(blank=True, null=True)
    # only take the date? e.g.: 24/06/2022. don't care about the time? or implement as it suits best!
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceLocationAbstract(models.Model):
    """
    Abstract model. Booking exact location, saves during placing a booking. e.g.: street address, city and etc.
    """

    street_address = models.CharField(max_length=128)
    apt_suite = models.CharField(max_length=128)  # apartment/flat/suite/Unit etc.
    city = models.CharField(max_length=48)
    state_choices = [
        ("nyc", "NYC"),
        ("ca", "CA"),
        ("fl", "FL"),
    ]
    state = models.CharField(max_length=48, choices=state_choices)
    zip_code = models.IntegerField()
    let_long = models.CharField(max_length=56, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BODServiceLocation(ServiceLocationAbstract):
    pass


class BookingOrderDetails(BookingAbstract):
    """
    The parent booking order model. Creates when a order placed. Based on the order details Booking instance gets created.
    For example if an order is a recurring order then for a 60days of recurrence order should be created at once.
    One BOD instance should get created for one order. BOD instance == an order.
    """

    bod_contact_info = models.OneToOneField(BODContactInfo, on_delete=models.CASCADE)
    frequency = models.OneToOneField(Frequency, on_delete=models.CASCADE)
    bod_service_location = models.OneToOneField(
        BODServiceLocation, on_delete=models.CASCADE
    )  # must have fields for a booking
    """session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )  # optional field, only applicable for anonymous customers. When a session gets deleted this booking instance \
    will also get deleted! So we need to work on that. We need to save the session on Database. in order save the \
    session we need to modify the session.
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )  # optional field, only applicable for registered customers
    _choices = [
        # ('pending', 'Pending'),  # no use for now!
        (
            "unscheduled",
            "Unscheduled",
        ),  # means active. no booking instance yet created.
        (
            "scheduled",
            "Scheduled",
        ),  # means recurring object created. dispatch will be maintained from schedule model.
        ("complete", "Complete"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=48, choices=_choices, default="unscheduled")

    colour = models.CharField(max_length=124, default="#FFA500")


class ServiceLocation(ServiceLocationAbstract):
    """
    Booking exact location, saves during placing a booking. e.g.: street address, city and etc.
    """

    pass


class Booking(BookingAbstract):
    """
    The booking model. Every time a booking takes in place, an instance of this should get created along with
    other related table.
    """

    bod = models.ForeignKey(BookingOrderDetails, on_delete=models.CASCADE)
    service_location = models.OneToOneField(
        ServiceLocation, on_delete=models.CASCADE
    )  # must have fields for a booking
    _choices = [
        ("unscheduled", "Unscheduled"),
        ("scheduled", "Scheduled"),
        ("dispatched", "Dispatched"),
        ("complete", "Complete"),
        ("cancelled", "Cancelled"),
    ]
    status = models.CharField(max_length=48, choices=_choices, default="unscheduled")
    customer_notes = models.CharField(max_length=250, default="null", blank=True)
    cleaner_notes = models.CharField(max_length=250, default="null", blank=True)
    three_day_reminder = models.BooleanField(default=False)
    one_day_reminder = models.BooleanField(default=False)
    three_hour_reminder = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    latitude = models.CharField(max_length=124, default="null")
    longitude = models.CharField(max_length=124, default="null")
    appointment_date_time = (
        models.DateTimeField()
    )  # when the appointment will be scheduled if scheduled.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BookingItemDetailsAbstract(models.Model):
    """
    Abstract model. All the items that a client orders for a particular booking.
    """

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BODItemDetails(BookingItemDetailsAbstract):
    """
    BookingOrderDetails(BOD). All the items that a client orders for a particular booking.
    """

    bod = models.ForeignKey(BookingOrderDetails, on_delete=models.CASCADE)


class BookingExtraDetailsAbstract(models.Model):
    """
    Abstract model. All the extra that a client orders for a particular booking.
    """

    extra = models.ForeignKey(Extra, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BODExtraDetails(BookingExtraDetailsAbstract):
    """
    BookingOrderDetails(BOD) parent. All the extra that a client orders for a particular booking.
    """

    bod = models.ForeignKey(BookingOrderDetails, on_delete=models.CASCADE)


class Sale(models.Model):
    """
    Payment information for a particular booking. For now it's demo purpose.
    """

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.FloatField()
    paid = models.FloatField(default=0.0)
    status_choices = [
        ("pending", "pending"),
        ("partial", "partial"),
        ("completed", "completed"),
    ]
    status = models.CharField(max_length=24, choices=status_choices, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PaymentSale(models.Model):
    """
    Payment information for a particular booking. For now it's demo purpose.
    """

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, null=True)
    mode = models.CharField(max_length=48, default="card")
    capture = models.CharField(max_length=48, null=True, blank=True)
    is_captured = models.BooleanField(default=True)
    is_first = models.BooleanField(default=False)
    amount = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BookingItemDetails(BookingItemDetailsAbstract):
    """
    All the items that a client orders for a particular booking. Copied from BOD parent.
    """

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class BookingExtraDetails(BookingExtraDetailsAbstract):
    """
    All the extra that a client orders for a particular booking. Copied from BOD parent.
    """

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)


class Schedule(models.Model):
    """
    Booking Schedule model for cleaners/service providers. A month of schedule should get created at once for recurring booking for the cleaners.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_in_schedule",
        null=True,
        blank=True,
    )
    booking = models.OneToOneField(
        Booking, on_delete=models.CASCADE, related_name="booking_in_schedule"
    )
    start_time = (
        models.DateTimeField()
    )  # !!! must have : between value like 18:50. with correct date and time
    end_time = models.DateTimeField()  # must have : between value like 20:50
    status_choices = [
        ("Scheduled", "Scheduled"),
        ("Dispatched", "Dispatched"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]
    status = models.CharField(
        max_length=24, choices=status_choices, default="Scheduled"
    )
    shift_started = models.BooleanField(default=False)
    colour = models.CharField(max_length=124, default="#FFA500")
    shift_ended = models.BooleanField(default=False)
    shift_status_choices = [
        ("pending", "pending"),
        ("on_progress", "on_progress"),
        ("completed", "completed"),
    ]
    tip_amount = models.FloatField(default=0.00)
    shift_status = models.CharField(
        max_length=24, choices=shift_status_choices, default="pending"
    )
    count = models.IntegerField(
        default=1
    )  # count of schedule for a particular booking. Should increment for the same booking schedule.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # if the record is new
            schedules = Schedule.objects.filter(booking=self.booking)
            self.count = schedules.count() + 1
        return super(Schedule, self).save(*args, **kwargs)

    def get_start_hour_minute_pretty(self):
        return str(self.start_time.hour) + ":" + str(self.start_time.minute)

    def get_end_hour_minute_pretty(self):
        return str(self.end_time.hour) + ":" + str(self.end_time.minute)

    def get_start_end_hyphened(self):
        return (
                self.get_start_hour_minute_pretty()
                + " - "
                + self.get_end_hour_minute_pretty()
        )


class UserStripe(models.Model):
    bod = models.CharField(max_length=148, default="0")
    user = models.CharField(max_length=250, null=True, blank=True)
    email = models.CharField(max_length=250, null=True, blank=True)
    stripe_customer = models.CharField(max_length=148)


class BookingProblem(models.Model):
    """
    Payment log for each Invoice instance
    """

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    message = models.CharField(max_length=512)
    status_choices = [
        ("Active", "Active"),
        ("Solved", "Solved"),
    ]
    status = models.CharField(max_length=30, choices=status_choices, default="Active")
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)


class BookingAttachments(models.Model):
    """
    Abstract model. Attachment such as jpg, png for a particular booking.
    """

    file = models.FileField()
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="booking_attachments"
    )
    share_with_customer = models.BooleanField(default=False)
    share_with_cleaner = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=True)


class DispatchedAppointment(models.Model):
    """Dispatched to user"""

    service_provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_in_dispatched_appointment"
    )
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="booking_in_dispatched_appointment",
        null=True,
        blank=True,
    )
    status_choices = [
        ("Dispatched", "Dispatched"),
        ("Cancelled", "Cancelled"),
    ]
    status = models.CharField(
        max_length=24, choices=status_choices, default="Dispatched"
    )
    shift_started = models.BooleanField(default=False)
    shift_ended = models.BooleanField(default=False)
    start_time = models.DateTimeField(
        null=True, blank=True
    )  # !!! must have : between value like 18:50. with correct date and time
    end_time = models.DateTimeField(null=True, blank=True)
    shift_status_choices = [
        ("pending", "pending"),
        ("on_progress", "on_progress"),
        ("completed", "completed"),
    ]
    shift_status = models.CharField(
        max_length=24, choices=shift_status_choices, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_start_hour_minute_pretty(self):
        return str(self.start_time.hour) + ":" + str(self.start_time.minute)

    def get_end_hour_minute_pretty(self):
        return str(self.end_time.hour) + ":" + str(self.end_time.minute)

    def get_start_end_hyphened(self):
        return (
                self.get_start_hour_minute_pretty()
                + " - "
                + self.get_end_hour_minute_pretty()
        )


class CustomerSupportCollection(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_in_customer_support_collection",
        null=True,
        blank=True,
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CustomerSupportChat(models.Model):
    collection = models.ForeignKey(
        CustomerSupportCollection,
        on_delete=models.CASCADE,
        related_name="collection_in_chat",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_in_customer_support",
        null=True,
        blank=True,
    )
    message = models.CharField(max_length=200, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CleanyBranches(models.Model):
    """Totally not related with the app. This is is an additional service. Helps route mobile app remote server."""

    title = models.CharField(max_length=128)
    uri = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChatRoom(models.Model):
    """ChatRoom."""

    bod = models.OneToOneField(BookingOrderDetails, on_delete=models.CASCADE)
    status_choices = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Disabled", "Disabled"),
    ]
    status = models.CharField(max_length=24, choices=status_choices, default="Active")
    type = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class AllowedUser(models.Model):
    """AllowedUser."""

    user = models.ManyToManyField(User)
    chatroom = models.OneToOneField(ChatRoom, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class MessageInfo(models.Model):
    """MessageInfo."""

    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    from_user_name = models.CharField(max_length=64, blank=True, editable=False)
    chatroom = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    message = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    # updated_at = models.DateTimeField(auto_now=True)

    def get_user_full_name(self):
        if self.from_user.groups.filter(name="service_provider"):
            return f"{UserProfile.objects.get(user=self.from_user).get_full_name()}"
        else:
            return f"{UserProfile.objects.get(user=self.from_user).get_full_name()}"

    def save(self, *args, **kwargs):
        if (
                not self.pk
        ):  # if primary key not created yet, means object not saved on db yet.
            self.from_user_name = self.get_user_full_name()
        return super(MessageInfo, self).save(*args, **kwargs)


class SpOperatingHour(models.Model):
    """
    Service Provider Operating Hours by day. Only 7 record can exist for 7 days. By default wizard should create all 7 records while
    creations of a service provider.
    """

    service_provider = models.ForeignKey(User, on_delete=models.CASCADE)
    day_choices = [
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
    ]
    day = models.CharField(max_length=24, choices=day_choices)
    is_available = models.BooleanField(default=True)
    start_hour = models.TimeField(default="08:00")  # e.g.: '09:30' %H:%M
    end_hour = models.TimeField(default="17:00")  # e.g.: '18:00' %H:%M
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.day}"

    def save(self, *args, **kwargs):
        if (
                not self.pk
        ):  # if primary key not created yet, means object not saved on db yet.
            # print(SpOperatingHour.objects.filter(service_provider=self.service_provider).all().count(), ': is?')
            if (
                    SpOperatingHour.objects.filter(service_provider=self.service_provider)
                            .all()
                            .count()
                    >= 7
            ):
                raise Http404(
                    "Failed! Cannot create more than 7 days for a service provider."
                )
        return super(SpOperatingHour, self).save(*args, **kwargs)

    def get_html_friendly_start_hour(self):
        """Returns start hour in str(00:00:00) format"""
        if self.start_hour.hour >= 10:
            hour = str(self.start_hour.hour)
        else:
            hour = "0" + str(self.start_hour.hour)

        if self.start_hour.minute >= 10:
            minute = str(self.start_hour.minute)
        else:
            minute = "0" + str(self.start_hour.minute)

        if self.start_hour.second >= 10:
            second = str(self.start_hour.minute)
        else:
            second = "0" + str(self.start_hour.second)

        return hour + ":" + minute + ":" + second

    def get_html_friendly_end_hour(self):
        """Returns end hour in str(00:00:00) format"""
        if self.end_hour.hour >= 10:
            hour = str(self.end_hour.hour)
        else:
            hour = "0" + str(self.end_hour.hour)

        if self.end_hour.minute >= 10:
            minute = str(self.end_hour.minute)
        else:
            minute = "0" + str(self.end_hour.minute)

        if self.end_hour.second >= 10:
            second = str(self.end_hour.minute)
        else:
            second = "0" + str(self.end_hour.second)

        return hour + ":" + minute + ":" + second


class PageViewsCount(models.Model):
    """PageViewsCount."""

    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BookingNotifications(models.Model):
    """
    Booking order client end page views count.
    """

    bod = models.ForeignKey(
        BookingOrderDetails, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="cleaner_in_notifications", null=True, blank=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=256)
    mark_as_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Payroll(models.Model):
    """Payroll."""

    sp = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="service_provider_in_payroll"
    )
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_in_payroll",
                                null=True, blank=True)
    hourly_wage = models.FloatField(default=0.00)
    total_hours = models.FloatField(default=0.00)
    total_amount = models.FloatField(default=0.00)
    tip_amount = models.FloatField(default=0.00)
    paid_amount = models.FloatField(default=0.00)
    due_amount = models.FloatField(default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Invoice(models.Model):
    """Invoice"""

    sp = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="service_provider_in_invoice"
    )
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    status_choices = [
        ("Paid", "Paid"),
        ("Partial", "Partial"),
        ("Due", "Due"),
    ]
    status = models.CharField(max_length=30, choices=status_choices, default="Due")
    hourly_wage = models.FloatField(default=0.00)
    total_hours = models.FloatField(default=0.00)
    total_amount = models.FloatField(default=0.00)
    tip_amount = models.FloatField(default=0.00)
    paid_amount = models.FloatField(default=0.00)
    due_amount = models.FloatField(default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ChargeTip(models.Model):
    """ChargeTip"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE,
                                related_name="booking_in_charge_tip", null=True, blank=True)
    tip_amount = models.FloatField(default=0.00)
    charge_id = models.CharField(max_length=256, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserInvoices(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_in_user_invoices")
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="booking_in_user_invoices")
    items_amount = models.FloatField(default=0.00)
    extra_amount = models.FloatField(default=0.00)
    total_amount = models.FloatField(default=0.00)
    tax_amount = models.FloatField(default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EmailTypes(models.Model):
    """
    Email types
    """

    MAIL_TYPES = [
        ('Confirmation', 'Confirmation'),
        ('Cancelled', 'Cancelled'),
        ('Modified', 'Modified'),
        ('Reminder', 'Reminder'),

    ]
    subject = models.CharField(max_length=256)
    body = models.TextField()
    email_type = models.CharField(max_length=30, choices=MAIL_TYPES)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)


class EmailLogs(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_in_email_logs")
    title = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PayrollLedger(models.Model):
    """Payroll ledger."""

    payroll = models.ManyToManyField(Payroll, related_name="payroll_in_payroll_ledger")
    service_provider = models.ForeignKey(User, on_delete=models.CASCADE,
                                         related_name="service_provider_in_payroll_ledger")
    total_amount = models.FloatField(default=0.00)


class Banners(models.Model):
    """Banners for the service page"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    image = models.ImageField(null=True, blank=True, upload_to='service_image1')
    description = models.TextField(default = 'null', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

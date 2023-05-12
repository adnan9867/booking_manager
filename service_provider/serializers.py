from django.db import transaction
from rest_framework import serializers

from booking.models import BookingOrderDetails, Booking
from booking.serializers import BookingSerializerList
from service_provider.models import (
    LeaveTime,
    ServiceProviderTasks,
    ServiceProviderLocation, ManagerTask,
)
from user_module.models import User, UserProfile


class CleanerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    zip_code = serializers.CharField(write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(write_only=True, required=False)
    time_zone = serializers.CharField(write_only=True, required=False)
    document = serializers.FileField(write_only=True, required=False)
    profile_picture = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "role",
            "password",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "gender",
            "language",
            "time_zone",
            "document",
            "profile_picture",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context["request"]
            data = request.data
            validated_data["role"] = "Cleaner"
            email = User.objects.filter(email=validated_data["email"]).first()
            if email:
                raise serializers.ValidationError("Email already exists")
            user = User.objects.create(email=validated_data["email"])
            user.set_password(validated_data["password"])
            user.save()
            UserProfile.objects.create(
                role=validated_data["role"],
                user=user,
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone_number=data["phone"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                gender=data["gender"],
                language=data["language"],
                time_zone=data["time_zone"],
                document=data["document"],
                profile_picture=data["profile_picture"],
                color=data["color"] or "#800020",
            )
            return user


class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    zip_code = serializers.CharField(write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(write_only=True, required=False)
    time_zone = serializers.CharField(write_only=True, required=False)
    document = serializers.FileField(write_only=True, required=False)
    profile_picture = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "role",
            "password",
            "email",
            "phone",
            "address",
            "city",
            "state",
            "zip_code",
            "gender",
            "language",
            "time_zone",
            "document",
            "profile_picture",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context["request"]
            data = request.data
            validated_data["role"] = "Customer"
            email = User.objects.filter(email=validated_data["email"]).first()
            if email:
                raise serializers.ValidationError("Email already exists")
            user = User.objects.create(email=validated_data["email"])
            user.set_password(validated_data["password"])
            user.save()
            UserProfile.objects.create(
                role=data["role"],
                user=user,
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone_number=data["phone"],
                address=data["address"],
                city=data["city"],
                state=data["state"],
                zip_code=data["zip_code"],
                gender=data["gender"],
                language=data["language"],
                time_zone=data["time_zone"],
                document=data["document"],
                profile_picture=data["profile_picture"],
            )
            return user


class CustomerSerializerCsv(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone_number = serializers.CharField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    city = serializers.CharField(write_only=True, required=False)
    state = serializers.CharField(write_only=True, required=False)
    zip_code = serializers.CharField(write_only=True, required=False)
    gender = serializers.CharField(write_only=True, required=False)
    language = serializers.CharField(write_only=True, required=False)
    time_zone = serializers.CharField(write_only=True, required=False)
    document = serializers.FileField(write_only=True, required=False)
    profile_picture = serializers.FileField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "password",
            "email",
            "phone_number",
            "address",
            "city",
            "state",
            "zip_code",
            "gender",
            "language",
            "time_zone",
            "document",
            "profile_picture",
        ]

    def create(self, validated_data):
        with transaction.atomic():
            request = self.context["request"]
            data = request.data
            validated_data["role"] = "Customer"
            email = User.objects.filter(email=validated_data["email"]).first()
            if email:
                raise serializers.ValidationError("Email already exists")
            user = User.objects.create(email=validated_data["email"])
            user.set_password(validated_data["password"])
            user.save()
            UserProfile.objects.create(
                role='Customer',
                user=user,
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                phone_number=validated_data["phone_number"],
                address=validated_data["address"],
                city=validated_data["city"],
                state=validated_data["state"],
                zip_code=validated_data["zip_code"],
                gender=validated_data["gender"],
                language=validated_data["language"],
            )
            return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class UserProfileSerializerNew(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField("get_profile")

    class Meta:
        model = User
        fields = ["id", "email", "profile"]

    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.filter(user=obj).first()
            return UserProfileSerializer(profile).data
        except:
            return None


class UserListSerializer(serializers.ModelSerializer):
    is_leave = serializers.SerializerMethodField("get_is_leave")
    leave_time = serializers.SerializerMethodField("get_leave_time")
    user_profile = serializers.SerializerMethodField("get_user_profile")
    bookings = serializers.SerializerMethodField("get_bookings")

    class Meta:
        model = User
        fields = ["id", "email", "is_leave", "leave_time", "user_profile", "is_active", 'bookings']

    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.filter(user=obj).first()
        if user_profile:
            return UserProfileSerializer(user_profile).data
        return None

    def get_is_leave(self, obj):
        try:
            leave = LeaveTime.objects.filter(service_provider=obj).first()
            if leave:
                return True
            return False
        except Exception as e:
            return False

    def get_leave_time(self, obj):
        try:
            leave = LeaveTime.objects.filter(service_provider=obj)
            serializer = ClearnerLeaveTimeSerializer(leave, many=True)
            return serializer.data
        except Exception as e:
            return None

    def get_bookings(self, obj):
        try:
            bod = BookingOrderDetails.objects.filter(user=obj).values_list('id', flat=True)
            bookings = Booking.objects.filter(bod__id__in=bod, status__in=['scheduled', 'dispatched']).first()
            serializer = BookingSerializerList(bookings)
            return serializer.data
        except Exception as e:
            return None


class UserListSerializerNew(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField("get_user_profile")

    class Meta:
        model = User
        fields = ["id", "email", "role"]

    def get_user_profile(self, obj):
        user_profile = UserProfile.objects.filter(user=obj).first()
        if user_profile:
            return UserProfileSerializer(user_profile).data
        return None


class ClearnerSerializerUpdate(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class CustomerSerializerUpdate(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)

    class Meta:
        model = UserProfile
        fields = "__all__"


class ClearnerLeaveTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveTime
        fields = "__all__"


class CleanerTasksSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField("get_user")

    class Meta:
        model = ServiceProviderTasks
        fields = "__all__"

    def get_user(self, obj):
        try:
            return obj.service_provider.email
        except Exception as e:
            return None


class ManagerTaskSerializer(serializers.ModelSerializer):
    manager = UserProfileSerializerNew(read_only=True)

    class Meta:
        model = ManagerTask
        fields = "__all__"


class ManagerTaskSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = ManagerTask
        fields = "__all__"


class ServiceProviderLocationSerializer(serializers.ModelSerializer):
    service_provider = UserProfileSerializerNew(read_only=True)

    class Meta:
        model = ServiceProviderLocation
        fields = "__all__"


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"


class DispatchSerializer(serializers.Serializer):
    cleaner_id = serializers.IntegerField(required=True)
    dispatch_id = serializers.IntegerField(required=True)

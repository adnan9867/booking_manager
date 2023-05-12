from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *


class UserLoginSerializer(serializers.ModelSerializer):
    """
    Serializer for user login.
    """

    email = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(
        trim_whitespace=True,
        max_length=128,
        write_only=True,
    )
    device_token = serializers.CharField(max_length=255, write_only=True, required=False)
    user_id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "role",
            "user_id",
            "full_name",
            "access_token",
            "refresh_token",
            "device_token"
        ]

    def validate(self, attrs) -> dict:
        data = self.context["request"].data
        email = data["email"]
        password = data["password"]
        full_name = None
        if email and password:
            user = User.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError("User does not exist")
            if not user.access_dashboard:
                raise serializers.ValidationError("You are not allowed to login.")
            if user:
                if not user.check_password(password):
                    raise serializers.ValidationError("Incorrect password")
            else:
                raise serializers.ValidationError("User does not exist")
        else:
            raise serializers.ValidationError("Email and password required")
        if not user.access_dashboard:
            raise serializers.ValidationError("Access denied")
        user_profile = UserProfile.objects.filter(user_id=user.id).first()
        if not user_profile:
            raise serializers.ValidationError("User profile does not exist")
        role = None
        if user_profile:
            role = user_profile.role
            full_name = str(user_profile.first_name) + " " + str(user_profile.last_name)
        data_dict = dict()
        data_dict["user_id"] = user.id
        data_dict["role"] = role
        token = RefreshToken.for_user(user)
        data_dict["access_token"] = str(token.access_token)
        data_dict["refresh_token"] = str(token)
        data_dict["full_name"] = full_name
        user.device_token = data.get("device_token", None)
        user.save()
        return data_dict


class UserEmailSignupSerializer(serializers.ModelSerializer):
    role = serializers.CharField(read_only=True)
    email = serializers.CharField(required=True, max_length=255)
    """
    Serializer for user email signup.
    """

    class Meta:
        model = User
        fields = ["id", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.filter(
            email=validated_data["email"],
        ).first()
        if user and not user.booking_account:
            raise serializers.ValidationError("User already exists")
        if user and user.booking_account:
            user.set_password(validated_data["password"])
            user.booking_account = False
            user.access_dashboard = True
            user.save()
            return user
        if not user:
            user = User.objects.create(
                email=validated_data["email"],
                password='123',
                booking_account=False,
            )
            user.set_password(validated_data["password"])
            user.save()
            return user
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(max_length=255)
    first_name = serializers.CharField(max_length=255, write_only=True)
    last_name = serializers.CharField(max_length=255, write_only=True)
    country = serializers.CharField(max_length=255, write_only=True)
    city = serializers.CharField(max_length=255, write_only=True)
    state = serializers.CharField(max_length=255, write_only=True)
    gender = serializers.CharField(max_length=255, write_only=True)
    language = serializers.CharField(max_length=255, write_only=True)
    address = serializers.CharField(max_length=255, write_only=True)
    phone_number = serializers.CharField(max_length=255, write_only=True)
    zip_code = serializers.CharField(max_length=255, write_only=True)
    user_id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    """
    Serializer for user profile.
    """

    class Meta:
        model = UserProfile
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.filter(email=validated_data["email"]).first()
        profile = UserProfile.objects.filter(user_id=user.id).first()
        if profile:
            if not profile.booking_profile:
                raise serializers.ValidationError("User profile already exists")
        if not profile:
            profile = UserProfile.objects.create(user=user, role="Customer")
        profile.first_name = validated_data["first_name"]
        profile.last_name = validated_data["last_name"]
        profile.country = validated_data["country"]
        profile.city = validated_data["city"]
        profile.state = validated_data["state"]
        profile.gender = validated_data['gender']
        profile.language = validated_data["language"],
        profile.address = validated_data["address"],
        profile.phone_number = validated_data["phone_number"],
        profile.zip_code = validated_data["zip_code"],
        profile.booking_profile = False
        profile.save()
        token = RefreshToken.for_user(user)
        access_token = str(token.access_token)
        full_name = profile.first_name + " " + profile.last_name
        data_dict = {
            "user_id": user.id,
            "full_name": full_name,
            "email": validated_data["email"],
            "role": profile.role,
            "refresh_token": str(token),
            "access_token": access_token,
        }
        return data_dict


class CustomerSignupSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=255, write_only=True)
    first_name = serializers.CharField(max_length=255, write_only=True)
    last_name = serializers.CharField(max_length=255, write_only=True)
    country = serializers.CharField(max_length=255, write_only=True)
    city = serializers.CharField(max_length=255, write_only=True)
    state = serializers.CharField(max_length=255, write_only=True)
    gender = serializers.CharField(max_length=255, write_only=True)
    language = serializers.CharField(max_length=255, write_only=True)
    address = serializers.CharField(max_length=255, write_only=True)
    phone_number = serializers.CharField(max_length=255, write_only=True)
    zip_code = serializers.CharField(max_length=255, write_only=True)
    user_id = serializers.IntegerField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    """
    Serializer for user profile.
    """

    class Meta:
        model = UserProfile
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create(email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        profile = UserProfile.objects.create(user=user,
                                             role="Customer",
                                             first_name=validated_data["first_name"],
                                             last_name=validated_data["last_name"],
                                             country=validated_data["country"],
                                             city=validated_data["city"],
                                             state=validated_data["state"],
                                             gender=validated_data['gender'],
                                             language=validated_data["language"],
                                             address=validated_data["address"],
                                             phone_number=validated_data["phone_number"],
                                             zip_code=validated_data["zip_code"],
                                             booking_profile=False,

                                             )
        token = RefreshToken.for_user(user)
        access_token = str(token.access_token)
        full_name = profile.first_name + " " + profile.last_name
        data_dict = {
            "user_id": user.id,
            "full_name": full_name,
            "email": validated_data["email"],
            "role": profile.role,
            "refresh_token": str(token),
            "access_token": access_token,
        }
        return data_dict


class PaymentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    card_no = serializers.CharField(max_length=255)
    exp_m = serializers.CharField(max_length=255)
    exp_y = serializers.CharField(max_length=255)
    cvc = serializers.CharField(max_length=255)


class ForgetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('password',)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class CleanerLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['latitude', 'longitude']


class UserReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReview
        fields = "__all__"


class UserProfilePictureSerializer(serializers.ModelSerializer):
    profile_picture = serializers.FileField(required=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'profile_picture']

from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
import stripe
from booking.models import UserStripe, EmailTypes
from booking.serializers import EmailTypeSerializer
from cleany.base.response_mixins import BaseAPIView
from service_provider.serializers import UpdateUserProfileSerializer, CustomerSerializer, CustomerSerializerCsv
from .serialziers import *
from .utils import forget_password_email, read_csv
import csv
import dotenv
import os
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
stripe.api_key =os.environ['STRIPE_KEY']


class UserLoginViewSet(ModelViewSet, BaseAPIView):
    """
    User Login
    """

    serializer_class = UserLoginSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["User"])
    def create(self, request, *args, **kwargs):
        """
        This function is used to log in user.
        """
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            serializer.is_valid(
                raise_exception=True,
            )
            return self.send_success_response(
                message="User logged in successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return self.send_bad_request_response(
                message=e.args[0],
            )


class MobileLoginViewSet(ModelViewSet, BaseAPIView):
    """
    User Login
    """

    serializer_class = UserLoginSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["User"])
    def create(self, request, *args, **kwargs):
        """
        This function is used to log in user.
        """
        try:
            data = request.data
            serializer = self.serializer_class(data=data, context={"request": request})
            serializer.is_valid(
                raise_exception=True,
            )
            return Response(
                {
                    "success": True,
                    "message": "User logged in successfully.",
                    "role": serializer.data["role"],
                    "user_id": serializer.data["user_id"],
                    "full_name": serializer.data["full_name"],
                    "access_token": serializer.data["access_token"],
                    "refresh_token": serializer.data["refresh_token"],
                }
            )
        except Exception as e:
            return self.send_bad_request_response(
                message=e.args[0],
            )


class UserEmailSignupViewSet(ModelViewSet, BaseAPIView):
    serializer_class = UserEmailSignupSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["User"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="User account created successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class UserAccountInformationView(ModelViewSet, BaseAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["User"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            user = self.queryset.filter(email=data["email"]).first()
            if not user:
                return self.send_bad_request_response(message="User not exist")
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Account created successfully", data=serializer.data
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class CustomerSignUpView(ModelViewSet, BaseAPIView):
    serializer_class = CustomerSignupSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=["User"])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            user = self.queryset.filter(email=data["email"]).first()
            if user:
                return self.send_bad_request_response(message="User already exist")
            serializer = self.serializer_class(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="Account created successfully", data=serializer.data
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class UserProfileViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = None

    def retrieve(self, request, *args, **kwargs):
        try:
            user = request.user
            serializer = self.serializer_class(user)
            return self.send_success_response(
                message="User profile fetched successfully.",
                data=serializer.data,
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class UpdateUserProfile(BaseAPIView, ModelViewSet):
    serializer_class = UpdateUserProfileSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=["Update User Profile"])
    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            user = request.user
            profile = UserProfile.objects.filter(user=user).first()
            serializer = self.serializer_class(
                profile, data=data, partial=True, context={"request": request}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return self.send_success_response(
                    message="User profile updated successfully"
                )
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class UserPaymentMethod(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = None
    serializer_class = PaymentSerializer

    @swagger_auto_schema(tags=["User Payment Method"])
    def create(self, request, *args, **kwargs):
        try:
            _user = request.user
            user_stripe = UserStripe.objects.filter(user=_user.email).first()
            if not user_stripe:
                user_stripe = UserStripe.objects.create(user=_user.email)
                customer = stripe.Customer.create(
                    email=user_stripe.user,
                    description="Customer for " + user_stripe.user,
                )
                user_stripe.stripe_customer = customer.id
                user_stripe.save()
            token = stripe.Token.create(
                card={
                    "name": request.data.get('name'),
                    "number": request.data.get('card_no'),
                    "exp_month": request.data.get('exp_m'),
                    "exp_year": request.data.get('exp_y'),
                    "cvc": request.data.get('cvc'),
                },
            )

            customer = stripe.Customer.create_source(
                user_stripe.stripe_customer,
                source=token)
            stripe.Customer.modify(
                user_stripe.stripe_customer,
                default_source=customer.id
            )
            return self.send_success_response(
                message="Card added successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    @swagger_auto_schema(tags=["User Payment Method"])
    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            user_stripe = UserStripe.objects.filter(user=user.email).first()
            if not user_stripe:
                return self.send_bad_request_response(message="No card found")
            cards = stripe.Customer.list_sources(
                user_stripe.stripe_customer,
                object="card",
                limit=3,
            )
            return self.send_success_response(
                message="Cards fetched successfully",
                data=cards
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])

    def destroy(self, request, *args, **kwargs):
        try:
            user = request.user
            user_stripe = UserStripe.objects.filter(user=user.email).first()
            if not user_stripe:
                return self.send_bad_request_response(message="No card found")
            stripe.Customer.delete_source(
                user_stripe.stripe_customer,
                request.data.get('card_id')
            )
            return self.send_success_response(
                message="Card deleted successfully"
            )
        except Exception as e:
            return self.send_bad_request_response(message=e.args[0])


class AdminCardDetailViewSet(ModelViewSet, BaseAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserStripe.objects.all()
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(tags=["Admin Payment Method"])
    def list(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(id=request.GET.get('user_id')).first()
            if not user:
                return self.send_bad_request_response(message="User not found")
            user_stripe = UserStripe.objects.filter(user=user.email).first()
            if not user_stripe:
                return self.send_bad_request_response(message="No card found")
            cards = stripe.Customer.list_sources(
                user_stripe.stripe_customer,
                object="card",
                limit=3,
            )
            return self.send_success_response(
                message="Cards fetched successfully",
                data=cards
            )
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ForgetPassword(ModelViewSet, BaseAPIView):
    serializer_class = ForgetPasswordSerializer
    queryset = User.objects.all()

    @swagger_auto_schema(tags=['User Password'])
    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            user = User.objects.filter(email=email).first()
            if not user:
                return self.send_bad_request_response(message="User not found")
            forget_password_email(user=user, template="forget_password.html")
            return self.send_success_response(message="Reset Password Email Sent successfully", data=user.email)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ResetPassword(ModelViewSet, BaseAPIView):
    permission_classes = []
    serializer_class = ResetPasswordSerializer
    queryset = None

    @swagger_auto_schema(tags=['User Password'])
    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            user = User.objects.filter(email=request.data.get('email')).first()
            verification_code = VerificationCode.objects.filter(
                user=user,
                code=request.data.get('code'),
            ).first()
            if not verification_code:
                return self.send_bad_request_response(message="Verification code not found")
            if not verification_code.is_active:
                return self.send_bad_request_response(message="Verification code expired")
            if not int(verification_code.code) == request.data.get('code'):
                return self.send_bad_request_response(message="Verification code not matched")
            verification_code.is_active = False
            verification_code.save()
            serializer = self.serializer_class(instance=user, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_success_response(data=serializer.data, message="Password updated successfully")
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class EmailTypesViewSet(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EmailTypes.objects.all()
    serializer_class = EmailTypeSerializer

    @swagger_auto_schema(tags=["Email Types"])
    def list(self, request, *args, **kwargs):
        try:
            email_types = EmailTypes.objects.all().order_by('-id')
            serializer = self.serializer_class(email_types, many=True)
            return self.send_success_response(message="Email Types fetched successfully", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class ImportCustomerCsv(BaseAPIView, ModelViewSet):
    # permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CustomerSerializerCsv

    def create(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file')
            file_data = read_csv(file)
            for data in file_data:
                serializer = self.serializer_class(data=data, context={'request': request})
                if serializer.is_valid():
                    serializer.save()
                else:
                    return self.send_bad_request_response(message=serializer.errors)
            return self.send_success_response(message="Customers imported successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class CleanerLocationView(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CleanerLocationSerializer

    def create(self, request, *args, **kwargs):
        try:
            profile = UserProfile.objects.filter(user=request.user).first()
            if not profile:
                return self.send_bad_request_response(message="Profile not found")
            if not profile.role == 'Cleaner':
                return self.send_bad_request_response(message="Only cleaner can add location")
            profile.latitude = request.data.get('latitude')
            profile.longitude = request.data.get('longitude')
            profile.save()
            return self.send_success_response(message="Location updated successfully")
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UserReviewSystem(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserReview.objects.all()
    serializer_class = UserReviewSerializer

    def create(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data
            service = data.get('service', None)
            cleaner = data.get('cleaner', None)
            if not service and not cleaner:
                return self.send_bad_request_response(message="Service or cleaner required")
            data['customer'] = user.id
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return self.send_success_response(message="Review added successfully", data=serializer.data)
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    def customer_reviews(self, request, *args, **kwargs):
        try:
            review_type = request.data.get('review_type', None)
            cleaner_reviews = UserReview.objects.filter(customer=request.user).order_by('-id')
            if review_type:
                cleaner_reviews = cleaner_reviews.filter(review_type=review_type)
            serializer = self.serializer_class(cleaner_reviews, many=True)
            return self.send_success_response(message="Reviews fetched successfully", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    def update(self, request, *args, **kwargs):
        try:
            data = request.data
            user_review = UserReview.objects.filter(id=data.get('id')).first()
            if not user_review:
                return self.send_bad_request_response(message="Review not found")
            serializer = self.serializer_class(instance=user_review, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_success_response(message="Review updated successfully", data=serializer.data)
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

    def list(self, request, *args, **kwargs):
        try:
            user = request.user
            user_review = UserReview.objects.filter(customer=user).order_by('-id')
            serializer = self.serializer_class(user_review, many=True)
            return self.send_success_response(message="Reviews fetched successfully", data=serializer.data)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))


class UpdateUserProfilePicture(BaseAPIView, ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserProfilePictureSerializer

    def update(self, request, *args, **kwargs):
        try:
            user = request.user
            data = request.data
            if not data.get('profile_picture', None):
                return self.send_bad_request_response(message="Profile picture required")
            serializer = self.serializer_class(instance=user.user_in_profile, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return self.send_success_response(message="Profile updated successfully", data=serializer.data)
            return self.send_bad_request_response(message=serializer.errors)
        except Exception as e:
            return self.send_bad_request_response(message=str(e))

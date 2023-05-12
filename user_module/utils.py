import csv
import random
import pandas as pd

from django.core.mail import EmailMessage
from django.template.loader import get_template

from cleany import settings
from user_module.models import User, VerificationCode


def expire_previous_code(user: User):
    """
    Expire previous verification code
    """
    previous_code = VerificationCode.objects.filter(user=user, is_active=True)
    if previous_code.exists():
        previous_code.update(is_active=False)


def create_verification(user: User):
    """
    Create a verification code for the user
    """
    code = random.randint(100000, 999999)
    verification = VerificationCode.objects.filter(code=code)
    if verification.exists():
        create_verification(user=user)
    expire_previous_code(user=user)
    VerificationCode.objects.create(code=code, user=user)
    return code


def forget_password_email(user: User, template: str = "verify_email.html"):
    """
        Send email to user
        """
    code = create_verification(user=user),
    rtx = {
        "name": user.first_name + " " + user.last_name,
        'code': code
    }
    message = get_template(template).render(rtx)
    email = EmailMessage(
        subject="User SignUp",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


def read_csv(path):
    """Read the csv into dictionaries, transform the keys necessary
    and return a list of cleaned-up dictionaries.
    """
    data = pd.read_csv(path)
    return data.to_dict('records')


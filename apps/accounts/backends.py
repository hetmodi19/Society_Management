from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User
from apps.properties.models import Unit

class UniversalAuthBackend(ModelBackend):
    """
    Universal multi-identifier authentication backend for SmartSociety 360.
    Allows authentication by:
    1. Username (case-insensitive)
    2. Email address (case-insensitive)
    3. Phone number (normalized digits)
    4. Full Name or First Name (e.g. 'Rajesh Sharma', 'Vikram Malhotra')
    5. Flat / Unit Number (e.g. 'A-402', 'B-201', 'A101')
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        identifier = str(username).strip()

        # 1. Exact or case-insensitive username match
        user = User.objects.filter(username__iexact=identifier).first()

        # 2. Email match (case-insensitive)
        if not user:
            user = User.objects.filter(email__iexact=identifier).first()

        # 3. Phone number match
        if not user:
            digits_only = ''.join(c for c in identifier if c.isdigit())
            if len(digits_only) >= 7:
                tail = digits_only[-10:] if len(digits_only) >= 10 else digits_only
                user = User.objects.filter(phone_number__icontains=tail).first()

        # 4. Flat / Unit Number match (e.g. A-402, B-201, A101, 402)
        if not user:
            unit = Unit.objects.filter(unit_number__iexact=identifier).first()
            if not unit:
                # Try adding hyphen if typed as e.g. A402 or B201
                if len(identifier) >= 3 and identifier[0].isalpha() and identifier[1:].isdigit():
                    formatted = f"{identifier[0]}-{identifier[1:]}"
                    unit = Unit.objects.filter(unit_number__iexact=formatted).first()
            if unit:
                user = unit.primary_resident or unit.owner

        # 5. Full name or first name match
        if not user:
            name_parts = identifier.split()
            if len(name_parts) >= 2:
                user = User.objects.filter(
                    first_name__iexact=name_parts[0],
                    last_name__iexact=name_parts[-1]
                ).first()
            elif len(name_parts) == 1:
                user = User.objects.filter(
                    Q(first_name__iexact=name_parts[0]) |
                    Q(last_name__iexact=name_parts[0])
                ).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

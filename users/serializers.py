import re
from rest_framework import serializers
from .models import User, Profile


def validate_password_strength(password):
    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters.")
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("Must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("Must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise serializers.ValidationError("Must contain at least one number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise serializers.ValidationError("Must contain at least one special character.")
    return password


class ProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id", "full_name", "first_name", "last_name",
            "phone", "avatar_url", "current_location",
            "university_name", "major_degree", "graduation_date",
            "how_did_you_hear_about_us", "friend_name",
            "linkedin_url", "portfolio_url", "visa_status",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_full_name(self, obj):
        return obj.full_name


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role", "approval_status", "portal_access", "created_at", "profile"]
        read_only_fields = ["id", "role", "approval_status", "portal_access", "created_at"]


class RegisterSerializer(serializers.Serializer):
    email    = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    role     = serializers.ChoiceField(choices=["candidate", "recruiter"], default="candidate")
    first_name = serializers.CharField(max_length=60)
    last_name  = serializers.CharField(max_length=60)
    phone      = serializers.CharField(max_length=30, required=False, allow_blank=True)
    current_location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    university_name  = serializers.CharField(max_length=120, required=False, allow_blank=True)
    major_degree     = serializers.CharField(max_length=120, required=False, allow_blank=True)
    graduation_date  = serializers.DateField(required=False, allow_null=True)
    how_did_you_hear_about_us = serializers.ChoiceField(
        choices=["LinkedIn", "Google", "University", "Friend", "Social Media", "Other"],
        required=False, allow_blank=True,
    )
    friend_name   = serializers.CharField(max_length=120, required=False, allow_blank=True)
    linkedin_url  = serializers.URLField(required=False, allow_blank=True)
    portfolio_url = serializers.URLField(required=False, allow_blank=True)
    visa_status   = serializers.ChoiceField(
        choices=["H1B", "OPT", "CPT", "Green Card", "US Citizen", "EAD", "TN", "Other"],
        required=False, allow_blank=True,
    )

    def validate_email(self, value):
        return User.objects.normalize_email(value).lower()

    def validate(self, attrs):
        if User.objects.filter(email=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Email already registered."})
        validate_password_strength(attrs["password"])
        if attrs.get("how_did_you_hear_about_us") == "Friend" and not attrs.get("friend_name"):
            raise serializers.ValidationError({"friend_name": "Please provide your friend name."})
        return attrs

    def create(self, validated_data):
        profile_fields = [
            "first_name", "last_name", "phone", "current_location",
            "university_name", "major_degree", "graduation_date",
            "how_did_you_hear_about_us", "friend_name",
            "linkedin_url", "portfolio_url", "visa_status",
        ]
        profile_data = {k: validated_data.pop(k, None) for k in profile_fields}
        role = validated_data.pop("role", "candidate")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=role,
            approval_status="pending_approval",
            portal_access=False,
        )
        Profile.objects.create(user=user, **{k: v for k, v in profile_data.items() if v is not None})
        return user


class ApproveUserSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    action  = serializers.ChoiceField(choices=["approved", "rejected"])


class UserListSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "role", "approval_status", "portal_access", "created_at", "profile"]


class ChangePasswordSerializer(serializers.Serializer):
    current_password     = serializers.CharField(write_only=True)
    new_password         = serializers.CharField(min_length=8, write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        validate_password_strength(attrs["new_password"])
        return attrs

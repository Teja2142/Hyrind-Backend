from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserPublicSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(source='profile.public_id', read_only=True)
    class Meta:
        model = User
        fields = ('id', 'public_id', 'username', 'email')

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'full_name', 'email', 'phone', 'university', 'degree', 'major',
            'visa_status', 'graduation_date', 'resume', 'terms_accepted'
        ]

class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=20)
    university = serializers.CharField(max_length=100, allow_blank=True, required=False)
    degree = serializers.CharField(max_length=100, allow_blank=True, required=False)
    major = serializers.CharField(max_length=100, allow_blank=True, required=False)
    visa_status = serializers.CharField(max_length=50, allow_blank=True, required=False)
    graduation_date = serializers.DateField(required=False)
    resume = serializers.FileField(required=False)
    terms_accepted = serializers.BooleanField()

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        if not data.get('terms_accepted'):
            raise serializers.ValidationError('Terms must be accepted.')
        return data

    def create(self, validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        profile = Profile.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            email=email,
            phone=validated_data['phone'],
            university=validated_data.get('university', ''),
            degree=validated_data.get('degree', ''),
            major=validated_data.get('major', ''),
            visa_status=validated_data.get('visa_status', ''),
            graduation_date=validated_data.get('graduation_date', None),
            resume=validated_data.get('resume', None),
            terms_accepted=validated_data['terms_accepted']
        )
        # Audit log
        try:
            from audit.utils import log_action
            # prefer using public_id for external references
            log_action(actor=user, action='user_registered', target=f'Profile:{str(profile.public_id)}', metadata={'username': username})
        except Exception:
            pass
        return profile

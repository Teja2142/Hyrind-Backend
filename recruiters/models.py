from django.db import models
from users.models import Profile

class Recruiter(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Assignment(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    recruiter = models.ForeignKey(Recruiter, on_delete=models.SET_NULL, null=True)
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name} assigned to {self.recruiter.name if self.recruiter else 'None'}"
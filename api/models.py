import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ExpertiseRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seller = models.ForeignKey(User, related_name='seller_requests', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, related_name='buyer_requests', on_delete=models.CASCADE)
    product_category = models.CharField(max_length=100, choices=[('mobile', 'Mobile'), ('laptop', 'Laptop')])
    address = models.CharField(max_length=255)
    seller_approval = models.BooleanField(default=True)
    buyer_approval = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed')
    ], default='pending')

class Payment(models.Model):
    expertise_request = models.ForeignKey(ExpertiseRequest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=20)
    paid_at = models.DateTimeField(auto_now_add=True)

class Schedule(models.Model):
    expertise_request = models.ForeignKey(ExpertiseRequest, on_delete=models.CASCADE)
    expert = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    scheduled_date = models.DateTimeField(auto_now_add=True)
    result = models.BooleanField(choices=[
        (True, 'Healthy'),
        (False, 'Faulty')
    ], null=True, blank=True, default=None)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['expertise_request'], name='unique_request_expert')
        ]

from rest_framework import serializers, viewsets, permissions, status
from .models import ExpertiseRequest, Payment, Schedule
from django.contrib.auth.models import User



# class ExpertiseRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ExpertiseRequest
#         fields = '__all__'
#         read_only_fields = ('created_at', 'status')
class ExpertiseRequestSerializer(serializers.ModelSerializer):
    seller = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    buyer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = ExpertiseRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'status']

    def validate(self, data):
        # بررسی عدم وجود درخواست مشابه
        if ExpertiseRequest.objects.filter(
            seller=data['seller'],
            buyer=data['buyer'],
            product_category=data['product_category'],
            status__in=['pending', 'approved', 'paid', 'scheduled']
        ).exists():
            raise serializers.ValidationError(
                "A similar request already exists between this seller and buyer for this product category."
            )
        if data['seller'] == data['buyer']:
            raise serializers.ValidationError("Seller and Buyer cannot be the same user")
        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class ScheduleSerializer(serializers.ModelSerializer):
    result = serializers.ChoiceField(
        choices=[(True, 'Healthy'), (False, 'Faulty')],
        allow_null=True,
        required=False
    )

    class Meta:
        model = Schedule
        fields = '__all__'
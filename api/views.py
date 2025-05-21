from django.shortcuts import render
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from .serializers import ExpertiseRequestSerializer, PaymentSerializer, ScheduleSerializer
from api.models import ExpertiseRequest, Payment, Schedule
from django.contrib.auth.models import User



# Create your views here.

# class ExpertiseRequestViewSet(viewsets.ModelViewSet):
#     queryset = ExpertiseRequest.objects.all()
#     serializer_class = ExpertiseRequestSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def perform_create(self, serializer):
#         seller_id = self.request.data.get('seller')
#         if not seller_id:
#             raise serializers.ValidationError("Seller ID is required")
#         try:
#             seller = User.objects.get(id=seller_id)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid Seller ID")
#         buyer_id = self.request.data.get('buyer')
#         if not buyer_id:
#             raise serializers.ValidationError("Buyer ID is required")
#         try:
#             buyer = User.objects.get(id=buyer_id)
#         except User.DoesNotExist:
#             raise serializers.ValidationError("Invalid Buyer ID")
#         if ExpertiseRequest.objects.filter(
#                 seller=seller,
#                 buyer=buyer,
#                 product_category=self.request.data.get('product_category'),
#                 status__in=['pending', 'approved', 'paid', 'scheduled']
#         ).exists():
#             raise serializers.ValidationError(
#                 "A similar request already exists between this seller and buyer for this product category."
#             )
#         serializer.save(seller=seller, buyer=buyer)
#
#     @action(detail=True, methods=['post'])
#     def approve(self, request, pk=None):
#         expertise_request = self.get_object()
#         user_id = request.data.get('user')
#         print("dffereewrerewr")
#         print(user_id)
#         # expertise_request.approve(user_id)
#         if not user_id:
#             return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             user = User.objects.get(id=user_id)
#             print(user)
#         except User.DoesNotExist:
#             return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if user == expertise_request.seller:
#             expertise_request.seller_approval = True
#         elif user == expertise_request.buyer:
#             expertise_request.buyer_approval = True
#         else:
#             return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
#         print(expertise_request.seller_approval)
#         if expertise_request.seller_approval and expertise_request.buyer_approval:
#             expertise_request.status = 'approved'
#             expertise_request.save()
#         else:
#             expertise_request.save()
#         return Response({'status': 'Approval recorded'})

class ExpertiseRequestViewSet(viewsets.ModelViewSet):
    queryset = ExpertiseRequest.objects.all()
    serializer_class = ExpertiseRequestSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # اعتبارسنجی seller
        seller_id = self.request.data.get('seller')
        if not seller_id:
            raise serializers.ValidationError("Seller ID is required")
        try:
            seller = User.objects.get(id=seller_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid Seller ID")

        # اعتبارسنجی buyer
        buyer_id = self.request.data.get('buyer')
        if not buyer_id:
            raise serializers.ValidationError("Buyer ID is required")
        try:
            buyer = User.objects.get(id=buyer_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid Buyer ID")

        # بررسی درخواست تکراری
        if ExpertiseRequest.objects.filter(
                seller=seller,
                buyer=buyer,
                product_category=self.request.data.get('product_category'),
                status__in=['pending', 'approved', 'paid', 'scheduled']
        ).exists():
            raise serializers.ValidationError(
                "A similar request already exists between this seller and buyer for this product category."
            )

        # ذخیره درخواست
        serializer.save(seller=seller, buyer=buyer)

    def partial_update(self, request, pk=None):
        expertise_request = self.get_object()
        print(f"Request data: {request.data}")  # لاگ برای دیباگ
        serializer = self.get_serializer(expertise_request, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # دریافت user_id از درخواست
        user_id = request.data.get('user')
        if not user_id:
            raise serializers.ValidationError("User ID is required")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid User ID")

        # اطمینان از اینکه فقط فروشنده یا خریدار می‌توانند تایید کنند
        if user not in [expertise_request.seller, expertise_request.buyer]:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        # بررسی فیلدهای ارسالی و به‌روزرسانی
        if 'seller_approval' in request.data and user != expertise_request.seller:
            raise serializers.ValidationError("Only the seller can update seller_approval")
        if 'buyer_approval' in request.data and user != expertise_request.buyer:
            raise serializers.ValidationError("Only the buyer can update buyer_approval")

        # به‌روزرسانی درخواست
        serializer.save()
        print(
            f"After save - seller_approval: {expertise_request.seller_approval}, buyer_approval: {expertise_request.buyer_approval}, status: {expertise_request.status}")  # لاگ برای دیباگ

        # تغییر وضعیت به approved اگر هر دو تایید کرده باشند
        if expertise_request.seller_approval and expertise_request.buyer_approval:
            expertise_request.status = 'approved'
            expertise_request.save()
            print(f"Status updated to: {expertise_request.status}")  # لاگ برای دیباگ

        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        expertise_request = self.get_object()
        user_id = request.data.get('user')
        if not user_id:
            raise serializers.ValidationError("User ID is required")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid User ID")

        if user == expertise_request.seller:
            expertise_request.seller_approval = True
        elif user == expertise_request.buyer:
            expertise_request.buyer_approval = True
        else:
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        expertise_request.save()
        print(
            f"Approve action - seller_approval: {expertise_request.seller_approval}, buyer_approval: {expertise_request.buyer_approval}, status: {expertise_request.status}")  # لاگ برای دیباگ
        if expertise_request.seller_approval and expertise_request.buyer_approval:
            expertise_request.status = 'approved'
            expertise_request.save()
            print(f"Status updated to: {expertise_request.status}")  # لاگ برای دیباگ
        return Response({'status': 'Approval recorded'})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        expertise_request = serializer.validated_data['expertise_request']
        if expertise_request.status != 'approved':
            raise serializers.ValidationError('Request must be approved by both parties')
        serializer.save()
        # if Payment.objects.filter(expertise_request=expertise_request).count() == '2':
        #     expertise_request.status = 'paid'
        #     expertise_request.save()


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        expertise_request = serializer.validated_data['expertise_request']
        scheduled_date = serializer.validated_data['scheduled_date']
        if expertise_request.status != 'paid':
            raise serializers.ValidationError('Request must be paid')
        if scheduled_date > (datetime.now().date() + timedelta(days=7)):
            raise serializers.ValidationError('Date must be within next 7 days')
        serializer.save()

    @action(detail=False, methods=['get'])
    def available_requests(self, request):
        available = ExpertiseRequest.objects.filter(status='paid', schedule__isnull=True)
        serializer = ExpertiseRequestSerializer(available, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_expert(self, request, pk=None):
        schedule = self.get_object()
        if schedule.expert:
            return Response({'error': 'Already assigned'}, status=status.HTTP_400_BAD_REQUEST)
        schedule.expert = request.data.get('expert')  # از داده‌های ارسالی
        schedule.expertise_request.status = 'scheduled'
        schedule.expertise_request.save()
        schedule.save()
        return Response({'message': f'Expert assigned for {schedule.scheduled_date}'})

    @action(detail=True, methods=['post'])
    def submit_result(self, request, pk=None):
        schedule = self.get_object()
        result = request.data.get('result')
        if result not in [True, False]:
            return Response({'error': 'Result must be True (Healthy) or False (Faulty)'}, status=status.HTTP_400_BAD_REQUEST)
        schedule.result = result
        schedule.expertise_request.status = 'completed'
        schedule.expertise_request.save()
        schedule.save()
        return Response({'message': 'Result submitted', 'result': 'Healthy' if result else 'Faulty'})

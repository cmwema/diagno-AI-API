from rest_framework.generics import GenericAPIView, RetrieveAPIView, UpdateAPIView
from .serializers import (UserRegisterSerializer, LoginSerializer, PasswordResetRequestSerializer,
                          SetNewPasswordSerializer, ProfileSerializer, ProfileUpdateSerializer)
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .utils import send_otp
from .models import OTP, User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str, DjangoUnicodeDecodeError
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class RegisterUserView(GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            user = serializer.data
            # send email
            send_otp(user['email'])
            return Response({
                'data': user,
                'message': 'user registered successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyUserEmail(GenericAPIView):
    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            user_code_obj = OTP.objects.get(code=otp_code)
            user = user_code_obj.user
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({
                    'message': "account email verified successfully"
                }, status=status.HTTP_200_OK)
            return Response({
                "message": "code is invalid. User email is already verified."
            }, status=status.HTTP_204_NO_CONTENT)

        except OTP.DoesNotExist:
            return Response({
                "message": "passcode not provided"
            }, status=status.HTTP_404_NOT_FOUND)


class LoginUserView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfile(RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer


class UpdateUserProfile(UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileUpdateSerializer


class PasswordResetRequestView(GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        return Response({"message": "A link has been sent to your email to reset your password"})


class PasswordResetConfirm(GenericAPIView):
    def get(self, request, uidb64, token):
        try:
            user_id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=user_id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({"message": "token is invalid or has expired"}, status=status.HTTP_401_UNAUTHORIZED)

            return Response({"success": True, "message":"credentials valid", "uidb64": uidb64, "token":token}, status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            return Response({"message": "token is invalid or has expired"}, status=status.HTTP_401_UNAUTHORIZED)


class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)

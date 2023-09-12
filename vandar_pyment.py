# These codes were written for Vendar and by Ali Kazemzadeh for Django and DRF

import http.client
import json
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class SendRequestView(APIView):
    def post(self, request):
        user = request.user

        if not user.is_authenticated:
            return Response({"error": "شما باید لاگین کنید."}, status=401)

        conn = http.client.HTTPSConnection("ipg.vandar.io")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data = {
            "api_key": "your_api_key",
            "amount": 10000,
            "callback_url": "http://your_callback_url/",
            "mobile_number": user.phone,
        }
        try:
            conn.request("POST", "/api/v3/send", json.dumps(data), headers)
            response = conn.getresponse()
            payment_response = response.read().decode("unicode-escape")
            payment_data = json.loads(payment_response)
            token = payment_data.get('token', None)

            request.session['token'] = token

            return Response(token, status=200)
        except requests.exceptions.RequestException as e:
            return Response({"error": "درخواست پرداخت با مشکل مواجه شد."}, status=500)


class RedirectView(APIView):
    def get(self, request):
        token = request.session.get('token')
        print(token)
        url = f'https://ipg.vandar.io/v3/{token}'

        return redirect(url)


class ProcessTransactionView(APIView):
    def post(self, request):
        token = request.session.get('token')
        url = 'https://ipg.vandar.io/api/v3/transaction'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            'api_key': 'your_api_key',
            'token': token
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return Response({"error": "خطا در پردازش پاسخ"}, status=500)

        return Response(response_data, status=response.status_code)


class VerifyPaymentView(APIView):
    @method_decorator(login_required)
    def post(self, request):
        token = request.session.get('token')
        user = request.user

        url = 'https://ipg.vandar.io/api/v3/verify'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            'api_key': 'your_api_key',
            'token': token
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        try:
            response_data = response.json()
            # اینجا میتوانید موارد لازم که نیاز دارید بعد از پرداخت موفق انجام شود را وارد کنید.

        except json.JSONDecodeError:
            return Response({"error": "خطا در پردازش پاسخ"}, status=500)

        return Response(response_data, status=response.status_code)
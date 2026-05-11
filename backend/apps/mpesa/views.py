from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils import timezone
from .models import MpesaPayment
from apps.subscriptions.models import Subscription, Plan
import requests
import base64
from datetime import datetime
import json
import re

def get_access_token():
    try:
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET), timeout=10)
        return response.json().get('access_token')
    except:
        return None

def format_phone(phone):
    """Format phone number to 2547XXXXXXXX"""
    # Remove all non-digits
    phone = re.sub(r'\D', '', phone)
    # Remove leading zeros
    phone = phone.lstrip('0')
    # Add 254 if not present
    if not phone.startswith('254'):
        phone = '254' + phone
    return phone

@login_required
def initiate_stk_push(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    phone = request.POST.get('phone', '').strip()
    amount = request.POST.get('amount', '')
    plan_id = request.POST.get('plan_id', '')
    
    print(f"RAW INPUT - Phone: '{phone}', Amount: '{amount}', Plan: '{plan_id}'")
    
    if not phone:
        return JsonResponse({'success': False, 'message': 'Phone number is required'}, status=400)
    if not amount:
        return JsonResponse({'success': False, 'message': 'Amount is required'}, status=400)
    
    # Format phone
    phone = format_phone(phone)
    print(f"Formatted phone: {phone}")
    
    try: 
        amount = int(float(amount))
    except: 
        return JsonResponse({'success': False, 'message': 'Invalid amount'}, status=400)
    
    if amount < 1:
        return JsonResponse({'success': False, 'message': 'Amount must be at least Ksh 1'}, status=400)
    
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({'success': False, 'message': 'M-Pesa service unavailable. Try again.'}, status=500)
    
    shortcode = '174379'
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {
        'BusinessShortCode': shortcode,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone,
        'PartyB': shortcode,
        'PhoneNumber': phone,
        'CallBackURL': 'https://sanction-twentieth-elongated.ngrok-free.dev/mpesa/callback/',
        'AccountReference': f'WD-{request.user.username[:8]}',
        'TransactionDesc': 'WebDesign Academy'
    }
    
    print(f"Sending STK Push: {payload}")
    
    try:
        response = requests.post(
            'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
            json=payload, headers=headers, timeout=15
        )
        data = response.json()
        print(f"M-Pesa Response: {data}")
        
        if data.get('ResponseCode') == '0':
            plan = Plan.objects.get(id=plan_id) if plan_id else None
            payment = MpesaPayment.objects.create(
                user=request.user, plan=plan,
                phone_number=phone, amount=amount,
                merchant_request_id=data.get('MerchantRequestID'),
                checkout_request_id=data.get('CheckoutRequestID'),
                status='pending'
            )
            return JsonResponse({
                'success': True,
                'message': '📱 Check your phone! Enter M-Pesa PIN.',
                'payment_id': str(payment.id)
            })
        else:
            error = data.get('ResponseDescription', data.get('errorMessage', 'Payment failed'))
            return JsonResponse({'success': False, 'message': error}, status=400)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

@csrf_exempt
def mpesa_callback(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        print(f"CALLBACK: {json.dumps(data, indent=2)}")
        stk = data.get('Body', {}).get('stkCallback', {})
        cid = stk.get('CheckoutRequestID')
        rc = str(stk.get('ResultCode', ''))
        payment = MpesaPayment.objects.filter(checkout_request_id=cid).first()
        if payment:
            payment.result_code = rc
            payment.result_description = stk.get('ResultDesc', '')
            if rc == '0':
                for item in stk.get('CallbackMetadata', {}).get('Item', []):
                    if item.get('Name') == 'MpesaReceiptNumber':
                        payment.mpesa_receipt_number = item.get('Value')
                payment.status = 'completed'
                payment.save()
                if payment.plan:
                    sub, _ = Subscription.objects.get_or_create(user=payment.user, defaults={'plan': payment.plan})
                    sub.activate_plan(payment.plan)
            else:
                payment.status = 'failed'
                payment.save()
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    except Exception as e:
        print(f"Callback Error: {e}")
        return JsonResponse({'ResultCode': 1, 'ResultDesc': str(e)})

@login_required
def check_status(request, payment_id):
    try:
        payment = MpesaPayment.objects.get(id=payment_id, user=request.user)
        return JsonResponse({'status': payment.status, 'receipt': payment.mpesa_receipt_number})
    except:
        return JsonResponse({'status': 'completed'})

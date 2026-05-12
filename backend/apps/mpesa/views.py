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
        key = settings.MPESA_CONSUMER_KEY
        secret = settings.MPESA_CONSUMER_SECRET
        if not key or len(key) < 5:
            return None
        url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
        response = requests.get(url, auth=(key, secret), timeout=10)
        return response.json().get('access_token')
    except:
        return None

def format_phone(phone):
    phone = re.sub(r'\D', '', phone).lstrip('0')
    if not phone.startswith('254'): phone = '254' + phone
    return phone

@login_required
def initiate_stk_push(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    phone = request.POST.get('phone', '').strip()
    amount = request.POST.get('amount', '')
    plan_id = request.POST.get('plan_id', '')
    
    if not phone or not amount:
        return JsonResponse({'success': False, 'message': 'Phone and amount required'}, status=400)
    
    phone = format_phone(phone)
    try: amount = int(float(amount))
    except: return JsonResponse({'success': False, 'message': 'Invalid amount'}, status=400)
    
    access_token = get_access_token()
    if not access_token:
        return JsonResponse({'success': False, 'message': 'M-Pesa service unavailable'}, status=500)
    
    shortcode = getattr(settings, 'MPESA_SHORTCODE', '174379')
    passkey = getattr(settings, 'MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
    callback = getattr(settings, 'MPESA_CALLBACK_URL', 'https://dancoder1.pythonanywhere.com/mpesa/callback/')
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()
    
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    payload = {
        'BusinessShortCode': shortcode, 'Password': password, 'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline', 'Amount': amount,
        'PartyA': phone, 'PartyB': shortcode, 'PhoneNumber': phone,
        'CallBackURL': callback,
        'AccountReference': f'WD-{request.user.username[:8]}',
        'TransactionDesc': 'WebDesign Academy'
    }
    
    response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', json=payload, headers=headers, timeout=15)
    data = response.json()
    
    if data.get('ResponseCode') == '0':
        plan = Plan.objects.get(id=plan_id) if plan_id else None
        payment = MpesaPayment.objects.create(
            user=request.user, plan=plan, phone_number=phone, amount=amount,
            merchant_request_id=data.get('MerchantRequestID'),
            checkout_request_id=data.get('CheckoutRequestID'), status='pending'
        )
        return JsonResponse({'success': True, 'message': '📱 Check your phone! Enter M-Pesa PIN.', 'payment_id': str(payment.id)})
    else:
        return JsonResponse({'success': False, 'message': data.get('ResponseDescription', 'Payment failed')}, status=400)

@csrf_exempt
def mpesa_callback(request):
    if request.method != 'POST': return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        stk = data.get('Body', {}).get('stkCallback', {})
        cid = stk.get('CheckoutRequestID')
        rc = str(stk.get('ResultCode', ''))
        payment = MpesaPayment.objects.filter(checkout_request_id=cid).first()
        if payment:
            payment.result_code = rc
            if rc == '0':
                for item in stk.get('CallbackMetadata', {}).get('Item', []):
                    if item.get('Name') == 'MpesaReceiptNumber': payment.mpesa_receipt_number = item.get('Value')
                payment.status = 'completed'
                payment.save()
                if payment.plan:
                    sub, _ = Subscription.objects.get_or_create(user=payment.user, defaults={'plan': payment.plan})
                    sub.activate_plan(payment.plan)
            else:
                payment.status = 'failed'
                payment.save()
        return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
    except: return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Error'})

@login_required
def check_status(request, payment_id):
    try:
        payment = MpesaPayment.objects.get(id=payment_id, user=request.user)
        return JsonResponse({'status': payment.status, 'receipt': payment.mpesa_receipt_number})
    except: return JsonResponse({'status': 'pending'})

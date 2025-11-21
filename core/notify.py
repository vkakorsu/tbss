import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from urllib import request as urlrequest
from urllib import parse as urlparse
import json


def send_order_email(order, subject_prefix="Order"):
    subject = f"{subject_prefix} #{order.order_number} - TBSS"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@tbss.com")
    to = [order.email]
    body = render_to_string("emails/order_confirmation.txt", {"order": order})
    try:
        send_mail(subject, body, from_email, to, fail_silently=True)
    except Exception:
        # Ignore email errors in dev
        pass


def send_sms(phone: str, message: str):
    api_key = os.environ.get("HUBTEL_API_KEY")
    client_id = os.environ.get("HUBTEL_CLIENT_ID")
    sender = os.environ.get("HUBTEL_SENDER", "TBSS")
    if not (api_key and client_id):
        return False
    try:
        payload = {
            "from": sender,
            "to": phone,
            "content": message,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urlrequest.Request(
            url="https://sms.hubtel.com/v1/messages/send",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Basic {api_key}:{client_id}",
            },
            method="POST",
        )
        urlrequest.urlopen(req, timeout=5)
        return True
    except Exception:
        return False

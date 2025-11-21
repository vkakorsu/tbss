from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView

from orders.models import Order
from .models import Payment
from core.notify import send_order_email, send_sms


class PaymentsIndexView(TemplateView):
    template_name = "payments/index.html"


def momo_start(request, order_number: str):
    order = get_object_or_404(Order, order_number=order_number)
    payment = getattr(order, "payment", None)
    if not payment:
        payment = Payment.objects.create(order=order, method="momo", provider="mtn-voda-at", status="pending", amount=order.total)

    # In a real integration, call provider API and redirect to approval or prompt USSD.
    # For now, simulate immediate success.
    payment.status = "paid"
    payment.reference = f"SIM-{order.order_number}"
    payment.save(update_fields=["status", "reference"])

    messages.success(request, "Payment successful via Mobile Money.")
    # notifications
    send_order_email(order, subject_prefix="Order Paid")
    send_sms(order.phone, f"TBSS: Payment received for order {order.order_number}. Thank you!")

    # clear cart if any remnants
    request.session["cart"] = {}
    request.session.modified = True

    return redirect("orders:success", order_number=order.order_number)

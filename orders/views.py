from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import TemplateView, View

from catalog.models import Book
from .models import Order, OrderItem, ShippingMethod
from payments.models import Payment
from core.notify import send_order_email, send_sms
from decimal import Decimal
import datetime


def _get_cart(session):
    return session.setdefault("cart", {})


class CartView(TemplateView):
    template_name = "orders/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = _get_cart(self.request.session)
        items = []
        total = 0
        if cart:
            books = Book.objects.filter(slug__in=cart.keys())
            book_map = {b.slug: b for b in books}
            for slug, qty in cart.items():
                book = book_map.get(slug)
                if not book:
                    continue
                line_total = book.price * qty
                total += line_total
                items.append({"book": book, "qty": qty, "line_total": line_total})
        ctx["items"] = items
        ctx["total"] = total
        return ctx


def add_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug, is_active=True)
    if not book.in_stock:
        messages.error(request, "This book is currently out of stock.")
        return redirect(book.get_absolute_url())
    cart = _get_cart(request.session)
    current_qty = int(cart.get(slug, 0))
    if current_qty >= book.stock:
        messages.info(request, f"You already have the maximum available quantity ({book.stock}) of this title in your cart.")
    else:
        new_qty = current_qty + 1
        if new_qty > book.stock:
            new_qty = book.stock
        cart[slug] = new_qty
        messages.success(request, f"Added to cart: {book.title} (x{new_qty}).")
    request.session.modified = True
    return redirect("orders:cart")


def remove_from_cart(request, slug):
    cart = _get_cart(request.session)
    if slug in cart:
        del cart[slug]
        request.session.modified = True
        messages.info(request, "Item removed from cart.")
    return redirect("orders:cart")


def decrease_quantity(request, slug):
    cart = _get_cart(request.session)
    if slug in cart:
        new_qty = int(cart[slug]) - 1
        if new_qty <= 0:
            del cart[slug]
            messages.info(request, "Item removed from cart.")
        else:
            cart[slug] = new_qty
            messages.info(request, f"Updated quantity to {new_qty}.")
        request.session.modified = True
    return redirect("orders:cart")


def clear_cart(request):
    request.session["cart"] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect("orders:cart")


class CheckoutView(View):
    template_name = "orders/checkout.html"

    def get(self, request):
        cart = _get_cart(request.session)
        if not cart:
            messages.info(request, "Your cart is empty.")
            return redirect("orders:cart")
        methods = ShippingMethod.objects.filter(is_active=True).order_by("fee")
        if not methods.exists():
            messages.error(request, "No delivery methods configured. Please contact the shop.")
        # compute subtotal
        subtotal = Decimal("0.00")
        books = Book.objects.filter(slug__in=cart.keys())
        for b in books:
            subtotal += Decimal(b.price) * cart.get(b.slug, 0)
        default_fee = Decimal(str(methods.first().fee)) if methods.exists() else Decimal("0.00")
        return render(request, self.template_name, {
            "shipping_methods": methods,
            "subtotal": subtotal,
            "subtotal_plus_shipping": subtotal + default_fee,
            "default_shipping_fee": default_fee,
        })

    def post(self, request):
        cart = _get_cart(request.session)
        if not cart:
            messages.info(request, "Your cart is empty.")
            return redirect("orders:cart")
        try:
            method_id = int(request.POST.get("shipping_method"))
            method = ShippingMethod.objects.get(pk=method_id, is_active=True)
        except (TypeError, ValueError, ShippingMethod.DoesNotExist):
            messages.error(request, "Please select a valid delivery option.")
            return redirect("orders:checkout")

        # collect form fields
        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        address_line1 = request.POST.get("address_line1", "").strip()
        address_line2 = request.POST.get("address_line2", "").strip()
        city = request.POST.get("city", "").strip()
        region = request.POST.get("region", "").strip()
        notes = request.POST.get("notes", "").strip()
        if not (full_name and email and phone and address_line1 and city and region):
            messages.error(request, "Please complete the required fields.")
            return redirect("orders:checkout")

        # compute totals
        subtotal = Decimal("0.00")
        books = Book.objects.filter(slug__in=cart.keys())
        book_map = {b.slug: b for b in books}
        for slug, qty in cart.items():
            b = book_map.get(slug)
            if not b:
                continue
            subtotal += Decimal(b.price) * int(qty)
        shipping_fee = Decimal(method.fee)
        total = subtotal + shipping_fee

        # create order
        ts = datetime.datetime.now().strftime("%y%m%d%H%M%S")
        order_number = f"TB{ts}"
        order = Order.objects.create(
            order_number=order_number,
            user=request.user if request.user.is_authenticated else None,
            email=email,
            full_name=full_name,
            phone=phone,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            region=region,
            notes=notes,
            shipping_method=method,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
        )

        # create items and adjust stock
        for slug, qty in cart.items():
            b = book_map.get(slug)
            if not b:
                continue
            qty = int(qty)
            OrderItem.objects.create(
                order=order,
                book=b,
                title=b.title,
                unit_price=b.price,
                quantity=qty,
                line_total=Decimal(b.price) * qty,
            )
            if b.stock >= qty:
                b.stock -= qty
                b.save(update_fields=["stock"])

        # payment selection
        pay_method = request.POST.get("payment_method", "momo")  # default momo
        if pay_method == "cod":
            # Cash on Delivery: consider order placed without payment now
            Payment.objects.create(order=order, method="cod", provider="cod", status="authorized", amount=order.total)
            # clear cart
            request.session["cart"] = {}
            request.session.modified = True
            # notifications
            send_order_email(order, subject_prefix="Order Placed (COD)")
            send_sms(order.phone, f"TBSS: Order {order.order_number} placed. Pay on delivery. Total GH₵ {order.total}.")
            return redirect(reverse("orders:success", kwargs={"order_number": order.order_number}))
        else:
            # Start Mobile Money payment
            Payment.objects.create(order=order, method="momo", provider="mtn-voda-at", status="pending", amount=order.total)
            return redirect(reverse("payments:momo_start", kwargs={"order_number": order.order_number}))


class OrderSuccessView(TemplateView):
    template_name = "orders/success.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["order_number"] = self.kwargs.get("order_number")
        return ctx

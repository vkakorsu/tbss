def cart_count(request):
    """Expose total quantity of items in the session cart as cart_count."""
    cart = request.session.get("cart", {}) or {}
    try:
        total = sum(int(qty) for qty in cart.values())
    except (TypeError, ValueError):
        total = 0
    return {"cart_count": total}

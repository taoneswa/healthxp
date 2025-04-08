from .models import ShoppingCart


def cart_processor(request):
    """
    Context processor that adds shopping cart data to all template contexts
    """
    context = {}

    if request.user.is_authenticated:
        # Get or set default values for cart
        try:
            cart = ShoppingCart.objects.get(user=request.user)
            context['user_cart'] = cart
            context['cart_item_count'] = cart.total_items
        except ShoppingCart.DoesNotExist:
            context['cart_item_count'] = 0

    return context

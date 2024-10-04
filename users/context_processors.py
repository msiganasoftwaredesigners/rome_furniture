#users/context_processors.py

def liked_products(request):
    if request.user.is_authenticated:
        liked_products = request.user.liked_products.all()
    else:
        liked_products = []
    return {'liked_products': liked_products}
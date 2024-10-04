#store/context_processors.py
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from .models import Product
from django.db.models import Count, Q
from django.core.exceptions import ObjectDoesNotExist
import logging


def most_liked_products(request):
    try:
        # Try to fetch the most liked products from cache
        most_liked_products = cache.get('most_liked_products')

        # If the most liked products are not in cache or cache is stale, recalculate them
        if most_liked_products is None:
            # Get the date 90 days ago
            ninety_days_ago = timezone.now() - timedelta(days=90)

            # Get the most liked products in the last 90 days
            most_liked_products = Product.objects.filter(
                product_modified_date__gte=ninety_days_ago
            ).annotate(
                likes_count=Count('likes')
            ).order_by('-likes_count')[:80]

            # Store the most liked products in cache for 3 days
            cache.set('most_liked_products', most_liked_products, 60*60*0)
        else:
            # Check if the products in cache still exist in the database
            updated_products = []
            for product in most_liked_products:
                try:
                    Product.objects.get(id=product.id)
                    updated_products.append(product)
                except ObjectDoesNotExist:
                    pass  # Product no longer exists, skip

            most_liked_products = updated_products

    except Exception as e:
        # Handle exceptions gracefully, log the error, and provide a fallback response
        logging.error(f"Error fetching most liked products: {e}")
        most_liked_products = []

    return {'most_liked_products': most_liked_products}

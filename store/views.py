from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from category.models import Category
from store.models import Product,Like
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .context_processors import most_liked_products
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import  SizeVariation
from django.views.decorators.csrf import csrf_exempt
import uuid
import logging
from django.db.models import Avg
from .models import ProductRating
from django.http import JsonResponse
from django.db.models import Q
from django.core.cache import cache
from django.db.models import Min
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Min, Max


logger = logging.getLogger(__name__)


def store(request, category_slug=None):
    categories = None
    products = None
    template = 'store.html'

    if category_slug != None:
        categories = get_object_or_404(Category, category_slug=category_slug)
        products = Product.objects.filter(category=categories, product_is_available=True).select_related('category').prefetch_related('images').order_by('-product_modified_date')
        template = 'store.html'
    else:
        products = cache.get('latest_products')
        if not products:
            products = Product.objects.filter(product_is_available=True).prefetch_related('images').order_by('-product_modified_date')[:30]
            cache.set('latest_products', products, 60*60*0)  


    most_liked_products_with_count = most_liked_products(request)['most_liked_products']
    
    paginator = Paginator(products, 30)
    page = request.GET.get('page')

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"end": True}, status=404)  
        products_page = paginator.page(1)
    except EmptyPage:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"end": True}, status=404)  
        products_page = paginator.page(paginator.num_pages)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = {"products": list(products_page), "end": False}
        return JsonResponse(data, safe=False)

    # Your existing code
    for product in products:
        product.average_rating = product.average_rating()
        product.review_count = product.review_count()
    most_liked_product = most_liked_products_with_count[0] if most_liked_products_with_count else None
    return render(request, template, {'products': products_page, 'most_liked_product': most_liked_product})

def product_detail(request, category_slug, product_slug):
    print("product_detail view was called")
    try:
        single_product = cache.get(f'product_{product_slug}')
        if not single_product:
            single_product = get_object_or_404(Product, category__category_slug=category_slug, product_slug=product_slug)
        single_product.increment_views()
        # single_product = get_object_or_404(Product, category__category_slug=category_slug, product_slug=product_slug)
        # single_product.increment_views()
        reviews_count = single_product.review_count()
        if request.META.get('HTTP_X_MOZ') == 'prefetch':
            return HttpResponse('No prefetch', status=200)

        main_image = single_product.images.filter(is_main=True).first()
        other_images = single_product.images.all()
        related_products = Product.objects.filter(category=single_product.category).exclude(id=single_product.id).order_by('-product_created_date')[:80]
        size_variations = single_product.sizevariation_set.all()
        color_variations = [size_variation.color for size_variation in size_variations if size_variation.color]
        is_owner = request.user == single_product.product_owner
        # like Implementation
        product_slug = single_product.product_slug
        print("product_slug:", product_slug)
        
        liked = False
        if request.user.is_authenticated:
            liked = Like.objects.filter(product=single_product, liked_by=request.user).exists()

        user_rating = None
        if request.user.is_authenticated:
            user_rating = ProductRating.objects.filter(user=request.user, product=single_product).first()
            if user_rating:
                user_rating = user_rating.rating

        average_rating = ProductRating.objects.filter(product=single_product).aggregate(Avg('rating'))['rating__avg']
    except Exception as e:
        raise e
    
    context = {
        'single_product': single_product,
        'main_image': main_image,
        'other_images': other_images,
        'related_products': related_products,
        'color_variations': color_variations,
        'size_variations': size_variations,
        'liked': liked,
        'is_owner': is_owner,
        'user_rating': user_rating,
        'average_rating': average_rating,
        'reviews_count': reviews_count,
    }
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # If the request is an AJAX request, return the product details as JSON
        size_variations = [size_variation.size for size_variation in size_variations]
        color_variations = [color_variation.name for color_variation in color_variations]
        return JsonResponse({
            'liked': liked,
            'sizes': size_variations,
            'colors': color_variations,
            'price': single_product.price,
        })
    
    return render(request, 'product-detail.html', context)


def filter_products(request):
    if request.method == 'GET':
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)
        category_name = request.GET.get('category', None)

        queryset = Product.objects.all() if min_price or max_price or category_name else Product.objects.none()

        min_variation_price = SizeVariation.objects.aggregate(Min('price'))['price__min']
        max_variation_price = SizeVariation.objects.aggregate(Max('price'))['price__max']

        filters = {'product_is_available': True}

        if min_price:
            min_price = max(float(min_price), min_variation_price)  
            filters['sizevariation__price__gte'] = min_price
        if max_price:
            max_price = min(float(max_price), max_variation_price)  
            filters['sizevariation__price__lte'] = max_price
        if category_name and category_name.strip() != '':
            filters['category__category_name'] = category_name

        queryset = queryset.filter(**filters)

        if min_price is None and max_price is None and (category_name is None or category_name.strip() == ''):
            message = 'Please apply some filters.'
        else:
            message = ''

        return render(request, 'filter_template.html', {'products': queryset, 'message': message})
    else:
        return render(request, 'filter_template.html', {'products': queryset})
@csrf_exempt
def rate_product(request, product_slug):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        product = get_object_or_404(Product, product_slug=product_slug)
        rating = request.POST.get('rating')
        ProductRating.objects.update_or_create(user=request.user, product=product, defaults={'rating': rating})
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
@csrf_exempt
def get_price_and_colors(request):
    size_variation_id = request.GET.get('size_variation_id')
    if size_variation_id is not None:
        try:
            size_variation = SizeVariation.objects.get(id=size_variation_id)
            price = size_variation.price
            colors = [color.name for color in size_variation.color.all()]
            
            return JsonResponse({'price': price, 'colors': colors})
        except SizeVariation.DoesNotExist:
            return JsonResponse({'error': f'Variation with id {size_variation_id} does not exist'}, status=400)
    else:
        logger.error('Invalid request')
        return JsonResponse({'error': 'Invalid request'}, status=400)


def increment_view_count(request, product_slug):
    product = get_object_or_404(Product, product_slug=product_slug)
    product.increment_views()
    return JsonResponse({'product_views_count': product.product_views_count})


@login_required
def like_product(request, product_slug):
    product = get_object_or_404(Product, product_slug=product_slug)
    user = request.user

    if request.method == "POST":
        if product.product_likes.filter(liked_by=user).exists():
            Like.objects.filter(product=product, liked_by=user).delete()
            liked = False  
        else:
            Like.objects.create(product=product, liked_by=user)
            liked = True  

        product.product_likes_count = product.product_likes.count()
        product.save()

        response_data = {
            "liked": liked,
            "likes_count": product.product_likes_count,
        }

        return JsonResponse(response_data)

    return redirect("product-detail", category_slug=product.category.category_slug, product_slug=product_slug)

def search(request):
    context = {}
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('product_created_date').filter(
                Q(product_description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
            context = {
                'products': products,
                'product_count': product_count
            }

    return render(request, 'store.html', context)


def checkout(request):
    return render(request, 'checkout.html')

def order_complete(request):
    return render(request, 'order-complete.html')
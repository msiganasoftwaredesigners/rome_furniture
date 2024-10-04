# models.py
from django.db import models
from django.urls import reverse
from category.models import Category
from django.core.exceptions import ValidationError
from decimal import Decimal
from PIL import Image  
from django.core.files.base import ContentFile
from io import BytesIO 
import os
from django_quill.fields import QuillField
from users.models import CustomUser
from django.db.models import Avg
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


class Size(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Color(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    product_name = models.CharField(max_length=150, unique=True)
    product_brand = models.CharField(max_length=150, blank=True,default='Custom')
    product_slug = models.SlugField(max_length=150, unique=True)
    product_description = QuillField()
    product_stock = models.IntegerField(blank=True, null=True)
    product_is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_created_date = models.DateTimeField(auto_now_add=True)
    product_modified_date = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(CustomUser, through="Like", related_name="liked_products")
    product_views_count = models.PositiveIntegerField(default=0)
    product_phone = models.CharField(max_length=15, blank=True, null=True)
    product_owner = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='owned_products', default=1)
     
    @property
    def default_price(self):
        size_variations = SizeVariation.objects.filter(product=self).order_by('id')
        if size_variations.exists():
            return size_variations.first().price
        else:
            return None
    
    def increment_views(self):
        print("increment_views was called on product with slug:", self.product_slug)
        self.product_views_count += 1
        self.save()
        print("product_views_count after incrementing:", self.product_views_count)
    
    def save(self, *args, **kwargs):
        print("Product is being saved. Current views count is", self.product_views_count)
        super().save(*args, **kwargs)

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        if Product.objects.filter(product_name=self.product_name).exclude(id=self.id).exists():
            raise ValidationError({'product_name': ('Product with this name already exists.')})
        
    def get_store_url(self):
        if self.category and self.category.category_slug and self.product_slug:
            return reverse('product_detail', args=[self.category.category_slug, self.product_slug])
        else:
            return "#"

    def get_short_name(self):
        return self.product_name[:16]

    def get_main_image(self):
        main_image = self.images.filter(is_main=True).first()
        return main_image
    
    
    def likes_count(self):
        return self.likes.count()
    def average_rating(self):
        """Return the average rating for this product."""
        return ProductRating.objects.filter(product=self).aggregate(Avg('rating'))['rating__avg'] or 0
    
    def review_count(self):
        return ProductRating.objects.filter(product=self).count()
    
    def __str__(self):
        return self.product_name 
    

class ProductRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('user', 'product',)
    

class Like(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_likes")
    liked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  
        self.product.product_likes_count = self.product.product_likes.count()
        self.product.save()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs) 
        product.product_likes_count = product.product_likes.count()
        product.save()

    def __str__(self):
        return f"{self.liked_by} liked {self.product.product_name}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images')
    is_main = models.BooleanField(default=False)
    
    def clean(self):
        super().clean()

    def save(self, *args, **kwargs):
        try:
           this = ProductImage.objects.get(id=self.id)
           if this.image != self.image:
               this.image.delete(save=False)
        except: pass 

        if self.image:
            img = Image.open(self.image)

            target_size_kb = 750
            target_size_bytes = target_size_kb * 1024

            output = BytesIO()
            img_format = img.format
            quality = 85  
            while True:
                img.save(output, format=img_format, quality=quality)
                output_size = output.tell()

                if output_size <= target_size_bytes or quality <= 0:
                    break  

                quality -= 5

                output.seek(0)
                output.truncate()

            output.seek(0)

            self.image = ContentFile(output.read(), self.image.name)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        try:
            self.image.delete(save=False)
        except PermissionError:
            print("Permission denied: Unable to delete the image file.")
        except Exception as e:
            print(f"Unexpected error occurred while deleting the image file: {e}")
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return self.product.product_name + " Image"
    

@receiver(post_delete, sender=ProductImage)
def delete_product_image(sender, instance, **kwargs):
    """Delete the actual image file when a ProductImage object is deleted."""
    instance.image.delete(save=False)


@receiver(pre_save, sender=ProductImage)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Delete the old image file when a ProductImage object is updated."""
    if instance.pk:
        old_image = ProductImage.objects.get(pk=instance.pk).image
        new_image = instance.image
        if old_image != new_image:
            old_image.delete(save=False)


class SizeVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=7, decimal_places=2,default=0.00)
    color = models.ManyToManyField(Color, blank=True) 

    def clean(self):
        if not isinstance(self.price, Decimal):
            raise ValidationError("Please insert number only.")
        if self.price < 1:
            raise ValidationError("Price should be greater than or equal to 1.")
        if self.price >= Decimal('1000000.00'):
            raise ValidationError("Please insert less than 999999.99.")

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = not self.pk  
        super().save(*args, **kwargs)

        if is_new:
            default_color = Color.objects.get_or_create(name='White')[0]
            self.color.add(default_color)

    def __str__(self):
        colors = "Unknown"
        if self.id:
            try:
                colors = ', '.join([color.name for color in self.color.all()])
            except Exception as e:
                print(f"Exception occurred while accessing colors: {e}")
        return f"{self.product.product_name} - {colors} - {self.size.name} - {self.price}" 
    # def __str__(self):
    #     print("Inside __str__ method of SizeVariation")
    #     return f"{self.product.product_name} - {', '.join([color.name for color in self.color.all()])} - {self.size.name} - {self.price}" 
  
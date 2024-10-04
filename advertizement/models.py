from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver



class Favicon(models.Model):
    favicon_image = models.ImageField(upload_to='images/favicon', blank=True, null=True)
   
    def save(self, *args, **kwargs):
        try:
            this = Favicon.objects.get(id=self.id)
            if this.favicon_image != self.favicon_image:
                this.favicon_image.delete(save=False)
        except: pass 

        if not self.pk and Favicon.objects.exists():
            raise ValidationError('There is can be only one Favicon instance')
       
        if self.favicon_image:
            img = Image.open(self.favicon_image)
            output = BytesIO()

          
            img_format = img.format
            img.save(output, format=img_format, quality=75)
            output.seek(0)
            self.favicon_image = ContentFile(output.read(), self.favicon_image.name)

        return super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        self.favicon_image.delete(save=False)
        super().delete(*args, **kwargs)

@receiver(post_delete, sender=Favicon)
def delete_favicon_image(sender, instance, **kwargs):
    """Delete the actual image file when an Favicon object is deleted."""
    instance.favicon_image.delete(save=False)

@receiver(pre_save, sender=Favicon)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Delete the old image file when an Favicon object is updated."""
    if instance.pk:
        old_image = Favicon.objects.get(pk=instance.pk).favicon_image
        new_image = instance.favicon_image
        if old_image and new_image and old_image != new_image:
            old_image.delete(save=False)
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Footer(models.Model):
    nav_company_logo = models.ImageField(upload_to='images/contacts', blank=True, null=True)
    footer_company_logo = models.ImageField(upload_to='images/contacts', blank=True, null=True)
    main_page_image = models.ImageField(upload_to='images/contacts', blank=True, null=True)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    company_main_page_title = models.TextField(max_length=100, blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            # is the object in the database yet?
            this = Footer.objects.get(id=self.id)
            if this.nav_company_logo != self.nav_company_logo:
                this.nav_company_logo.delete(save=False)
            if this.footer_company_logo != self.footer_company_logo:
                this.footer_company_logo.delete(save=False)
            if this.main_page_image != self.main_page_image:
                this.main_page_image.delete(save=False)
        except: pass # when new photo then we do nothing, normal case

        if not self.pk and Footer.objects.exists():
            raise ValidationError('There is can be only one Footer instance')

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.nav_company_logo.delete(save=False)
        self.footer_company_logo.delete(save=False)
        self.main_page_image.delete(save=False)
        super().delete(*args, **kwargs)

@receiver(post_delete, sender=Footer)
def delete_footer_images(sender, instance, **kwargs):
    """Delete the actual image files when a Footer object is deleted."""
    instance.nav_company_logo.delete(save=False)
    instance.footer_company_logo.delete(save=False)
    instance.main_page_image.delete(save=False)
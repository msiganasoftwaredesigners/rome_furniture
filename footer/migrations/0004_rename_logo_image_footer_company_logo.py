# Generated by Django 5.0.1 on 2024-01-26 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('footer', '0003_rename_contact_footer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='footer',
            old_name='logo_image',
            new_name='company_logo',
        ),
    ]
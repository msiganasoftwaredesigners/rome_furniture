# Generated by Django 5.0.1 on 2024-03-09 21:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_sizevariation_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='sizevariation',
            name='color',
            field=models.ManyToManyField(blank=True, to='store.color'),
        ),
        migrations.DeleteModel(
            name='Variation',
        ),
    ]
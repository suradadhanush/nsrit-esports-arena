"""
Migration: Add retry_count and failure_reason to Payment model.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='retry_count',
            field=models.IntegerField(default=0, help_text='Number of payment attempts'),
        ),
        migrations.AddField(
            model_name='payment',
            name='failure_reason',
            field=models.TextField(blank=True, help_text='Razorpay failure description if failed'),
        ),
    ]

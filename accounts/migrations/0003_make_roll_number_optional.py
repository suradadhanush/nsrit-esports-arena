"""
Migration: make roll_number nullable and blank so registration works without it.
USERNAME_FIELD changed to email in models.py.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_nsrituser_account_locked_until_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nsrituser',
            name='roll_number',
            field=models.CharField(
                blank=True,
                max_length=20,
                null=True,
                unique=True,
                verbose_name='Roll Number (optional)',
            ),
        ),
    ]

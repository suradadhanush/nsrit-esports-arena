from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='payment_method',
            field=models.CharField(
                max_length=20,
                choices=[('RAZORPAY', 'Razorpay'), ('UPI', 'UPI')],
                default='UPI'
            ),
        ),
        migrations.AddField(
            model_name='registration',
            name='payment_status',
            field=models.CharField(
                max_length=20,
                choices=[('PENDING', 'Pending'), ('SUCCESS', 'Success'), ('FAILED', 'Failed')],
                default='PENDING'
            ),
        ),
        migrations.AddField(
            model_name='registration',
            name='transaction_id',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='registration',
            name='payment_proof',
            field=models.ImageField(upload_to='payment_proofs/', blank=True, null=True),
        ),
    ]
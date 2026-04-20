from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0002_registration_payment_fields'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE registrations ADD COLUMN IF NOT EXISTS notes TEXT NOT NULL DEFAULT '';",
            reverse_sql="ALTER TABLE registrations DROP COLUMN IF EXISTS notes;",
        ),
    ]

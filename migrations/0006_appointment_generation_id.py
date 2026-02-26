# Generated manually for add_to_class field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("p_totschool_appointment_tracker", "0005_alter_appointment_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="generation_id",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

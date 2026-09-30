from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="invoiceitem",
            name="invoice",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="items",
                to="billing.invoice",
            ),
        ),
    ]

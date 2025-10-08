# Generated migration for adding bank guarantee fields to LetterOfAward

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TenderManagement', '0008_alter_securitydeposit_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='letterofaward',
            name='bank_guarantee_required',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='letterofaward',
            name='bank_guarantee_percentage',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True),
        ),
    ]
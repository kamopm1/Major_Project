# Generated by Django 3.2 on 2024-12-22 09:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_more_evidance_send_case'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='more_evidance',
            name='lawyer_id',
        ),
        migrations.AddField(
            model_name='more_evidance',
            name='police_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.police_detail'),
        ),
    ]

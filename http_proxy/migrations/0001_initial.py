# Generated by Django 3.2.5 on 2021-07-11 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProPublicaRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('exceeds_limit', models.BooleanField()),
                ('executed_on', models.DateTimeField(null=True)),
                ('http_code', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RequestMonitor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_model', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('daily_count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddIndex(
            model_name='requestmonitor',
            index=models.Index(fields=['request_model', '-date'], name='http_proxy__request_de8994_idx'),
        ),
        migrations.AddConstraint(
            model_name='requestmonitor',
            constraint=models.UniqueConstraint(fields=('request_model', 'date'), name='daily_unique_request_model'),
        ),
    ]
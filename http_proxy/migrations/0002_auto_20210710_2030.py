# Generated by Django 3.2.5 on 2021-07-11 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('http_proxy', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='propublicarequest',
            old_name='url',
            new_name='endpoint',
        ),
        migrations.RenameField(
            model_name='propublicarequest',
            old_name='exceeds_limit',
            new_name='granted',
        ),
        migrations.RenameField(
            model_name='propublicarequest',
            old_name='executed_on',
            new_name='sent_on',
        ),
        migrations.RenameField(
            model_name='requestmonitor',
            old_name='daily_count',
            new_name='grant_count',
        ),
        migrations.AddField(
            model_name='propublicarequest',
            name='http_method',
            field=models.CharField(choices=[('GET', 'Get')], default='GET', max_length=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='requestmonitor',
            name='sent_count',
            field=models.IntegerField(default=0),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-09 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='path',
            name='path_id',
            field=models.CharField(max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='auth_write',
            field=models.BooleanField(default=False),
        ),
    ]
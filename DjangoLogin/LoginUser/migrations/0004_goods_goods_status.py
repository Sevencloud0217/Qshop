# Generated by Django 2.2.1 on 2019-09-20 03:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LoginUser', '0003_goods'),
    ]

    operations = [
        migrations.AddField(
            model_name='goods',
            name='goods_status',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]

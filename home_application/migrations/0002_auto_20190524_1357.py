# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='script_result',
            field=models.CharField(default=b'', max_length=2000),
        ),
        migrations.AlterField(
            model_name='script',
            name='when_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]

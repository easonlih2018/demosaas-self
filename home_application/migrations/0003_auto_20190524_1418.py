# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0002_auto_20190524_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostScriptResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('host_id', models.IntegerField()),
                ('script_id', models.IntegerField()),
                ('execute_result', models.CharField(max_length=2000)),
            ],
        ),
        migrations.RemoveField(
            model_name='script',
            name='script_result',
        ),
    ]

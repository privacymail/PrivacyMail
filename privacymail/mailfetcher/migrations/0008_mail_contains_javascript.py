# Generated by Django 2.1.7 on 2019-04-02 16:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailfetcher', '0007_auto_20190402_0727'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='contains_javascript',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 3.2.10 on 2021-12-10 22:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0005_auto_20211207_1729'),
    ]

    operations = [
        migrations.RenameField(
            model_name='package',
            old_name='Data',
            new_name='data',
        ),
        migrations.RenameField(
            model_name='package',
            old_name='Metadata',
            new_name='metadata',
        ),
    ]
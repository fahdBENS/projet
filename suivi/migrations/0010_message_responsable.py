# Generated by Django 5.0.7 on 2024-07-25 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suivi', '0009_alter_message_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='responsable',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
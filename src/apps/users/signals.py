from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import User, Profile


@receiver(pre_save, sender=User)
def normalize_email(sender, instance, **kwargs):
    if instance.email:
        instance.email = instance.email.lower().strip()

@receiver(post_save, sender=User)
def create_user_post(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.create(
            user=instance
        )
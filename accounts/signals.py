from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, Wishlist

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_wishlist(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)
        Wishlist.objects.get_or_create(user=instance)

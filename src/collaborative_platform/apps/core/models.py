from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    agree_to_terms = models.BooleanField(default=True)
    is_scientist = models.BooleanField(default=False)
    orcid = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    github = models.CharField(max_length=255, null=True, blank=True)
    scholar = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    about = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return "{0} {1} ({2})".format(self.user.first_name, self.user.last_name, self.user.username)


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

    instance.profile.save()

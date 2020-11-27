from django.db import models

class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()


from django.utils.translation import ugettext_lazy as _

class Report(models.Model):
    bucket = models.CharField(verbose_name=('S3 Bucket'), max_length=255)
    path = models.FileField(verbose_name=('S3 path'))
    s3_src = models.CharField(verbose_name=('S3 Link'), max_length=255)

    # @property
    # def s3_url(self):
    #     return "s3://%s/%s" % (self.bucket, self.path.name)
    class Meta:
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ('-id',)


from django.utils import timezone


def user_directory_path(instance, filename):
    return 'posts/{0}/{1}'.format(instance.id, filename)


class Post(models.Model):

    title = models.CharField(max_length=250)
    image = models.ImageField(
        upload_to=user_directory_path)
    image_caption = models.CharField(
        max_length=100, default='Photo by demo')
    publish = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
from __future__ import unicode_literals

from django.db import models
from django.contrib.sessions.models import Session
from PIL import Image
from django.core.files.storage import default_storage as storage
from django.core.files.base import ContentFile
import os
from cStringIO import StringIO

# Create your models here.
class Flare(models.Model):
    name = models.CharField(max_length=30, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    password = models.CharField(max_length=30)

class Joker(models.Model):
    name = models.CharField(max_length=30)
    flare = models.ForeignKey(Flare)
    joined_on = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now_add=True)

class TextMessage(models.Model):
    text = models.CharField(max_length=140)
    timestamp = models.DateTimeField(auto_now_add=True)
    joker = models.ForeignKey(Joker)

class FileMessage(models.Model):
    title = models.CharField(max_length=100)
    file = models.FileField(upload_to='others')
    timestamp = models.DateTimeField(auto_now_add=True)
    joker = models.ForeignKey(Joker)
    size = models.BigIntegerField(editable=False)

    def save(self, *args, **kwargs):
        self.size = self.file.size
        super(FileMessage, self).save(*args, **kwargs)

class ImageMessage(models.Model):
    image = models.ImageField(upload_to='images')
    thumbnail = models.ImageField(upload_to='thumbnails',
                                  editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    joker = models.ForeignKey(Joker)
    title = models.CharField(max_length=100)
    size = models.BigIntegerField(editable=False)

    def save(self, *args, **kwargs):
        self.size = self.image.size
        super(ImageMessage, self).save(*args, **kwargs)
        print 'Saving Super!'
        if not hasattr(self, 'just_saved'):
            self.just_saved = False
        if self.just_saved:
            self.just_saved = False
            return
        else:
            self.just_saved = True
        print 'Saving !'
        # since 'thumbnail' is editable, it is not saved by super
        if not self.make_thumbnail():
            raise Exception('Could not create thumbnail')


    def make_thumbnail(self):
        """
        Make and save the thumbnail for the image.
        :return True if successfully saved, False otherwise.
        """
        # http://stackoverflow.com/a/23927211
        fh = storage.open(self.image.name, 'rb')
        try:
            image = Image.open(fh)
        except Exception as ex:
            print 'Unable to open file ' + str(ex)
            return False
        print 'Making thumbnail'
        image.thumbnail((500, 200), Image.ANTIALIAS)
        fh.close()

        thumb_name, thumb_extension = os.path.splitext(self.image.name)
        thumb_extension = thumb_extension.lower()
        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE='JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False

        temp_thumb = StringIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        self.thumbnail.save(name=thumb_filename, content=ContentFile(temp_thumb.read()), save=True)
        print 'Reached here !'
        temp_thumb.close()

        return True

    def delete(self, using=None, keep_parents=False):
        return super(ImageMessage, self).delete(using, keep_parents)

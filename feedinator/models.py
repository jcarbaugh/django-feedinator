import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from pytz import common_timezones

FEED_TYPE_CHOICES = (
    (u'rss', u'RSS'),
    (u'rss-0.90',  u'RSS 0.90'),
    (u'rss-0.91', u'RSS 0.91'),
    (u'rss-1.0', u'RSS 1.0'),
    (u'rss-2.0', u'RSS 2.0 by Dave Winer'),
    (u'rss-2.0.10', u'RSS 2.0 by RSS Advisory Board'),
    (u'atom', u'Atom'),
    (u'atom-0.3', u'Atom 0.3'),
    (u'atom-1.0', u'Atom 1.0'),
)

TIMEZONE_CHOICES = [(tz, tz) for tz in common_timezones]


class Feed(models.Model):
    url = models.URLField()
    codename = models.CharField(max_length=128, blank=True)
    type = models.CharField(max_length=16, choices=FEED_TYPE_CHOICES, blank=True, null=True)
    title = models.CharField(max_length=225)
    link = models.URLField(blank=True)
    timezone = models.CharField(max_length=32, choices=TIMEZONE_CHOICES, default='UTC')
    description = models.TextField(blank=True)
    ttl = models.IntegerField(default=60)
    date_added = models.DateTimeField(auto_now_add=True)
    last_fetched = models.DateTimeField(blank=True, null=True)
    next_fetch = models.DateTimeField()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.last_fetched:
            self.last_fetched = datetime.datetime.now()
            self.next_fetch = self.last_fetched
        else:
            self.next_fetch = self.last_fetched + datetime.timedelta(0, 0, 0, 0, self.ttl)
        super(Feed, self).save(*args, **kwargs)


class Subscription(models.Model):
    feed = models.ForeignKey(Feed, related_name='subscriptions')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    subscriber = generic.GenericForeignKey()

    def __unicode__(self):
        return '%s to %s' % (self.subscriber, self.feed)


class FeedEntryManager(models.Manager):
    pass


class FeedEntry(models.Model):
    objects = FeedEntryManager()
    uid = models.CharField(max_length=255)
    feed = models.ForeignKey(Feed, related_name="entries")
    title = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    author_name = models.CharField(max_length=255, blank=True)
    author_email = models.EmailField(blank=True, null=True)
    author_uri = models.URLField(blank=True, null=True)
    date_published = models.DateTimeField(blank=True, null=True)
    date_updated = models.DateTimeField(blank=True, null=True)
    last_fetched = models.DateTimeField()

    class Meta:
        ordering = ['-date_published']

    def __unicode__(self):
        return u"%s: %s" % (self.feed.title, self.title)


class Tag(models.Model):
    name = models.CharField(max_length=128)
    feed_entry = models.ForeignKey(FeedEntry, related_name="tags")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name

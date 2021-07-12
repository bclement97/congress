import urllib.parse

import logging
import requests

from django.db import models
from django.db.models import F
from django.utils import timezone


logger = logging.getLogger('http_proxy.models')


class DailyRequestMonitor(models.Model):
    request_model = models.CharField(max_length=255)
    date = models.DateField()
    grant_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['request_model', 'date'],
                                    name='daily_unique_request_model'),
        ]
        indexes = [
            models.Index(fields=['request_model', '-date']),
        ]

    def grant(self):
        self.grant_count = F('grant_count') + 1
        self.save()
        self.refresh_from_db()
        logger.debug('{} granted (count: {})'.format(
            self.request_model,
            self.grant_count,
        ))

    def revoke_grant(self):
        self.grant_count = F('grant_count') - 1
        self.save()
        self.refresh_from_db()
        logger.debug('{} revoked (count: {})'.format(
            self.request_model,
            self.grant_count,
        ))

    def request_sent(self):
        self.sent_count = F('sent_count') + 1
        self.save()
        self.refresh_from_db()
        logger.debug('{} sent ({}/{})'.format(
            self.request_model,
            self.sent_count,
            self.grant_count,
        ))

    def __str__(self):
        return f'{self.request_model} {self.date:%m/%d/%Y}'


# RequestLimiter(limit: int)?
class DailyRequestManager(models.Manager):
    STOLEN_GRANT_THRESHOLD = 0

    def request_grant(self):
        monitor = self._monitor()
        if monitor.sent_count >= self.model.DAILY_LIMIT:
            return False
        monitor.grant()
        if monitor.grant_count <= self.model.DAILY_LIMIT:
            return True
        monitor.revoke_grant()
        return False

    def steal_grant(self):
        monitor = self._monitor()
        monitor.grant()
        if monitor.grant_count > DailyRequestManager.STOLEN_GRANT_THRESHOLD:
            logger.warning('Grant stolen over threshold ({}/{})'.format(
                monitor.grant_count,
                DailyRequestManager.STOLEN_GRANT_THRESHOLD,
            ))
        return monitor.grant_count <= self.model.DAILY_LIMIT

    def request_sent(self):
        self._monitor().request_sent()

    def _monitor(self):
        monitor, _ = DailyRequestMonitor.objects.get_or_create(
            request_model=self.model._meta.model_name,
            date=timezone.now(),
        )
        return monitor


class ProPublicaRequest(models.Model):
    VERSION = 1
    BASE_URL = f'https://api.propublica.org/congress/{VERSION}/'
    DAILY_LIMIT = 5000

    class HttpMethod(models.TextChoices):
        GET = 'GET'

    http_method = models.CharField(max_length=7, choices=HttpMethod.choices)
    endpoint = models.URLField()
    granted = models.BooleanField()
    created_on = models.DateTimeField(auto_now_add=True)
    sent_on = models.DateTimeField(null=True)
    http_code = models.IntegerField(null=True)

    objects = DailyRequestManager()

    @classmethod
    def get(cls, endpoint):
        request = cls._create(cls.HttpMethod.GET, endpoint)
        return request._send()

    @classmethod
    def _create(cls, http_method, endpoint):
        request = cls(http_method=http_method, endpoint=endpoint,
                      granted=cls.objects.request_grant())
        request.save()
        return request

    def _send(self):
        if not self.granted:
            return
        now = timezone.now()
        logger.info(self)
        # TODO: make request
        # url = urllib.parse.urljoin(ProPublicaRequest.BASE_URL, self.endpoint)
        # response = requests.request(self.http_method, url)
        self.sent_on = now
        self.http_code = 200
        # Request was created and sent around midnight.
        if self.sent_on.date() != self.created_on.date():
            # Stealing a grant is safe because it is very unlikely the limit's
            # been reached just after midnight. Even if it's not, it's best to
            # have a correct grant_count for diagnostics.
            #
            # If for some reason the stolen grant isn't valid (exceeds the
            # daily limit), self.granted is set to False even though
            # self.sent_on has a value. This allows filtering for these
            # requests.
            self.granted = ProPublicaRequest.objects.steal_grant()
        ProPublicaRequest.objects.request_sent()
        self.save()
        return self.http_code  # placeholder for the full response

    def __str__(self):
        return f'{self.http_method} {self.endpoint}'

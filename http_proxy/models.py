import logging
import requests

from django.db import models, transaction
from django.db.models import F
from django.utils import timezone


logger = logging.getLogger(__name__)


class RequestMonitor(models.Model):
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
        logger.debug('{} granted (count: {})'.format(self.request_model,
                                                     self.grant_count))

    def revoke_grant(self):
        self.grant_count = F('grant_count') - 1
        self.save()
        self.refresh_from_db()
        logger.debug('{} revoked (count: {})'.format(self.request_model,
                                                     self.grant_count))

    def request_sent(self):
        self.sent_count = F('sent_count') + 1
        self.save()
        self.refresh_from_db()
        msg = '{} sent ({}/{})'.format(self.request_model, self.sent_count,
                                       self.grant_count)
        logger.debug(msg)

    def __str__(self):
        return f'{self.request_model} {self.date:%m/%d/%Y}'


# RequestLimiter(limit: int)?
class RequestManager(models.Manager):
    STOLEN_GRANT_THRESHOLD = 0

    def request_grant(self):
        monitor = self._monitor()
        monitor.grant()
        if monitor.grant_count <= self.model.DAILY_LIMIT:
            return True
        monitor.revoke_grant()
        return False

    def steal_grant(self):
        monitor = self._monitor()
        monitor.grant()
        if monitor.grant_count >= RequestManager.STOLEN_GRANT_THRESHOLD:
            msg = 'Grant stolen over threshold ({}/{})'
            logger.warning(msg.format(monitor.grant_count,
                                      RequestManager.STOLEN_GRANT_THRESHOLD))

    def request_sent(self):
        self._monitor().request_sent()

    def _monitor(self):
        monitor, _ = RequestMonitor.objects.get_or_create(
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

    objects = RequestManager()

    @classmethod
    def get(cls, endpoint):
        request = cls._create(cls.HttpMethod.GET, endpoint)
        return request._send()

    @classmethod
    def _create(cls, http_method, endpoint):
        granted = cls.objects.request_grant()
        request = cls(http_method=http_method, endpoint=endpoint,
                      granted=granted)
        request.save()
        return request

    def _send(self):
        if not self.granted:
            return None
        now = timezone.now()
        # TODO: make request
        logger.info(f'[{now}] {self}')
        self.sent_on = now
        self.http_code = 200
        self.save()
        with transaction.atomic():
            if self.sent_on.date() != self.created_on.date():
                ProPublicaRequest.objects.steal_grant()
            ProPublicaRequest.objects.request_sent()
        return self.http_code  # placeholder for the full response

    def __str__(self):
        return f'{self.http_method} {self.endpoint}'
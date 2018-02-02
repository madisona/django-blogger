import sys

from django.core.management.base import BaseCommand

from blogger import models, config


class Command(BaseCommand):
    help = 'Add pubsubhubbub subscription for your blog.'

    def handle(self, *args, **options):
        topic_url = config.blogger_feed_url

        subscription = models.HubbubSubscription.get_by_feed_url(topic_url)
        if subscription:
            response = subscription.send_subscription_request(mode='unsubscribe')
            subscription.delete()

            if response is False:
                sys.stdout.write('Unsubscribe request for %s not sent successfully\n' % topic_url)
        sys.stdout.write('Unsubscribe request for %s sent successfully\n' % topic_url)


import re
import sys

from django.core.management.base import BaseCommand

from blogger import models, config

def is_valid_hostname(hostname):
    # from: http://stackoverflow.com/questions/2532053/validate-hostname-string-in-python
    if len(hostname) > 255:
        return False
    if hostname.endswith('.'):
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))

class Command(BaseCommand):
    help = 'Add pubsubhubbub subscription for your blog.'

    def handle(self, *args, **options):
        host_name = ''
        while not is_valid_hostname(host_name):
            if host_name:
                sys.stdout.write("%s is not a valid host name\n\n" % host_name)
            host_name = raw_input("Please enter your host name: ")
        topic_url = config.blogger_feed_url

        subscription, created = models.HubbubSubscription.objects.get_or_create(
            topic_url=topic_url,
            defaults = dict(host_name=host_name),
        )
        if not created:
            subscription.host_name = host_name
            subscription.save()
        response = subscription.send_subscription_request()
        if response is True:
            sys.stdout.write(
                'Created pubsubhubbub subscription for %s\n'
                'to be handled by the callback url %s\n' % (topic_url, subscription.callback_url)
            )
        else:
            sys.stdout.write(
                'Subscription request for %s\n'
                'to be handled by the callback url %s was not created successfully.\n'
                'Please check your logs\n' % (topic_url, subscription.callback_url)
            )




from django import template

from blogger import config, models

register = template.Library()

@register.assignment_tag
def get_recent_posts(cnt=None):
    return models.BloggerPost.get_latest_posts(cnt)

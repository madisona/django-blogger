from django import template

from blogger import models

register = template.Library()


@register.assignment_tag
def get_recent_posts(cnt=None):
    return models.BloggerPost.get_latest_posts(cnt)


@register.inclusion_tag('blogger/teaser_snippet.html')
def render_latest_blog_posts(num):
    posts = models.BloggerPost.get_latest_posts(num)
    return {
        'blog_posts': posts,
    }


@register.inclusion_tag('blogger/archive_month_links_snippet.html')
def render_month_links():
    return {
        'dates': models.BloggerPost.objects.all().dates('published', 'month'),
    }

from django import template
from mysite.util import Date

register = template.Library()


@register.filter(name='trans_date')
def trans_date(value, format_):
    return Date.trans_date(value, format_)

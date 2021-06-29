from django import template

register = template.Library()


@register.simple_tag()
def get_badge(string):
    if string != '':
        string = str(string)
        argf = float(string.strip('%')) / 100
        if argf >= 0.8:
            badge_type = 'bg-success'
        elif argf >= 0.6:
            badge_type = 'bg-cyan'
        elif argf >= 0.4:
            badge_type = 'bg-warning'
        elif argf >= 0.2:
            badge_type = 'bg-orange'
        elif argf >= 0:
            badge_type = 'bg-danger'
        return badge_type
    else:
        return ''

@register.simple_tag()
def get_severity_badge(string):
    if string != '':
        string = str(string)
        argf = float(string.strip('%')) / 100

        if argf >= 0.8:
            badge_type = 'bg-danger'
        elif argf >= 0.6:
            badge_type = 'bg-orange'
        elif argf >= 0.4:
            badge_type = 'bg-warning'
        elif argf >= 0.2:
            badge_type = 'bg-cyan'
        elif argf >= 0:
            badge_type = 'bg-success'
        return badge_type
    else:
        return ''

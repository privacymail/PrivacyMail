from django import template

register = template.Library()


@register.inclusion_tag('measure.html')
def show_measure(id, reliability, title, status_text, description, condition, errors, status):
    return {
        'id': id,
        'reliability': reliability,
        'title': title,
        'status_text': status_text,
        'description': description,
        'condition': condition,
        'errors': errors,
        'status': status,
    }

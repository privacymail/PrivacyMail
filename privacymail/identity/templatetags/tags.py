from django import template

register = template.Library()


@register.inclusion_tag('check.html')
def show_check(check):
    assert check.is_sane()
    return {
        "id": check.get_id(),
        "title": check.get_title(),
        "description": check.get_description(),
        "reliability": check.get_reliability(),
        "status": check.get_status(),
        "interpretation": check.get_interpretation(),
        "condition": check.get_condition(),
        "error": check.get_error(),
        "add_data": check.get_additional_data(),
        "display": check.should_display()
    }


class DetailItem():
    text = ""
    icons = []  # Each icon is specified as {"icon": "fa-icon-ident", "tooltip": "tooltip text"}
    link = ""
    properties = []  # Additional properties of the item

    def __init__(self, text, link, icons=[], properties=[]):
        self.text = text
        self.link = link
        self.icons = icons
        self.properties = properties


@register.inclusion_tag('detail.html')
def show_list_details(item):
    return {
        "text": item.text,
        "link": item.link,
        "icons": item.icons,
        "properties": item.properties
    }

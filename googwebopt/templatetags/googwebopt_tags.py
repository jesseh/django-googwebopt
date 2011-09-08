from django import template

register = template.Library()

@register.inclusion_tag("googwebopt/section_start.html", takes_context=True)
def gwo_start_section(context, name):
    return {
                "is_active" : context["GWO_ACTIVE"],
                "gwo_section": name,
           }

@register.inclusion_tag("googwebopt/section_end.html", takes_context=True)
def gwo_end_section(context):
    return {
                "is_active" : context["GWO_ACTIVE"],
           }


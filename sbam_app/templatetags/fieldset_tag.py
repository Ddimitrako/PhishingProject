from collections import OrderedDict

from django.template import TemplateSyntaxError, Library, Node, Variable
from django.utils.datastructures import *

register = Library()

@register.tag
def get_fieldset(parser, token):
    try:
        name, fields, as_, variable_name, from_, form = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError('bad arguments for %r' % token.split_contents()[0])

    return FieldSetNode(fields.split(','), variable_name, form)


class FieldSetNode(Node):
    def __init__(self, fields, variable_name, form_variable):
        self.fields = fields
        self.variable_name = variable_name
        self.form_variable = form_variable

    def render(self, context):
        form = Variable(self.form_variable).resolve(context)
        new_form = copy.copy(form)
        new_form.fields = OrderedDict([(key, form.fields[key]) for key in self.fields])

        context[self.variable_name] = new_form

        return u''

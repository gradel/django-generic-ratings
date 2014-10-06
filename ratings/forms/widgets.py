from decimal import Decimal

from django import forms
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify
from django import VERSION


def _model_name(model):
    if VERSION < (1, 7):
        return model._meta.module_name
    else:
        return model._meta.model_name


class BaseWidget(forms.TextInput):
    """
    Base widget. Do not use this directly.
    """
    template = None
    instance = None
    creation_counter = 0  # used to ensure each slider/star widget can be rendered with unique HTML id

    def __init__(self, *args, **kwargs):

        BaseWidget.creation_counter = (BaseWidget.creation_counter + 1) % 10000  # cycle the counter when too large

        super(BaseWidget, self).__init__(*args, **kwargs)

    def get_parent_id(self, name, attrs):
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        return final_attrs['id']

    def get_widget_id(self, prefix, name, key=''):
        if self.instance:
            opts = self.instance._meta
            widget_id = '%s-%s-%s_%s-%s' % (prefix, name, opts.app_label, _model_name(self.instance), self.instance.pk)
        else:
            widget_id = '%s-%s' % (prefix, name)
        if key:
            widget_id = '%s_%s' % (widget_id, slugify(key))
        widget_id = '%s_%d' % (widget_id, self.creation_counter)  # different id for different renditions of the same rating
        return widget_id

    def get_values(self, min_value, max_value, step=1):
        decimal_step = Decimal(str(step))
        value = Decimal(str(min_value))
        while value <= max_value:
            yield value
            value += decimal_step


class SliderWidget(BaseWidget):
    """
    Slider widget.

    In order to use this widget you must load the jQuery.ui slider
    javascript.

    This widget triggers the following javascript events:

    - *slider_change* with the vote value as argument
      (fired when the user changes his vote)
    - *slider_delete* without arguments
      (fired when the user deletes his vote)

    It's easy to bind these events using jQuery, e.g.::

        $(document).bind('slider_change', function(event, value) {
            alert('New vote: ' + value);
        });
    """
    def __init__(self, min_value, max_value, step, instance=None,
        can_delete_vote=True, key='', read_only=False, default='',
            template='ratings/slider_widget.html', attrs=None):
        """
        The argument *default* is used when the initial value is None.
        """
        super(SliderWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.instance = instance
        self.can_delete_vote = can_delete_vote
        self.read_only = read_only
        self.default = default
        self.template = template
        self.key = key

    def get_context(self, name, value, attrs=None):
        # here we convert *min_value*, *max_value*, *step* and *value*
        # to string to avoid odd behaviours of Django localization
        # in the template (and, for backward compatibility we do not
        # want to use the *unlocalize* filter)
        attrs['type'] = 'hidden'
        return {
            'min_value': str(self.min_value),
            'max_value': str(self.max_value),
            'step': str(self.step),
            'can_delete_vote': self.can_delete_vote,
            'read_only': self.read_only,
            'default': self.default,
            'parent': super(SliderWidget, self).render(name, value, attrs),
            'parent_id': self.get_parent_id(name, attrs),
            'value': str(value),
            'has_value': bool(value),
            'slider_id': self.get_widget_id('slider', name, self.key),
            'label_id': 'slider-label-%s' % name,
            'remove_id': 'slider-remove-%s' % name,
        }

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs or {})
        return render_to_string(self.template, context)


class StarWidget(BaseWidget):
    """
    Starrating widget.

    In order to use this widget you must download the
    jQuery Star Rating Plugin available at
    http://www.fyneworks.com/jquery/star-rating/#tab-Download
    and then load the required javascripts and css, e.g.::

        <link href="/path/to/jquery.rating.css" rel="stylesheet" type="text/css" />
        <script type="text/javascript" src="/path/to/jquery.MetaData.js"></script>
        <script type="text/javascript" src="/path/to/jquery.rating.js"></script>

    This widget triggers the following javascript events:

    - *star_change* with the vote value as argument
      (fired when the user changes his vote)
    - *star_delete* without arguments
      (fired when the user deletes his vote)

    It's easy to bind these events using jQuery, e.g.::

        $(document).bind('star_change', function(event, value) {
            alert('New vote: ' + value);
        });
    """
    def __init__(self, min_value, max_value, step, instance=None,
        can_delete_vote=True, key='', read_only=False,
            template='ratings/star_widget.html', attrs=None):
        super(StarWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.instance = instance
        self.can_delete_vote = can_delete_vote
        self.read_only = read_only
        self.template = template
        self.key = key

    def get_context(self, name, value, attrs=None):
        # here we convert *min_value*, *max_value* and *step*
        # to string to avoid odd behaviours of Django localization
        # in the template (and, for backward compatibility we do not
        # want to use the *unlocalize* filter)
        attrs['type'] = 'hidden'
        split_value = int(1 / self.step)
        if split_value == 1:
            values = range(1, self.max_value + 1)
            split = u''
        else:
            values = self.get_values(self.min_value, self.max_value, self.step)
            split = u' {split:%d}' % split_value
        return {
            'min_value': str(self.min_value),
            'max_value': str(self.max_value),
            'step': str(self.step),
            'can_delete_vote': self.can_delete_vote,
            'read_only': self.read_only,
            'values': values,
            'split': split,
            'parent': super(StarWidget, self).render(name, value, attrs),
            'parent_id': self.get_parent_id(name, attrs),
            'value': self._get_value(value, split_value),
            'star_id': self.get_widget_id('star', name, self.key),
        }

    def _get_value(self, original, split):
        if original:
            value = round(original * split) / split
            return Decimal(str(value))

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs or {})
        return render_to_string(self.template, context)


class BootstrapWidget(BaseWidget):
    """
    rating widget.

    In order to use this form you must download the
    Bootstrap Star Rating Plugin available at
    https://github.com/kartik-v/bootstrap-star-rating
    and then load the required javascripts and css.
    """
    def __init__(self, min_value, max_value, step,
            instance=None,
            can_delete_vote=True,
            key='',
            read_only=False,
            template='ratings/bootstrap_widget.html',
            attrs=None,
            show_clear=True):
        super(BootstrapWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.instance = instance
        self.can_delete_vote = can_delete_vote
        self.read_only = read_only
        self.template = template
        self.key = key
        self.show_clear = show_clear

    def get_context(self, name, value, attrs=None):
        split_value = int(1 / self.step)
        value = self._get_value(value, split_value)
        context = {
            # switch identifiers from django-ratings app to bootstrap-
            # rating app style, i.e. min_value -> min
            'min': str(self.min_value),
            'max': str(self.max_value),
            'step': str(self.step),
            'can_delete_vote': self.can_delete_vote,
            'readonly': self.read_only,
            'value': value,
            'star_id': self.get_widget_id('star', name, self.key),
            'show_clear': self.show_clear,
        }
        return context

    def _get_value(self, original, split):
        if original:
            value = round(original * split) / split
            return Decimal(str(value))

    def render(self, name, value, attrs=None):
        context = self.get_context(name, value, attrs or {})
        return render_to_string(self.template, context)

title: Using Jinja2 in Django
public: true
published: 2010-12-29
tags:
    - web-development
    - django
    - jinja
    - snippets
summary: >
    How to replace Django’s templating system by Jinja2 and still profit from
    it eg. in generic views.
    
[Jinja2](http://jinja.pocoo.org/) is a templating language inspired by
[Django](http://www.djangoproject.com/)’s, but that I find more powerful
and less awkward.  You can just use it a library in a Django application,
but then other parts of Django such as generic views still use Django
templates.

However, Django 1.2 added the concept of “template loaders”. Though it was
not the first reason they were added, these loaders allows us to plug other
template languages into Django’s templating system. (This is even
[documented](http://docs.djangoproject.com/en/dev/ref/templates/api/#using-an-alternative-template-language).)

Below is the Django 1.2+ template loader for Jinja2.

I had also posted it to
[djangosnippets.org](http://djangosnippets.org/snippets/2063/) a while ago,
and more recently on
[github](https://github.com/SimonSapin/snippets/blob/master/jinja2_for_django.py).

    :::python
    from django.template.loader import BaseLoader
    from django.template.loaders.app_directories import app_template_dirs
    from django.template import TemplateDoesNotExist
    from django.core import urlresolvers
    from django.conf import settings
    import jinja2

    class Template(jinja2.Template):
        def render(self, context):
            # flatten the Django Context into a single dictionary.
            context_dict = {}
            for d in context.dicts:
                context_dict.update(d)
            return super(Template, self).render(context_dict)

    class Loader(BaseLoader):
        is_usable = True
        
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(app_template_dirs))
        env.template_class = Template

        # These are available to all templates.
        env.globals['url_for'] = urlresolvers.reverse
        env.globals['MEDIA_URL'] = settings.MEDIA_URL
        #env.globals['STATIC_URL'] = settings.STATIC_URL
        

        def load_template(self, template_name, template_dirs=None):
            try:
                template = self.env.get_template(template_name)
            except jinja2.TemplateNotFound:
                raise TemplateDoesNotExist(template_name)
            return template, template.filename


To use it, add the following to your `settings.py` file:
(The comma is important!)

    :::python
    TEMPLATE_LOADERS = (
        'jinja2_for_django.Loader',
    )

… where `jinja2_for_django` is the name of the module where you saved the loader.

Now `django.shortcuts.render_to_response`, generic views, and other Django
components will use Jinja wherever they use templates.

Django tags and filters won’t be available but you can add functions or other
values in the `env.globals` dict as done above, or filters in `env.filters`.
See [Jinja’s documentation](http://jinja.pocoo.org/api/#jinja2.Environment)
for details.

I’ve seen two main differences apart form the syntax:

    :::html+jinja
    Use {{ url_for('view_name') }} and
    <input type="hidden" name="csrfmiddlewaretoken" value="{{ csrf_token }}">

    where in Django templates you use {% url view_name %} and {% csrf_token %}




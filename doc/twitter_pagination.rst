Twitter-style Pagination
========================

Assuming the developer wants Twitter-style pagination of
entries of a blog post, in *views.py* we have class-based::

    from el_pagination.views import AjaxListView

    class EntryListView(AjaxListView):
        context_object_name = "entry_list"
        template_name = "myapp/entry_list.html"

        def get_queryset(self):
            return Entry.objects.all()

or fuction-based::

    def entry_index(request, template='myapp/entry_list.html'):
        context = {
            'entry_list': Entry.objects.all(),
        }
        return render(request, template, context)


In *myapp/entry_list.html*:

.. code-block:: html+django

    <h2>Entries:</h2>
    {% for entry in entry_list %}
        {# your code to show the entry #}
    {% endfor %}

.. _twitter-split-template:

Split the template
~~~~~~~~~~~~~~~~~~

The response to an Ajax request should not return the entire template,
but only the portion of the page to be updated or added.
So it is convenient to extract from the template the part containing the
entries, and use it to render the context if the request is Ajax.
The main template will include the extracted part, so it is convenient
to put the page template name in the context.

*views.py* class-based becomes::

    from el_pagination.views import AjaxListView

    class EntryListView(AjaxListView):
        context_object_name = "entry_list"
        template_name = "myapp/entry_list.html"
        page_template='myapp/entry_list_page.html'

        def get_queryset(self):
            return Entry.objects.all()

or fuction-based::

    def entry_list(request,
        template='myapp/entry_list.html',
        page_template='myapp/entry_list_page.html'):
        context = {
            'entry_list': Entry.objects.all(),
            'page_template': page_template,
        }
        is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if is_ajax:
            template = page_template
        return render(request, template, context)


See :ref:`below<twitter-page-template>` how to obtain the same result
**just decorating the view**.

*myapp/entry_list.html* becomes:

.. code-block:: html+django

    <h2>Entries:</h2>
    {% include page_template %}

*myapp/entry_list_page.html* becomes:

.. code-block:: html+django

    {% for entry in entry_list %}
        {# your code to show the entry #}
    {% endfor %}

.. _twitter-page-template:

A shortcut for ajaxed views
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A good practice in writing views is to allow other developers to inject
the template name and extra data, so that they are added to the context.
This allows the view to be easily reused. Let's resume the original view
with extra context injection:

*views.py*::

    def entry_index(request,
            template='myapp/entry_list.html', extra_context=None):
        context = {
            'entry_list': Entry.objects.all(),
        }
        if extra_context is not None:
            context.update(extra_context)
        return render(request, template, context)


Splitting templates and putting the Ajax template name in the context
is easily achievable by using an included decorator.

*views.py* becomes::

    from el_pagination.decorators import page_template

    @page_template('myapp/entry_list_page.html')  # just add this decorator
    def entry_list(request,
            template='myapp/entry_list.html', extra_context=None):
        context = {
            'entry_list': Entry.objects.all(),
        }
        if extra_context is not None:
            context.update(extra_context)
        return render(request, template, context)


Paginating objects
~~~~~~~~~~~~~~~~~~

All that's left is changing the page template and loading the
:doc:`endless templatetags<templatetags_reference>`, the jQuery library and the
jQuery plugin ``el-pagination.js`` included in the distribution under
``/static/el-pagination/js/``.

*myapp/entry_list.html* becomes:

.. code-block:: html+django

    <h2>Entries:</h2>
    {% include page_template %}

    {% block js %}
        {{ block.super }}
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
        <script>$.endlessPaginate();</script>
    {% endblock %}

*myapp/entry_list_page.html* becomes:

.. code-block:: html+django

    {% load el_pagination_tags %}

    {% paginate entry_list %}
    {% for entry in entry_list %}
        {# your code to show the entry #}
    {% endfor %}
    {% show_more %}

The :ref:`templatetags-paginate` template tag takes care of customizing the
given queryset and the current template context. In the context of a
Twitter-style pagination the :ref:`templatetags-paginate` tag is often replaced
by the :ref:`templatetags-lazy-paginate` one, which offers, more or less, the
same functionalities and allows for reducing database access: see
:doc:`lazy_pagination`.

The :ref:`templatetags-show-more` one displays the link to navigate to the next
page.

You might want to glance at the :doc:`javascript` for a detailed explanation of
how to integrate JavaScript and Ajax features in Django Endless Pagination.

Pagination on scroll
~~~~~~~~~~~~~~~~~~~~

If you want new items to load when the user scroll down the browser page,
you can use the :ref:`pagination on scroll<javascript-pagination-on-scroll>`
feature: just set the *paginateOnScroll* option of *$.endlessPaginate()* to
*true*, e.g.:

.. code-block:: html+django

    <h2>Entries:</h2>
    {% include page_template %}

    {% block js %}
        {{ block.super }}
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
        <script>$.endlessPaginate({paginateOnScroll: true});</script>
    {% endblock %}

That's all. See the :doc:`templatetags_reference` to improve the use of
included templatetags.

It is possible to set the bottom margin used for
:ref:`pagination on scroll<javascript-pagination-on-scroll>` (default is 1
pixel). For example, if you want the pagination on scroll to be activated when
20 pixels remain to the end of the page:

.. code-block:: html+django

    <h2>Entries:</h2>
    {% include page_template %}

    {% block js %}
        {{ block.super }}
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
        <script>
            $.endlessPaginate({
                paginateOnScroll: true,
                paginateOnScrollMargin: 20
            });
        </script>
    {% endblock %}

Again, see the :doc:`javascript`.

On scroll pagination using chunks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes, when using on scroll pagination, you may want to still display
the *show more* link after each *N* pages. In Django Endless Pagination this is
called *chunk size*. For instance, a chunk size of 5 means that a *show more*
link is displayed after page 5 is loaded, then after page 10, then after page
15 and so on. Activating :ref:`chunks<javascript-chunks>` is straightforward,
just use the *paginateOnScrollChunkSize* option:

.. code-block:: html+django

    {% block js %}
        {{ block.super }}
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
        <script>
            $.endlessPaginate({
                paginateOnScroll: true,
                paginateOnScrollChunkSize: 5
            });
        </script>
    {% endblock %}

Specifying where the content will be inserted
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are paginating a table, you may want to include the *show_more* link
after the table itself, but the loaded content should be placed inside the
table.

For any case like this, you may specify the *contentSelector* option that
points to the element that will wrap the cumulative data:

.. code-block:: html+django

    {% block js %}
        {{ block.super }}
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
        <script>
            $.endlessPaginate({
                contentSelector: '.endless_content_wrapper'
            });
        </script>
    {% endblock %}

.. note::

    By default, the contentSelector is null, making each new page be inserted
    before the *show_more* link container.

When using this approach, you should take 2 more actions.

At first, the page template must be splitted a little different. You must do
the pagination in the main template and only apply pagination in the page
template if under ajax:

*myapp/entry_list.html* becomes:

.. code-block:: html+django

    <h2>Entries:</h2>
    {% paginate entry_list %}
    <ul>
        {% include page_template %}
    </ul>
    {% show_more %}

    {% block js %}
        {{ block.super }}
        <script src="http://code.jquery.com/jquery-latest.js"></script>
        <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
        <script>$.endlessPaginate();</script>
    {% endblock %}

*myapp/entry_list_page.html* becomes:

.. code-block:: html+django

    {% load el_pagination_tags %}

    {% if request.is_ajax %}{% paginate entry_list %}{% endif %}
    {% for entry in entry_list %}
        {# your code to show the entry #}
    {% endfor %}

This is needed because the *show_more* button now is taken off the
page_template and depends of the *paginate* template tag. To avoid apply
pagination twice, we avoid run it a first time in the page_template.

You may also set the *EL_PAGINATION_PAGE_OUT_OF_RANGE_404* to True, so a blank
page wouldn't render the first page (the default behavior). When a blank page
is loaded and propagates the 404 error, the *show_more* link is removed.

Before version 2.0
~~~~~~~~~~~~~~~~~~

Django Endless Pagination v2.0 introduces a redesigned Ajax support for
pagination. As seen above, Ajax can now be enabled using a brand new jQuery
plugin that can be found in
``static/el-pagination/js/el-pagination.js``.

Old code was removed:

.. code-block:: html+django

    <script src="http://code.jquery.com/jquery-latest.js"></script>
    {# new jQuery plugin #}
    <script src="{{ STATIC_URL }}el-pagination/js/el-pagination.js"></script>
    {# Removed. #}
    <script src="{{ STATIC_URL }}el-pagination/js/el-pagination-endless.js"></script>
    <script src="{{ STATIC_URL }}el-pagination/js/el-pagination_on_scroll.js"></script>

However, please consider :ref:`migrating<javascript-migrate>` as soon as
possible: the old JavaScript files are removed.

Please refer to the :doc:`javascript` for a detailed overview of the new
features and for instructions on :ref:`how to migrate<javascript-migrate>` from
the old JavaScript files to the new one.

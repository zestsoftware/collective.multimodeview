from collective.multimodeview.browser.base import MultiModeMixin

class MultiModeViewlet(MultiModeMixin):
    """ This class should be inherited by viewlets using
    multi-mode.
    """

    # This id will be used for two reasons:
    # - when submitting a form, each view will check that 'widget_id'
    #   entry in the form correcponds to its widget id, to avoid
    #   processing a form that should have been trated by another
    #   viewlet.
    # - it's user as an HTML id, allowing to scroll directly to the
    #   viewlet (and also replace the viewlet in Ajax)
    # Do not use '#' in the id, it's added automatically.
    widget_id = ''

    # Defines the list of buttons displayed on top of the viewlet.
    # This list is composed of dictionnaries with four keys:
    # - img: the url for the button image.
    # - text: the text used as alt/title for the image.
    # - id: the id used for the button
    # - url: the href for the link wrapping the image.
    # If the 'url' key is absent, there is not <a> tag.
    buttons = []

    # Title displayed on top of the viewlet.
    title = ''

    def __init__(self, context, request, view=None, manager=None):
        super(MultiModeViewlet, self).__init__(context, request)

        self.__parent__ = view
        self.view = view
        self.manager = manager

        form = self.request.form
        # We only switch to the asked mode if the correct widget
        # id has been provided.
        if form.get('widget_id') == self.widget_id:
            self.set_mode(form.get('mode'))
        else:
            self.mode = self.default_mode

    def get_base_url(self):
        return '%s/%s' % (self.context.absolute_url(),
                          self.view.__name__)

    def get_form_action(self):
        return '%s#%s' % (self.get_base_url(),
                          self.widget_id)

    def make_link(self, mode, extra_params = None):
        if extra_params is None:
            extra_params = {}

        extra_params['widget_id'] = self.widget_id
        link = super(MultiModeViewlet, self).make_link(mode, extra_params)

        return '%s#%s' % (link, self.widget_id)

    def make_form_extras(self, options = None):
        if options is None:
            options = {}

        options['widget_id'] = self.widget_id
        return super(MultiModeViewlet, self).make_form_extras(options)

    def update(self):
        self.on_call()

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from collective.multimodeview import MultiModeViewMessageFactory as _
from zope.app.component.hooks import getSite
from zope.i18n import translate
import logging

logger = logging.getLogger('collective.multimodeview')


class MultiModeMixin(BrowserView):
    """ Do not use this view, use MultiModeView or MultiModeViewlet below.
    """

    # The list of modes for this view.
    # You can define as a simple list: ['list', 'add', 'edit', 'delete']
    # for example.
    # You can also define it as a dictionnary to define some extra values
    # for each mode.
    # example: {'list' : {},
    #           'add': {'success_msg': 'The file has been added',
    #                   'error_msg': 'This file can not be added - see errors',
    #                   'submit_label': 'Add file'},
    #           'edit': {'success_msg': 'The file has been edited',
    #                    'error_msg': 'This file can not be edited - see errors',
    #                    'submit_label': 'Edit file'},
    #           'delete': {'success_msg': 'The file has been deleted',
    #                      'error_msg': 'This file can not be deleted - see errors',
    #                      'submit_label': 'Delete file'}}
    # Possible values for extra values are:
    # - success_msg: the message to display in portal message when the form has been
    #   successfully processed
    # - error_msg: message dislayed in the portal message when errors have been
    #   found when checking the form
    # - cancel_msg: message displayed when the user cancels
    # - submit_label: value for the submit button generated by 'make_form_extras'
    # - cancel_label: label for the cancel button
    # - success_mode: the mode used when the form is successfully processed
    # - cancel_mode: the mode to switch when the user cancels.
    # - redirect_url: the url where the user is redirected when this mode is used.
    # - redirect_meth: the method used to generate the redirection url.
    # - auto_process: if set to True, the view will automatically run the _process_xxx_form
    #   method when switching to this mode (as if the view was switched to this mode and
    #   the form submitted)
    modes = {}

    # The mode the view should switch to by default
    # after a form is correctly submitted or when
    # switching to a non-existing mode.
    default_mode = ''

    # You can define a special mode displayed when the user cancels.
    # If cancel_mode is not defined, it will use the default_mode
    # when cancelling.
    cancel_mode = None

    # The permission needed see the view.
    # This can be usefull when you want to include a multimode
    # view in another view and do not want to get 'Unauthorized'
    # errors.
    # The view is decalred as public in the zcml, but will render
    # an empty string if the user does not have the correct permission.
    view_permission = ''

    # The name of the view as defined in the zcml.
    # This is used in two places:
    # - when creating links with make_link to be sure we redirect
    #   to the correct place.
    # - to render the correct widget when replacing it with Ajax.
    view_name = ''

    # The list of errors founds when submitting the form.
    # If a field name is present in the keys, then is should be
    # displayed as an error field.
    # The associated values are the list of errors found for the link.
    errors = {}

    # Message displayed as a portal message when the form submitted was not
    # checkable (see check_form)
    form_error_msg = _(
        u'form_error_msg',
        default=u'The form you filled has not ben sent properly, ' +
        'please try again.'
    )

    # Message displayed as a portal message when the form was successfully
    # processed.
    success_msg = _(
        u'success_msg',
        default=u'Changes have been saved.'
    )

    # Message displayed as a portal message when the form was not valid.
    error_msg = _(
        u'error_msg',
        default=u'Errors have been found in the form you sent. ' +
        'Please correct them.'
    )

    # Message displayed when the user hit the cancel button.
    cancel_msg = _(
        u'cancel_msg',
        default=u'Changes have been cancelled.'
    )

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}
        self.mode = self.default_mode

    def set_mode(self, mode):
        """ This method should always be used when switching
        the mode of a view instead of directly playing with
        the 'mode' attribute directly.
        """
        if mode in self.modes:
            self.mode = mode
        else:
            self.mode = self.default_mode

    def __getattr__(self, name):
        """ A bit of black magic here.
        You can access a few not-really defined
        attributes here:
        - is_something_mode: boolean telling if the view
          is currently in the 'something' mode.
        - something_link: link to switch to 'something' mode.
        """
        for mode in self.modes:
            if name == ('is_%s_mode' % mode):
                return self.mode == mode

            if mode != 'make' and name == ('%s_link' % mode):
                # If the mode is called 'make' we would run into
                # a infinite loop and that's not a good thing.
                return self.make_link(mode)

        return super(MultiModeMixin, self).__getattribute__(name)

    def make_link(self, mode, extra_params=None):
        """ Returns a link for the asked mode.
        If extra parameters are provided, they will
        be included as GET parameters too.

        myview.make_link('edit', {'UID': 'my_uid'})
        http://example.com/current_context/view_name?mode=add&UID=mu_uid
        """
        if extra_params is None:
            extra_params = {}

        base_url = self.get_base_url()

        base_url += '?mode=%s' % mode
        for key, value in extra_params.items():
            base_url += '&%s=%s' % (key, value)

        return base_url

    def make_form_extras(self, options=None):
        """ Returns a string meant to be used in the form.
        It provides a hidden field with the current mode
        and two submit buttons (validate/cancel).

        The buttons are only shown when there is a
        'submit_label' associated with the mode.
        (see explanations for the modes attribute)
        """
        if options is None:
            options = {}

        # We need to define the template as an attribute of the view, if we don't
        # we can not render it.
        self.fake_template = ZopeTwoPageTemplateFile(
            'templates/form_extras.pt')

        options['mode'] = self.mode
        if isinstance(self.modes, dict):
            options['submit_label'] = self.modes[self.mode].get('submit_label')
            options['cancel_label'] = self.modes[
                self.mode].get('cancel_label', None)

        return self.fake_template(**options)

    @property
    def portal_url(self):
        """ Shortcut to get the portal_url.
        """
        return self.getSite().absolute_url()

    def get_portal(self):
        return getSite()

    def get_base_url(self):
        """ The url of the page.
        """
        return '%s/%s' % (aq_inner(self.context.absolute_url()),
                          self.view_name)

    def get_form_action(self):
        return self.get_base_url()

    def get_mtool(self):
        """ Shortcut to get the portal_membership tool.
        """
        return getToolByName(aq_inner(self.context),
                             'portal_membership')

    def get_user(self):
        """ Shortcut to get the user currently logged-in.
        Return None when the user is Anonymous.
        """
        mtool = self.get_mtool()
        if mtool.isAnonymousUser():
            return
        return mtool.getAuthenticatedMember()

    def check_permission(self, permission, context=None):
        """ Shortcut to check a permission.
        """
        if context is None:
            context = aq_inner(self.context)
        return self.get_mtool().checkPermission(permission,
                                                context)

    def object_from_uid(self, uid):
        """ Shortcut to use the uid_catalog.
        Return the first (and hopefully only) having this
        UID or None.
        """
        uid_cat = getToolByName(self.context,
                                'uid_catalog')
        brains = uid_cat(UID=uid)
        if not brains:
            logger.info('No object found for UID %s' % uid)
            return None

        try:
            return brains[0].getObject()
        except:
            logger.info('Unable to wake up %s' % brains[0])
            return None

    def is_shown(self):
        """ Tells if the user has the permission to see
        the page.
        """
        if not self.view_permission:
            # Ok there is no custom permission for this view,
            # it should be Ok.
            # in the worst case, it might raise an Unanthorized error.
            return True

        return self.check_permission(self.view_permission)

    def add_portal_message(self, msg, type='info'):
        """ Translates the message and displays it as a
        portal message.
        """
        if not msg:
            return

        translated = translate(msg, context=self.request)
        IStatusMessage(self.request).addStatusMessage(translated, type)

    def class_for_field(self, field):
        if field in self.errors:
            return 'field error'
        return 'field'

    def filter_archetype_form(self, context, schema, fields):
        """ This can be used when you manage Archetypes objects and use
        the archetypes macros in the template.
        This method will use the widgets process_form method to transform
        content in the form.
        """
        form = self.request.form
        new_form = {}
        for field in schema.fields():
            fieldname = field.getName()
            if fieldname not in fields:
                continue

            widget = field.widget
            processed_value = widget.process_form(
                context, field, form)

            if isinstance(processed_value, tuple):
                new_form[fieldname] = processed_value[0]
            else:
                new_form[fieldname] = processed_value

        return new_form

    def check_archetype_form(self, form, context, fields):
        """ Uses the schema validators to validate a form.
        """
        for field in context.schema.fields():
            fieldname = field.getName()
            if fieldname not in fields:
                continue

            if not field.validators:
                continue

            field_errors = field.validate(
                form.get(fieldname),
                context,
                REQUEST=self.request)

            if field_errors is not None:
                self.errors[fieldname] = field_errors

    def check_form(self):
        """ This function is called when a form is submitted.
        It returns True in most cases, except when something really
        wrong happens (the example the form is not complete and can not
        be checked).

        You can override this method to do you checkings or simply
        define one method for each mode you have in you view.
        Those methods must be called _check_mode_form.
        For example _check_add_form will be called when a form has been
        submitted in 'add' mode.
        """
        try:
            checker = getattr(self, '_check_%s_form' % self.mode)
        except AttributeError:
            logger.error('Method not found: _check_%s_form' % self.mode)
            return False

        return checker()

    def process_form(self):
        """ Method called when a form has been submitted and no error
        have been found.
        This method can eventually return the mode displayed once the form
        is processed. If nothing is returned, the view will switch to the
        default mode.

        As for check_form, you can either override it or create a process
        method for each mode (for example _process_add_form to process the
        form in 'add' mode).
        """
        try:
            processor = getattr(self, '_process_%s_form' % self.mode)
        except AttributeError:
            logger.error('Method not found: _process_%s_form' % self.mode)
            return

        view = processor()
        if isinstance(self.modes, dict):
            msg = self.modes[self.mode].get('success_msg', None)
            if msg is not None:
                self.success_msg = msg

            # We only check what has been defined in the modes dictionnary
            # if nothing is defined in the _process_mode_form itself.
            if view is None:
                view = self.modes[self.mode].get('success_mode', view)

        return view

    def get_redirect_url(self):
        """ Returns the URL where the user should be redirected
        if needed.
        Returns None is nothing was specified.
        """
        if not isinstance(self.modes, dict):
            return

        redirect_url = self.modes.get(self.mode, {}).get('redirect_url', None)
        if redirect_url:
            return redirect_url

        redirect_meth_id = self.modes.get(
            self.mode, {}).get(
            'redirect_meth', '')
        if redirect_meth_id:
            redirect_meth = getattr(self, redirect_meth_id, None)
            if redirect_meth:
                return redirect_meth()

    def on_call(self):
        """ This is the method called by __call__ (for the views)
        or update (for the viewlets).

        It checks and process the form is needed.
        """
        if not self.is_shown():
            # The user does not have the permission to see
            # this view.
            return

        form = self.request.form
        if 'form_cancelled' in form:
            # User cancelled.
            if isinstance(self.modes, dict):
                cancel_mode = self.modes.get(
                    self.mode, {}).get(
                    'cancel_mode', None)
                if cancel_mode not in self.modes:
                    msg = "Tried to switch to mode '%s' after cancelling, " + \
                          "but this mode does not exist"
                    logger.info(msg % cancel_mode)
                    cancel_mode = None

                cancel_msg = self.modes.get(
                    self.mode, {}).get(
                    'cancel_msg', None)
            else:
                cancel_mode = None
                cancel_msg = None

            self.mode = cancel_mode or self.cancel_mode or self.default_mode

            self.add_portal_message(cancel_msg or self.cancel_msg)
            return

        if 'form_submitted' not in form or \
                self.request.get('REQUEST_METHOD') != 'POST':
            if isinstance(self.modes, dict) and \
               self.modes.get(self.mode, {}).get('auto_process', False):
                # We are in an auto-process mode.
                new_mode = self.process_form()
                self.set_mode(new_mode)
                self.add_portal_message(self.success_msg)

            # We just called the page normally.
            return

        if not self.check_form():
            # Something wrong happened, like fields missing when
            # submitting the form.
            # This case should not happen normally.
            self.add_portal_message(self.form_error_msg, 'error')
            logger.info('Check form returned False - please investigate.' +
                        'The form was: \n%s' % form)
        else:
            if self.errors:
                if isinstance(self.modes, dict):
                    error_msg = self.modes[self.mode].get('error_msg', None)
                    if error_msg is not None:
                        self.error_msg = error_msg

                self.add_portal_message(self.error_msg,
                                        'error')
                logger.info(self.errors)
            else:
                new_mode = self.process_form()
                self.set_mode(new_mode)
                self.add_portal_message(self.success_msg)

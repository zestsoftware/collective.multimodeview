from zope.i18n import translate
from jquery.pyproxy.plone import jquery, JQueryProxy

class MultiModeAjaxMixin(object):
    """ This class is used when refreshing a multimodeview
    with ajax.
    """

    # Dictionnary matching error and the selectors.
    error_mapping = {}

    # CSS selector to provide the node holding refreshed content.
    content_selector = ''

    # The name of the viewlet (or page) used to refresh the content.
    viewlet_name = ''

    def _update_content(self, jq):
        jq(self.content_selector).html(
            self.context.restrictedTraverse(self.viewlet_name)())
        return jq

    @jquery
    def refresh(self):
        jq = JQueryProxy()
        return self._update_content(jq)

    @jquery
    def save(self):
        jq = JQueryProxy()
        if not self.check_form():
            jq.set_portal_message(self.form_error_msg, 'error')
            return jq

        if self.errors:
            # Remove the previous errors.
            errors_selector = '#' + self.content_selector + ' .error'
            jq(errors_selector).addClass('dont-show')
            jq(errors_selector).removeClass('error')

            for err in self.errors:
                if err in self.error_mapping:
                    jq(self.error_mapping[err]).addClass('error')
                    jq(self.error_mapping[err]).removeClass('dont-show')

            jq.set_portal_message(self.error_msg, 'error')
            return jq

        new_mode = self.process_form()
        # We have to remove the 'form_submitted' to avoid doing the action twice.
        del self.request.form['form_submitted']
        self.request.form['mode'] = new_mode

        jq.set_portal_message(self.success_msg, 'success')
        return self._update_content(jq)

    @jquery
    def cancel(self):
        """ Shows the cancel message and updates the page.
        """
        jq = JQueryProxy()
        jq.set_portal_message(self.cancel_msg, 'success')
        return self._update_content(jq)

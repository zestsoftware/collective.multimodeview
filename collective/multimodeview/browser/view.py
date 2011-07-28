from collective.multimodeview.browser.base import MultiModeMixin

class MultiModeView(MultiModeMixin):
    """ This class should be inherited by views using multi-mode.
    """
    def __init__(self, *args, **kwargs):
        super(MultiModeView, self).__init__(*args, **kwargs)
        self.set_mode(self.request.form.get('mode', ''))
    
    def __call__(self):
        self.on_call()
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return self.request.RESPONSE.redirect(redirect_url)

        return self.index()

from Products.Five import BrowserView

from collective.multimodeview.browser.base import MultiModeMixin

class MultiModeView(MultiModeMixin, BrowserView):
    """ This class should be inherited by views using multi-mode.
    """

    def __call__(self):
        self.on_call()
        return self.index()

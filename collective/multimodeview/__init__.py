  # -*- extra stuff goes here -*- 
from zope.i18nmessageid import MessageFactory
MultiModeViewMessageFactory = MessageFactory(u'collective.multimodeview')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

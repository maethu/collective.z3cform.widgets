import zope.component
import zope.interface
import zope.schema

from z3c.form import interfaces
from z3c.form import widget
from z3c.form.browser import textarea
from z3c.form.converter import BaseDataConverter

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from collective.z3cform.widgets.interfaces import IKeywordsWidget

class KeywordsWidget(textarea.TextAreaWidget):
    """Widget for adding new keywords and autocomplete with the ones in the
    system."""
    zope.interface.implementsOnly(IKeywordsWidget)
    klass = u"keyword-widget"
    display_template = ViewPageTemplateFile('keywords_display.pt')
    input_template = ViewPageTemplateFile('keywords_input.pt')
    
    # JavaScript template
    js_template = """\
    (function($) {
        $().ready(function() {
            var newValues = [%(newtags)s];
            var oldValues = [%(oldtags)s];
            $('#%(id)s').data('klass','%(klass)s');
            keywordTokenInputActivate('%(id)s', newValues, oldValues);
        });
    })(jQuery);
    """

    def js(self):
        values = self.context.portal_catalog.uniqueValuesFor('Subject')
        old_values = self.context.Subject()
        tags = ""
        old_tags = ""
        index = 0
        for index, value in enumerate(values):
            tags += "{id: '%s', name: '%s'}" % (value, value)
            if index < len(values) - 1:
                tags += ", "
        old_index = 0
        #prepopulate
        for index, value in enumerate(old_values):
            old_tags += "{id: '%s', name: '%s'}" % (value, value)
            if index < len(old_values) - 1:
                old_tags += ", "

        return self.js_template % dict(id=self.id,
            klass=self.klass,
            newtags=tags,
            oldtags=old_tags)

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)

@zope.interface.implementer(interfaces.IFieldWidget)
def KeywordsFieldWidget(field, request):
    """IFieldWidget factory for KeywordsWidget."""
    return widget.FieldWidget(field, KeywordsWidget(request))
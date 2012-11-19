from json import dumps
import zope.component
import zope.interface
import zope.schema

from z3c.form import interfaces
from z3c.form import widget
from z3c.form.browser import textarea

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from collective.z3cform.widgets.interfaces import ITokenInputWidget
from zope.schema.interfaces import IChoice
from zope.schema.vocabulary import getVocabularyRegistry


class TokenInputWidget(textarea.TextAreaWidget):
    """Widget for adding new keywords and autocomplete with the ones in the
    system."""
    zope.interface.implementsOnly(ITokenInputWidget)
    klass = u"token-input-widget"
    display_template = ViewPageTemplateFile('token_input_display.pt')
    input_template = ViewPageTemplateFile('token_input_input.pt')

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

    def _get_old_values(self, vocab):
        values = getattr(self.context, self.field.getName(), [])
        result = []
        if not vocab:
            return result
        for value in values:
            term = vocab.getTermByToken(value)
            if term:
                result.append((term.token, term.value))
        return result

    def js(self):
        value_type = self.field.value_type
        vocab = None
        if IChoice.providedBy(self.field.value_type):
            if value_type.vocabulary:
                vocab = value_type.vocabulary
            if value_type.vocabularyName:
                vocab = getVocabularyRegistry().get(
                    self.context, self.field.value_type.vocabularyName)
            values = [(term.token, term.value) for term in vocab]
            old_values = self._get_old_values(vocab)
        else:
            values = enumerate(self.context.portal_catalog.uniqueValuesFor('Subject'))
            old_values = enumerate(self.context.Subject())
        tags = []
        old_tags = []
        index = 0
        for index, value in values:
            tags.append({'id': index, 'name': value})
        #prepopulate
        for index, value in old_values:
            old_tags.append({'id': index, 'name': value})
        result = self.js_template % dict(id=self.id,
            klass=self.klass,
            newtags=dumps(tags),
            oldtags=dumps(old_tags))
        return result

    def render(self):
        if self.mode == interfaces.DISPLAY_MODE:
            return self.display_template(self)
        else:
            return self.input_template(self)


@zope.interface.implementer(interfaces.IFieldWidget)
def TokenInputFieldWidget(field, request):
    """IFieldWidget factory for TokenInputWidget."""
    return widget.FieldWidget(field, TokenInputWidget(request))

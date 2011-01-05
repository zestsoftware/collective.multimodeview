from collective.multimodeview.browser import MultiModeView

class Sample1View(MultiModeView):
    """ A simple view with two modes.
    """
    modes = ['conditions',
             'data_use']
    default_mode = 'conditions'
    view_name = 'multimodeview_sample1'


from zope.app.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from persistent.list import PersistentList

class Sample2View(MultiModeView):
    """ A view that adds annotations on the portal.
    """
    modes = ['list',
             'add',
             'edit',
             'delete']
    default_mode = 'list'
    view_name = 'multimodeview_sample2'

    def get_notes(self):
        anno_key = 'multimodeview_sample2'
        portal = getSite()

        annotations = IAnnotations(portal)
        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        notes = metadata.get('notes', None)
        if notes is None:
            metadata['notes'] = PersistentList()
            notes = metadata['notes']

        return notes

    def add_note(self, title):
        notes = self.get_notes()
        notes.append(title)

    def edit_note(self, note_id, title):
        notes = self.get_notes()
        notes[note_id] = title

    def delete_note(self, note_id):
        notes = self.get_notes()
        notes[note_id] = None

    def _get_note_id(self):
        notes = self.get_notes()
        note_id = self.request.form.get('note_id', '')
        try:
            note_id = int(note_id)
        except ValueError:
            # This should not happen, something wrong happened
            # with the form.
            return

        if note_id < 0 or note_id >= len(notes):
            # Again, something wrong hapenned.
            return

        if notes[note_id] is None:
            # This note has been deleted, nothing should be done
            # with it.
            return

        return note_id

    def _check_add_form(self):
        if not self.request.form.get('title'):
            self.errors['title'] = 'You must provide a title'

        return True

    def _check_edit_form(self):
        if self._get_note_id() is None:
            return

        return self._check_add_form()

    def _check_delete_form(self):
        return self._get_note_id() is not None

    def _process_add_form(self):
        self.add_note(self.request.form.get('title'))

    def _process_edit_form(self):
        self.edit_note(
            self._get_note_id(),
            self.request.form.get('title'))

    def _process_delete_form(self):
        self.delete_note(self._get_note_id())

class Sample21View(Sample2View):
    """ A view that adds annotations on the portal.
    """
    modes = {'list': {},
             'add': {'success_msg': 'The note has been added',
                     'error_msg': 'Impossible to add a note: please correct the form',
                     'submit_label': 'Add note'},
             'edit': {'success_msg': 'The note has been edited',
                     'submit_label': 'Edit note'},
             'delete': {'success_msg': 'The note has been deleted',
                        'submit_label': 'Delete note'}
             }

    view_name = 'multimodeview_sample21'

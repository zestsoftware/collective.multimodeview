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

class Sample3View(MultiModeView):
    modes = {'step1': {'submit_label': 'Go to step 2'},
             'step2': {'submit_label': 'Go to step 3'},
             'step3': {'submit_label': 'Go to step 4'},
             'step4': {'submit_label': 'Go to step 5'},
             'step5': {}}

    default_mode = 'step1'
    view_name = 'multimodeview_sample3'

    def check_form(self):
        return True

    def _process_step1_form(self):
        return 'step2'

    def _process_step2_form(self):
        return 'step3'

    def _process_step3_form(self):
        return 'step4'

    def _process_step4_form(self):
        return 'step5'

    def _process_step5_form(self):
        return 'step5'

    @property
    def cancel_mode(self):
        mapping = {'step1': 'step1',
                   'step2': 'step1',
                   'step3': 'step2',
                   'step4': 'step3',
                   'step5': 'step4'}
        return mapping.get(self.mode)

class Sample31View(MultiModeView):
    modes = {'step1': {'submit_label': 'Go to step 2',
                       'cancel_label': 'Cancel',
                       'success_mode': 'step2',
                       'cancel_mode': 'step1',
                       'cancel_msg': 'You can not go back, mwahaha'},
             'step2': {'submit_label': 'Go to step 3',
                       'cancel_label': 'Back to step 1',
                       'success_mode': 'step3',
                       'cancel_mode': 'step1'},
             'step3': {'submit_label': 'Go to step 4',
                       'cancel_label': 'Back to step 2',
                       'success_mode': 'step4',
                       'cancel_mode': 'step2'},
             'step4': {'submit_label': 'Go to step 5',
                       'cancel_label': 'Back to step 3',
                       'success_mode': 'step5',
                       'cancel_mode': 'step3'},
             'step5': {}}

    default_mode = 'step1'
    view_name = 'multimodeview_sample31'

    def check_form(self):
        return True

    def _process_step1_form(self):
        pass

    def _process_step2_form(self):
        pass

    def _process_step3_form(self):
        pass

    def _process_step4_form(self):
        pass


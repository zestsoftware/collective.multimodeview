from Products.Five import BrowserView
from zope.app.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from persistent.list import PersistentList

class NotesView(BrowserView):
    def _get_metadata(self):
        anno_key = 'multimodeview_sample2'
        portal = getSite()

        annotations = IAnnotations(portal)
        metadata = annotations.get(anno_key, None)
        if metadata is None:
            annotations[anno_key] = PersistentDict()
            metadata = annotations[anno_key]

        return metadata

    def get_notes(self):
        metadata = self._get_metadata()

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

    def get_home_message(self):
        metadata = self._get_metadata()
        return metadata.get('home_message', '')

    def set_home_message(self, msg):
        metadata = self._get_metadata()
        metadata['home_message'] = msg

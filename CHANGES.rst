Changelog
=========

0.2 (unreleased)
----------------

- the 'add_portal_message' now only displays a message if there is
  one. It allows for example to set an empty success message for a
  given mode. [vincent]

- added auto_process to mode. When declaring this kind of mode, the
  form is automatically processed when switching to this
  mode. [vincent]

- added possibility for modes to automatically redirect to another
  page. [vincent]


0.1 (2011-02-25)
----------------

- added the possibility to define a custom label for the cancel button
  and a custom cancel message for each mode. [vincent]

- you can now defined the modes to swtich to once form is processed or
  user cancelled in the 'modes' dictionnary. [vincent]

- added samples + README. [vincent]

- extracted code from Products.plonehrm. [vincent]

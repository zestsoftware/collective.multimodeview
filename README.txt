Introduction
============

collective.multimode view is a Plone package to ease creation of views
(or viewlets) which can be in several states, for example a page
containing a form or a guide with several steps.

This products can not be used alone, you need to manually define the
pages has you would do usually when creating browser views.

This README will show three simple examples on how to use the
product. All samples can be found in the sources in the samples
directory.

Samples of views
================

Sample 1: a simple view with two states
---------------------------------------

Let's say you want to define a view that displays the conditions to
use the site  or the engagments you are taking with the data provided
by the user.

First we need to define the Python view::

  from collective.multimodeview.browser import MultiModeView

  class Sample1View(MultiModeView):
      modes = ['conditions',
               'data_use']
      default_mode = 'conditions'
      view_name = 'multimodeview_sample1'

'modes' is the list of modes that the view can take. For simple cases, a
list is enough. The next samples will show the use of a dictionnary
for more complex cases.
'default_mode' is, as you can guess, the mode that will be displayed
by default for this page.
'view_name' is the name of the view as defined in the zcml file (we'll
see it after). It is needed to be able to define the base url for the
page or when using Ajax to fetch the content (mainly for viewlets).

The second step is to define a template for our page::

  <html xmlns="http://www.w3.org/1999/xhtml"
        xmlns:tal="http://xml.zope.org/namespaces/tal"
        xmlns:metal="http://xml.zope.org/namespaces/metal"
        xmlns:i18n="http://xml.zope.org/namespaces/i18n"
        metal:use-macro="here/main_template/macros/master"
        xml:lang="en"
        lang="en"
        i18n:domain="collective.multimodeview">
    <body>
      <div metal:fill-slot="main">
        <div tal:condition="view/is_conditions_mode">
          <p>By using this site, you agree on the fact that you will
          not do stupid things.</p>

          <p class="discreet">
            <a tal:attributes="href view/data_use_link">See how we use your data</a>
          </p>
        </div>
        <div tal:condition="view/is_data_use_mode">
          <p>We will sell your email to all known spam database, we need money.</p>

          <p class="discreet">
            <a tal:attributes="href view/conditions_link">See the conditions to use the site</a>
          </p>
        </div>
      </div>
    </body>
  </html>

With this example, we can see two examples of auto-generated
attributes for the multimodeviews.
'is_conditions_mode': provides a boolean telling if the view is in the
'conditions' mode. For each mode you defined, you can use this
shortcut ('is_xxx_mode', where 'xxx' is the name defined for you
mode).
'conditions_link': provides a link to swtich the page in 'conditions'
mode. This can be used for any mode, except if you have a mode called
'make' (it conflicts with the 'make_link' method). If you have a
'make' mode, then you'll have to manually use 'make_link' (that will
be described later).

Now you can define your view in the zcml file::

  <browser:page
      for="*"
      name="multimodeview_sample1"
      class=".views.Sample1View"
      template="sample1.pt"
      permission="zope2.View"
      />

And that's all, you can now access this  view and switch between the
two modes.

Now let's go for something a bit more interresting.

Sample 2: playing with forms
----------------------------

The first sample was pretty basic and could have been simply done by
using two pages or browser views.
The second example will show how to manage some data with a view. We
will add some annotations on the portal object (basically a simple
list of string). The view will be able to list, add, edit and delete
those notes.
We consider we have a view called 'multimodeview_notes_sample', that
provides an API to list, add, edit and delete notes (see
samples/notes_view.py).

As usual, we first define the view::

  class Sample2View(MultiModeView):
      """ A view that adds annotations on the portal.
      """
      modes = ['list',
               'add',
               'delete']
      default_mode = 'list'
      view_name = 'multimodeview_sample2'

      @property
      def notes_view(self):
          return self.context.restrictedTraverse('@@multimodeview_notes_sample')

      def _get_note_id(self):
          """ Extracts the note_id from the form, cast it
	  to an int.
	  Returns None if there is no corresponding note.
	  """

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
          self.notes_view.add_note(self.request.form.get('title'))

      def _process_edit_form(self):
          self.notes_view.edit_note(
              self._get_note_id(),
              self.request.form.get('title'))

      def _process_delete_form(self):
          self.notes_view.delete_note(self._get_note_id())

Like for the previous example, we have defined our list of modes, the
default mode and the name of the view.
We also defined some helpful functions (see the source for the
complete code, I removed it from here to focus on the important part)
to manage the notes.

The important functions are _check_xxx_form and _process_xxx_form.

The first one (_check_xxx_form) checks if the form submitted does not
contain errors. If an error is found, it is added to the 'errors'
dictionnary of the class, as we can see in '_check_add_form' if the
title is empty. 
The method always returns True, except if something wrong hapenned to
the form (some fields have not been submitted, or a value that the
user can not change in normal use case is wrong). In this case, the
method returns 'False' or None. A different message will be shown to
the user. We can see an example in '_check_delete_form', which only
checks that the note_id provided is correct.

The second one (_process_xxx_form) executes the code for the given
mode. It is only called if the corresponding check method returned
True and did not find any error.
If needed, it can return a 'mode' name so the view switch back to this
mode once the form is proceeded. By default, it switches to the
default mode.

The second step is to define the template for this view. We first
create the div (or whatever else) that is shown by default::

  <div tal:condition="view/is_list_mode">
    <tal:block tal:define="notes view/notes_view/get_notes;
                           note_exists python: bool([n for n in notes if n])">
      <table class="listing"
             tal:condition="note_exists">
        <thead>
          <tr>
            <th colspan="3">
              Notes
            </th>
          </tr>
        </thead>
        <tbody>
          <tal:block tal:repeat="note python: enumerate(notes)">
            <tr tal:define="note_id python: note[0];
                            note_text python: note[1]"
                tal:condition="note_text">
              <td tal:content="note_text" />
              <td>
                <a tal:attributes="href python: view.make_link('edit', {'note_id': note_id})"
                   title="edit this note">
                  <img tal:attributes="src python: '%s/edit.gif' % context.absolute_url()"
                       alt="edit" />
                </a>
              </td>
              <td>
                <a tal:attributes="href python: view.make_link('delete', {'note_id': note_id})"
                   title="delete this note">
                  <img tal:attributes="src python: '%s/delete_icon.gif' % context.absolute_url()"
                       alt="delete" />
                </a>
              </td>
            </tr>
          </tal:block>
        </tbody>
      </table>

      <p tal:condition="not: note_exists">
        You do not have any notes for the moment.
      </p>

      <a tal:attributes="href view/add_link">
        Add a new note
      </a>
    </tal:block>
  </div>

In this short sample, we can see the use of the 'make_link' method. We
use it to create the link to edit or delete a note. We could not use
'edit_link' or 'delete_link', as we also need to specify the note we
want to edit or delete.
using view.make_link('edit', {'note_id': note_id}) will generate a
link like this: http://..../multimodeview_sample2?mode=edit&note_id=2.

Now let's complete our template with the form to add a note::

  <div tal:condition="not: view/is_list_mode">
    <form name="manage_notes_form"
          method="POST"
          tal:define="notes view/notes_view/get_notes;
                      note_id view/_get_note_id;
                      note_text python: (note_id is not None) and notes[note_id] or '';"
          tal:attributes="action view/get_form_action">
      <tal:block tal:condition="view/is_add_mode">
        <div tal:attributes="class python: view.class_for_field('title')">
          <label for="title">Title</label>
          <div class="error_msg"
               tal:condition="view/errors/title|nothing"
               tal:content="view/errors/title" />
          <input type="text"
                 name="title"
                 tal:attributes="value view/request/form/title | nothing" />
        </div>

        <span tal:replace="structure view/make_form_extras" />

        <input type="submit"
               name="form_submitted"
               value="Add note" />
        <input type="submit"
               name="form_cancelled"
               value="Cancel" />
      </tal:block>
    </form>
  </div>

In this code we can see a few usefull methods provided by
multimodeview:

 - 'view/get_for_action': provides the action that should be used for
   the form.

 - 'view.class_for_field(field)': this methods returns 'field' if
   there is no error found for this field, or 'field error' if an error
   was found. Those class names are the default ones provided by
   Archetype, so an error will appear in red with a default Plone theme.

 - 'view/make_form_extras': this method should be used in every form 
   in multimode page. It adds some hidden fields such as the mode
   currently is use.

We can also see some specificities in the form:

 - the method should always be 'POST': if you do not use a 'POST'
   method, the form will not be processed.

 - the submit input to process the form is called 'form_submitted'.

 - the sumbit input to cancel is called 'form_cancelled'. If you use
   other names, the form will not be processed.

We can now complete the template to also be able to manage the 'edit'
and 'delete' modes::

  <tal:block tal:condition="view/is_edit_mode">
    <div tal:attributes="class python: view.class_for_field('title')">
      <label for="title">Title</label>
      <div class="error_msg"
           tal:condition="view/errors/title|nothing"
           tal:content="view/errors/title" />
      <input type="text"
             name="title"
             tal:attributes="value view/request/form/title | note_text" />
      <input type="hidden"
             name="note_id"
             tal:attributes="value note_id" />
    </div>

    <span tal:replace="structure view/make_form_extras" />
    <input type="submit"
           name="form_submitted"
           value="Edit note" />
    <input type="submit"
           name="form_cancelled"
           value="Cancel" />
  </tal:block>

  <tal:block tal:condition="view/is_delete_mode">
    <p>Are you sure you want to delete this note ?</p>
    <p class="discreet" tal:content="note_text" />

    <input type="hidden"
           name="note_id"
           tal:attributes="value note_id" />

    <span tal:replace="structure view/make_form_extras" />
    <input type="submit"
           name="form_submitted"
           value="Delete note" />
    <input type="submit"
           name="form_cancelled"
           value="Cancel" />
  </tal:block>

Nothing really new in this new code but at least we are now able to
manage the notes.

Now that the system is complete, we can see some problems incoming:

 - there is some repetitions in the template code, mainly for the
   submit buttons. The one to cancel could be factorized but the one to
   process the form has a different name everytime.

 - the messages always say 'Your changes have been saved', whatever
   you do.

Let's improve this quiclky.

Sample 2.1: using a dictionnary for modes
-----------------------------------------

The two problems seen before can be quickly fixed when defining a list
of modes with a dictionnary.

Let's define the new view, inheriting from the prevous one::

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

As you can see, for each mode, a dictionnary is provided with three
values:

 - success_msg: the message displayed when the form is successfuly
   processed.

 - error_msg: the message shown when errors are found in the form.
 
 - submit_label: the title for the button to submit the form.

Now we can also update our template. The part for listing the notes
does not change, we only update the form::

  <form name="manage_notes_form"
        method="POST"
        tal:define="notes view/notes_view/get_notes;
                    note_id view/_get_note_id;
                    note_text python: (note_id is not None) and notes[note_id] or '';"
        tal:attributes="action view/get_form_action">
    <tal:block tal:condition="view/is_add_mode">
      <div tal:attributes="class python: view.class_for_field('title')">
        <label for="title">Title</label>
        <div class="error_msg"
             tal:condition="view/errors/title|nothing"
             tal:content="view/errors/title" />
        <input type="text"
               name="title"
               tal:attributes="value view/request/form/title | nothing" />
      </div>
    </tal:block>

    <tal:block tal:condition="view/is_edit_mode">
      <div tal:attributes="class python: view.class_for_field('title')">
        <label for="title">Title</label>
        <div class="error_msg"
             tal:condition="view/errors/title|nothing"
             tal:content="view/errors/title" />
        <input type="text"
               name="title"
               tal:attributes="value view/request/form/title | note_text" />
        <input type="hidden"
               name="note_id"
               tal:attributes="value note_id" />
      </div>
    </tal:block>

    <tal:block tal:condition="view/is_delete_mode">
      <p>Are you sure you want to delete this note ?</p>
      <p class="discreet" tal:content="note_text" />

      <input type="hidden"
             name="note_id"
             tal:attributes="value note_id" />
    </tal:block>

    <span tal:replace="structure view/make_form_extras" />
  </form>

As we can see, this version is much shorter than the previous one. We
could even have factorized the input for the title, but this has
nothing to see with multimodeview, it is normal Zope/Plone/TAL coding.

The question you may have now is "Where are my input defined ?". It is
the view/make_form_extras that creates them. If no label for the
submit button is found, it will not show any button. If a label is
found, it automatically generates the two submit buttons.

Sample 3: Creating a multi-step form
------------------------------------

This last example shows how to handle a form in multiple steps. The
method used here is not the best one, as we pass the data from one
page to the other using hidden input. It would be better to use
session, cookies or even local storage for HTML5 fans, but the goal
here is more to shown how to navigate from one mode to another.

As usual, we first define the view::

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


We have overriden the 'check_form' method so it always returns True
(we do not really care about the values here).
The _process_xxx_form methods now returns the step to which the user
is sent when completing the step. So once the 1st step is done, the
second one is displayed and so on.

The 'cancel_mode' attribute has been defined has a property, so the
value can change depending on the current mode used by the view. You
can also define it has a simple attribute, but in this case it will
always return to the same mode when cancelling.

Now we can define a simple template for our view::

  <form method="POST"
        tal:attributes="action view/get_form_action">
    <input type="hidden"
           name="step1_value"
           tal:attributes="value view/request/form/step1_value|nothing"
           tal:condition="not: view/is_step1_mode" />

    <input type="hidden"
           name="step2_value"
           tal:attributes="value view/request/form/step2_value|nothing"
           tal:condition="not: view/is_step2_mode" />

    <input type="hidden"
           name="step3_value"
           tal:attributes="value view/request/form/step3_value|nothing"
           tal:condition="not: view/is_step3_mode" />

    <input type="hidden"
           name="step4_value"
           tal:attributes="value view/request/form/step4_value|nothing"
           tal:condition="not: view/is_step4_mode" />

    <div class="field"
         tal:condition="view/is_step1_mode">
      <label for="step1">What is your name?</label>
      <input type="text"
             name="step1_value"
             tal:attributes="value view/request/form/step1_value|nothing" />
    </div>

    <div class="field"
         tal:condition="view/is_step2_mode">
      <label for="step1">What is your quest?</label>
      <input type="text"
             name="step2_value"
             tal:attributes="value view/request/form/step2_value|nothing" />
    </div>

    <div class="field"
         tal:condition="view/is_step3_mode">
      <label for="step1">What is your favorite color?</label>
      <input type="text"
             name="step3_value"
             tal:attributes="value view/request/form/step3_value|nothing" />
    </div>

    <div class="field"
         tal:condition="view/is_step4_mode">
      <label for="step1">What is the air-speed velocity of an unladen swallow?</label>
      <input type="text"
             name="step4_value"
             tal:attributes="value view/request/form/step4_value|nothing" />
    </div>

    <div tal:condition="view/is_step5_mode">
      <p>Yer answers to the questions were:</p>
      <ul>
        <li>What is your name? <span tal:replace="view/request/form/step1_value|nothing" /></li>
        <li>What is your quest? <span tal:replace="view/request/form/step2_value|nothing" /></li>
        <li>What is your favorite color? <span tal:replace="view/request/form/step3_value|nothing" /></li>
        <li>What is the air-speed velocity of an unladen swallow? <span tal:replace="view/request/form/step4_value|nothing" /></li>
      </ul>
    </div>

    <span tal:replace="structure view/make_form_extras" />
  </form>

As told previously, this code is far from perfect, but shows how easy
it is to navigate from one form to the other by returning the next
mode in '_process_xxx_form' and overriding the 'cancel_mode' property.

But let's make it cleaner (again).

Sample 3.1: Navigating between mode again
-----------------------------------------

We'll use the same template than for the previous view, but update a
few things:

 - the cancel message wil differ in each mode.

 - the cancel mode will be defined in the 'modes' dictionnary

 - the next mode to use will also be defined there.


As previously, we override the 'check_form' to avoid having to define a
_check_stepx_form method for each step. We define empty methods to
process each step::

  class Sample31View(MultiModeView):
      modes = {'step1': {'submit_label': 'Go to step 2',
                         'cancel_label': 'Cancel',
                         'success_mode': 'step2',
                         'cancel_mode': 'step1',
                         'cancel_msg': 'You can not go back, mwahaha'}},
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

You might have seen that for step1, we also defined a
'cancel_msg'. This has the same effect than 'success_msg' or
'error_msg' shown in sample 2.1, except it is shown when the user cancels.

Samples with viewlets
=====================

There is currently no samples with the viewlets, for the good reason
that they work the exact same way than the views, except for two
points:

 - the class must inherit
   collective.multimodeview.browser.MultiModeViewlet instead of
   collective.multimodeview.browser.MultiModeView.
 - you must define a 'widget_id' attribute for the class, so there is
   no conflict when processing the form on page that have multiple
   viewlets defined.

Samples will be added when the automated Ajax version for viewlets
will be integrated.

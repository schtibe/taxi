from __future__ import unicode_literals

import datetime
import os
import shlex
import subprocess

from taxi.exceptions import TaxiException


def spawn_editor(filepath, editor=None):
    if editor is None:
        editor = 'sensible-editor'

    editor = shlex.split(editor)
    editor.append(filepath)

    try:
        try:
            subprocess.call(editor)
        except OSError:
            if 'EDITOR' not in os.environ:
                raise TaxiException("Can't find any suitable editor. Check"
                                    " your EDITOR env var.")

            editor = shlex.split(os.environ['EDITOR'])
            editor.append(filepath)
            subprocess.call(editor)
    # Ignore ctrl-c if the editor has been launched in the background
    except KeyboardInterrupt:
        pass


def expand_filename(filename, date=None):
    if date is None:
        date = datetime.date.today()

    return date.strftime(os.path.expanduser(filename))

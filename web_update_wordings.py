#!/usr/bin/env python
# coding=utf-8

from flask.helpers import url_for

import mobileStrings
from mobileStrings.collection_utils import StreamArrayJSONEncoder
import update_wordings

from flask import Flask, render_template

app = Flask(__name__)
app.json_encoder = StreamArrayJSONEncoder

cliargs = {}

@app.route('/')
def edit_wordings():
    return render_template("update_wordings.html")

@app.route('/table')
def wordings_table():
    languages, wordings = mobileStrings.input.read_file(cliargs.input_file)
    return render_template("wordings_table.html",
                           languages=languages, wordings=(w._asdict() for w in wordings))

@app.route('/print')
def print_wordings():
    languages, wordings = mobileStrings.input.read_file(cliargs.input_file)
    return render_template("print_wordings.html",
                           languages=languages, wordings=(w._asdict() for w in wordings))
@app.route('/save')
def save_wordings():
    #update_wordings.save_from_output_args(cliargs, languages, wordings)
    return url_for('/')

if __name__ == '__main__':
    cliargs = update_wordings.get_parsed_arguments(False)
    app.run(debug=True)

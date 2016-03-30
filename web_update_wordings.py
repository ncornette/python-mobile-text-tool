#!/usr/bin/env python
# coding=utf-8
from flask.helpers import url_for

import mobileStrings
import update_wordings

from flask import Flask, session, send_file, request, render_template

app = Flask(__name__)
app.secret_key = '\xad\xac\xe3?\xea\xd1Xg\x84\xa4\xc3\xfc!\x05\xb9\x11\xec\x89c\xb5@\xbbE\\'

cliargs = {}

@app.route('/')
def show_wordings():
    with open(cliargs.input_file) as f:
        languages, wordings = mobileStrings.input.read_json(f)
        session.update(languages=languages, wordings=wordings)
        return render_template("update_wordings.html",
                               languages=languages, wordings=wordings)

@app.route('/save')
def save_wordings():
    for f in cliargs.out_file:
        mobileStrings.output.write_file(session['languages'], session['wordings'], f)

    if cliargs.android_res_dir:
        mobileStrings.output.write_android_strings(
            session['languages'], session['wordings'], cliargs.android_res_dir, cliargs.android_resname)

    if cliargs.ios_res_dir:
        mobileStrings.output.write_ios_strings(
            session['languages'], session['wordings'], cliargs.ios_res_dir, cliargs.ios_resname)

    return url_for('/')

if __name__ == '__main__':
    cliargs = update_wordings.get_parsed_arguments(False)
    app.run(debug=True)



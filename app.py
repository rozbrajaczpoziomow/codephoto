#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from glob import glob
import os
import random

from flask import Flask, render_template, redirect, send_from_directory, request
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from highlighter import make_image, get_languages

app = Flask(__name__)
CORS(app)

class MyForm(FlaskForm):
    language = StringField('language')
    code = StringField('code', validators=[DataRequired()])


@app.route('/')
def hello_world():
    return render_template('input.html', languages=get_languages())


@app.route('/upload/<path:filename>')
def image(filename):
    return send_from_directory('upload', filename, as_attachment=('download' in request.args))

def get_random_bg():
    return random.choice(glob('templates/pycharm/*.jpg'))

def create_fname(l=6):
    return ''.join(map(lambda b: hex(b)[2:], random.randbytes(l)))

@app.route('/code', methods=['OPTIONS'])
def code_options_cors():
    return 'only here for cors'

@app.route('/code', methods=['POST'])
def render_code():
    form = MyForm(meta={'csrf': False})
    if not form.validate():
        return redirect('/')
    name = create_fname()
    path = os.path.join('upload', name + '.png')
    make_image(form.code.data, path, form.language.data, background=get_random_bg())
    # upload(path, name, nickname)
    return redirect('/i/' + name)


@app.route('/i/<path:filename>')
def custom_static(filename):
    path = os.path.join('upload', filename + '.png')
    if os.path.exists(path):
        return render_template('image.html', image=filename)
    else:
        return render_template('not_found.html'), 404


if __name__ == '__main__':
    app.run()

# install gunicorn if you wanna make it run not in dev mode
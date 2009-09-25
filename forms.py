#!/usr/bin/python
# -*- coding: utf-8 -*-

from lib.web import form

new_post = form.Form(
    form.Textbox('title'),
    form.Textarea('text'),
    form.Button('Submit!')
)

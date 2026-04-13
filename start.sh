#!/bin/sh
python manage_setup.py
exec gunicorn agrovalida.wsgi
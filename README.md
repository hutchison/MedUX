# MedUX

A Free/OpenSource Electronic Medical Record.

This project is in planning/pre-alpha state. Don't expect this to run yet.


### Install

For convenience, use a virtualenv.

    git clone https://github.com/nerdocs/MedUX.git
    cd MedUX
    pip install -r requirements.txt
    cp medux/settings.py.example medux/settings.py
    ./manage.py createsuperuser
    ./manage.py makemigrations
    ./manage.py migrate
    ./manage.py runserver

Stay tuned.

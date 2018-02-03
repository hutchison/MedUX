# MedUX

A Free/OpenSource Electronic Medical Record.

CAVEAT: This project is in planning/pre-alpha state. Don't expect this to run yet. It doesn't care about django migrations. So if your database is broken because of a major update, please just delete the DB again and start from scratch. Remember, it's pre-alpha.


### Install

For convenience, use a virtualenv.

    git clone git@github.com:nerdocs/MedUX.git
    cd MedUX
    pip install -r requirements.txt
    cp medux/settings.py.example medux/settings.py
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver

Stay tuned.

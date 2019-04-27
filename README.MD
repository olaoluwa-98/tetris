# Tetris
Tetris is a clothing store. It's built on the Django web framework.

## Project dependencies

* Django 1.11.0
* MySQLClient 1.3.7
* Django AutoSlug 1.9.3 (for AutoSlugField in Django Models)

**NB: Some of these dependencies have their own dependencies.**

Run `pip install -r requirements.txt` during initial setup.

## Running the project
After installing the requirements, run migrations:
`python manage.py migrate`

Then you can run the django server:
`python manage.py runserver`

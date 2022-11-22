SETTINGS={{ django_learning}}.settings

all:
	@echo Hello %USERNAME%, nothing to do by default.

update:
	pip install -U -r requirements.txt

superuser:
	python manage.py createsuperuser

rundev:
	python manage.py runserver

migrations:
	python manage.py makemigrations
	python manage.py migrate

tests:
	python manage.py test
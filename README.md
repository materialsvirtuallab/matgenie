# Matgenie

This repo contains the Django code for the [Matgenie](http://matgenie.materialsvirtuallab.org) front end for pymatgen.
The website is run off Heroku with static assets being served from Amazon Web Services S3.

## Running the frontend locally

Install all requirements using:

```
pip install -r requirements.txt
```

It is highly recommended you do this in a virtualenv.

Then run:

```
python manage.py runserver
```

Open a browser and point it to http://127.0.0.1:8000 (usually the default).
# CRM Proof of Concept

## Problem

We are planning to migrate away from Microsoft Dynamics 2011 (**CDMS**) and possibly build a new CRM system (**CRM**) using a gradual incremental approach.

This means that during a period of several months:

* the data between CDMS and CRM should be kept in sync
* CRM should allow re-modelling by adding/removing types/properties
* some users will use CDMS **and** others will use CRM whilst we transition from one system to the other

## Options

Different approaches could be used including:

* keep CDMS as Data Store and access it directly. This has many disadvantages including hosting CDMS, not being able to easily change the schemas etc.
* use two data stores with some sort of low level synchronization (via database or processes). This as well has many disadvantages including integrating with old technologies (Dynamics 2011), two separate layers (code and sync logic) tightly depending on each other / hard to manage etc.
* use two data stores with code-managed synchronization. This is the chosen architecture and has some disadvantages as well that we will explain later.

## The chosen approach

Two data stores with reads and writes to CDMS happening as usual and synchronization triggered from an action in CRM.

Writes to CRM will:
 * get the object from CDMS (if it exists)
 * write to CDMS and CRM

Reads from CRM will:
 * get the object from the CRM data store
 * get the related object from CDMS
 * check if CDMS was updated after the last synchronization
 * if so, update the CRM object from CDMS
 * update CDMS if the object does not exist

Read and write operations should be performed as a single transaction.

There is low possibility of conflicts as:

* objects on the two systems are kept in sync via the *modified* field updated after each CDMS get
* concurrent operations to a single object are low or non-existent in volume

In case two updates happen at approximately the same time, the last one wins. This should not be a problem as the system will keep a history of the changes.

## Disclaimer

**This code is NOT production ready**, it has not been tested well enough, does not handle errors as it should and was never supposed to be anything rather than a proof of concept.

## Getting started

This is a standard python 3 / Django / Postgres project.

Create and activate a new environment:

```
virtualenv --python=python3 venv
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements/local.txt
```

Install postgres, connect to it and run:

```
create database crm-poc;
```

Migrate the db:

```
python manage.py migrate
```

Set the ```CDMS_*``` values in ```settings/local.py```

Start the dev server, listening on port 8000:

```
python manage.py runserver 8000
```

Go to http://localhost:8000/organisation/


## For Developers

### How to enable sync support for a new Django model

Let's imagine you want to enable sync support for a new model `MyModel`.

**1. Set up Django app/model**

This is standard Django stuff that I presume you know.

**2. CDMSMigrator**

Subclass ```migrator.cdms_migrator.BaseCDMSMigrator``` and define the mapping fields and the CDMS service. Take a look at ```organisation.cdms_migrator``` for an example.

Add the CDMSMigrator to the Django Model

**3. Configure your model**

Change your model so that it looks like the one below:

```
from django.db import models

from core.models import CRMBaseModel
from core.managers import CRMManager

from .cdms_migrator import MyModel

class MyModel(CRMBaseModel):
    ...

    objects = CRMManager()
    cdms_migrator = MyModelMigrator()

```

Note the ```CRMBaseModel```, the ```CRMManager``` and the ```MyModelMigrator``` you created in step 2.

**4. Create a migration for your model**

```
./manage.py makemigrations
./manage.py migrate
```

### How it works

The custom manager defines a new extra query used to access CDMS.
Read and write operations are made to both systems at the same time and everything is transparent to the developer.

This means that you can use the usual Django ORM API:

```
myModel.save()
MyModel.objects.create()
MyModel.objects.filter(field1__icontains='...', field2__lt=4)
myModel.related_obj.set.all()
...
```

This proof of concept does not implement all the API as it was not its purpose. Some/most of them could be easily implemented.

## Limitations

There are some limitations in using this approach:

1. Amount of requests. This has not been measured yet but could (and should) be partially addressed by using some sort of caching strategy
2. The synchronization happens using one common CDMS user
3. Some Django ORM API cannot be easily implemented. E.g. ```Model.objects.count()```, ```Model.objects.filter(field1__field2='something')```. This is mainly because of the old CDMS technologies

## Tips

You can log calls to CDMS by setting the Django logger level to *DEBUG* in your ```settings/local.py```:

```
LOGGING = {
    'disable_existing_loggers': False,
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'cmds_api': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False
        }
    },
}
```

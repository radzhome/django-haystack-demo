django-haystack-demo
====================

demo using elasticsearch and haystack


First install elasticsearch and run it a sa service.  To simplify, you can use the simple search backend or Whoosh which is built in python.

Haystack
Haystack provides modular search for Django. It features a unified, familiar API that allows you to plug in different search backends (such as Solr, Elasticsearch, Whoosh, Xapian, etc.) without having to modify your code.


Install the package:
Latest stable (2.0.0) off PyPI: pip install django-haystack
Latest dev off GitHub: pip install -e git+https://github.com/toastdriven/django-haystack.git@master#egg=django-haystack
Add haystack to your INSTALLED_APPS.
Create search_indexes.py files for your models.
Setup the main SearchIndex via autodiscover.
Include haystack.urls to your URLconf.
Search!

Install

1. (optional) Setup a virtualenv and activate it.

2. Install haystack & Woosh or ElasticSearch (Recommended)

  pip install django-haystack
  pip install Whoosh  # If using whoosh, it has limitations so might want to use Elasticsearch
  pip install elasticsearch  # instead use this
  
3. Add to installed Apps

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    # Added.
    'haystack',

    # Then your usual apps...
    'blog',
]
4. Whoosh settings.py (No Geospatial support)

Requires setting PATH to the place on your filesystem where the Whoosh index should be located. Standard warnings about permissions and keeping it out of a place your webserver may serve documents out of apply.

Example:

import os
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}
4b. If using ElasticSearch instead:

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}
Others here.

5. Add The SearchView To Your URLconf. Within your URLconf, add the following line:

  (r'^search/', include('haystack.urls')),
  #url(r'^search/', include('haystack.urls')),
This will pull in the default URLconf for Haystack. It consists of a single URLconf that points to a SearchView instance. You can change this class’s behavior by passing it any of several keyword arguments or override it entirely with your own view.

6. Search template, default is in search/search.html, can define custom later i.e.

Note that the page.object_list is actually a list of SearchResult objects instead of individual models. These objects have all the data returned from that record within the search index as well as score. They can also directly access the model for the result via result.object. So the result.object.title uses the actual Note object in the database and accesses its title field.


SearchIndexes
SearchIndex objects are the way Haystack determines what data should be placed in the search index and handles the flow of data in. You can think of them as being similar to Django Models or Forms in that they are field-based and manipulate/store data.

You generally create a unique SearchIndex for each type of Model you wish to index, though you can reuse the same SearchIndex between different models if you take care in doing so and your field names are very standardized.

To build a SearchIndex, all that’s necessary is to subclass both indexes.SearchIndex & indexes.Indexable, define the fields you want to store data with and define a get_model method.

1. Sample search_indexes.py, goes into the app folder it belongs to:

import datetime
from haystack import indexes
from myapp.models import Note
 
 
class NoteIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='user')
    pub_date = indexes.DateTimeField(model_attr='pub_date')
 
    def get_model(self):
        return Note
 
    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
        
Every SearchIndex requires there be one (and only one) field with document=True. This indicates to both Haystack and the search engine about which field is the primary field for searching within.

When you choose a document=True field, it should be consistently named across all of your SearchIndex classes to avoid confusing the backend. The convention is to name this field text. There is nothing special about the text field name used in all of the examples. It could be anything; you could call it pink_polka_dot and it won’t matter. It’s simply a convention to call it text.

2. Additionally, we’re providing use_template=True on the text field. This allows us to use a data template (rather than error-prone concatenation) to build the document the search engine will index. You’ll need to create a new template inside your template directory called search/indexes/myapp/note_text.txt and place the following inside:

{{ object.title }}
{{ object.user.get_full_name }}
{{ object.body }}
In addition, we added several other fields (author and pub_date). These are useful when you want to provide additional filtering options. Haystack comes with a variety of SearchField classes to handle most types of data. A common theme is to allow admin users to add future content but have it not display on the site until that future date is reached. We specify a custom index_queryset method to prevent those future items from being indexed.

3. Index/Re-index: The final step, now that you have everything setup, is to put your data in from your database into the search index. Haystack ships with a management command to make this process easy.

Simply run:

  ./manage.py rebuild_index. 
  
You’ll get some totals of how many models were processed and placed in the index.

Note: Using the standard SearchIndex, your search index content is only updated whenever you run either ./manage.py update_index or start afresh with ./manage.py rebuild_index.

You should cron up a ./manage.py update_index job at whatever interval works best for your site (using –age=<num_hours> reduces the number of things to update). Alternatively, if you have low traffic and/or your search engine can handle it, the RealtimeSignalProcessor automatically handles updates/deletes for you.

Use Real time Signal Processor:

  HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

from django.shortcuts import render

# Create your views here.

from django.views.generic import TemplateView


class SearchView(TemplateView):

    template_name = 'mysearch/search.html'


search_view = SearchView.as_view()
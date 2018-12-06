from django.shortcuts import render


from .models import Search

import operator


def index(request):
    context = {
    }
    return render(request, 'metasearcher/index.html', context)

def search(request):
    query = request.GET['query']

    google_results_list = Search.get_google_results(query)
    contextual_results_list = Search.get_contextual_results(query)
    bing_results_list = Search.get_bing_results(query)
    faroo_results_list = Search.get_faroo_results(query)
    ahmed_results_list = Search.get_ahmed_results(query)

    unified_results = Search.get_unified_results(google_results_list, contextual_results_list, bing_results_list, faroo_results_list, ahmed_results_list)

    context = {
        'query': query,
        'google_results_list': google_results_list,
        'contextual_results_list': contextual_results_list,
        'bing_results_list': bing_results_list,
        'faroo_results_list': faroo_results_list,
        'ahmed_results_list': ahmed_results_list,
        'unified_results': sorted(unified_results.items(), key=operator.itemgetter(1))
    }
    return render(request, 'metasearcher/results.html', context)

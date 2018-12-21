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

    method = request.GET['method']
    if method == 'borda_quality':
        unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight = \
            Search.get_unified_results_borda_count_quality_weights(google_results_list, contextual_results_list,
                                                                bing_results_list, faroo_results_list,
                                                                ahmed_results_list)
    elif method == 'borda_stats':
        unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight = \
            Search.get_unified_results_borda_count_stat_weights(google_results_list, contextual_results_list,
                                                                bing_results_list, faroo_results_list,
                                                                ahmed_results_list)
    elif method == 'condorcet_quality':
        unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight = \
            Search.get_unified_results_condorcet_method_quality_weights(google_results_list, contextual_results_list,
                                                                bing_results_list, faroo_results_list,
                                                                ahmed_results_list)
    elif method == 'condorcet_stats':
        unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight = \
            Search.get_unified_results_condorcet_method_stat_weights(google_results_list, contextual_results_list,
                                                                bing_results_list, faroo_results_list,
                                                                ahmed_results_list)
    context = {
        'query': query,
        'google_results_list': google_results_list,
        'contextual_results_list': contextual_results_list,
        'bing_results_list': bing_results_list,
        'faroo_results_list': faroo_results_list,
        'ahmed_results_list': ahmed_results_list,
        'unified_results': sorted(unified_results.items(), key=operator.itemgetter(1)),
        'google_serp_weight': google_serp_weight,
        'contextual_weight': contextual_weight,
        'bing_weight': bing_weight,
        'faroo_weight': faroo_weight,
        'google_ahmed_weight': google_ahmed_weight
    }
    return render(request, 'metasearcher/results.html', context)

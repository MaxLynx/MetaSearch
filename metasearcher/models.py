from django.db import models
import urllib.request
import json

class Search(models.Model):
    # ...
    @staticmethod
    def get_google_results(query):
        url = 'https://serpapi.com/search?q=' + query
        req = urllib.request.Request(url)

        serialized_data = urllib.request.urlopen(req).read()
        google_results_list = []

        raw_google_results = json.loads(serialized_data)['organic_results']
        for google_result in raw_google_results:
            google_results_list.append(google_result['link'])
        return google_results_list

    @staticmethod
    def get_contextual_results(query):
        url = 'https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/' \
              'WebSearchAPI?q=' + query + '&count=20&autocorrect=false'
        req = urllib.request.Request(url)
        req.add_header("X-RapidAPI-Key", "b43bda6031mshce90d431d09c460p106129jsncef4762922a1")

        serialized_data = urllib.request.urlopen(req).read()
        contextual_results_list = []
        raw_contextual_results = json.loads(serialized_data)['value']
        for contextual_result in raw_contextual_results:
            contextual_results_list.append(contextual_result['url'])
        return contextual_results_list

    @staticmethod
    def get_bing_results(query):
        url = 'https://api.cognitive.microsoft.com/bing/v5.0/search?q=' + query
        req = urllib.request.Request(url)
        req.add_header("Ocp-Apim-Subscription-Key", 'dd0134941c984935854d743bf676784a')

        serialized_data = urllib.request.urlopen(req).read()
        bing_results_list = []
        raw_bing_results = json.loads(serialized_data)['webPages']['value']
        for bing_result in raw_bing_results:
            bing_results_list.append(bing_result['url'])
        return bing_results_list

    @staticmethod
    def get_faroo_results(query):
        url = 'https://faroo-faroo-web-search.p.rapidapi.com/api?q=' + query
        req = urllib.request.Request(url)
        req.add_header("X-RapidAPI-Key", "b43bda6031mshce90d431d09c460p106129jsncef4762922a1")

        serialized_data = urllib.request.urlopen(req).read()
        faroo_results_list = []
        raw_faroo_results = json.loads(serialized_data)['results']
        for faroo_result in raw_faroo_results:
            faroo_results_list.append(faroo_result['url'])
        return faroo_results_list

    @staticmethod
    def get_ahmed_results(query):
        url = 'https://www.googleapis.com/customsearch/v1?key=AIzaSyB0maKPFy0z-8VRsV1_K_rt2g-R-Ij_qp4' \
              '&cx=005983731279306834644:5bppqm2keiy&q=' + query
        req = urllib.request.Request(url)

        serialized_data = urllib.request.urlopen(req).read()
        ahmed_results_list = []
        raw_ahmed_results = json.loads(serialized_data)['items']
        for ahmed_result in raw_ahmed_results:
            ahmed_results_list.append(ahmed_result['link'])
        return ahmed_results_list

    @staticmethod
    def get_unified_results(google_results_list, contextual_results_list, bing_results_list, faroo_results_list, ahmed_results_list):
        unified_results = {}

        for i in range(len(google_results_list)):
            unified_results[google_results_list[i]] = 0
        for i in range(len(contextual_results_list)):
            unified_results[contextual_results_list[i]] = 0
        for i in range(len(bing_results_list)):
            unified_results[bing_results_list[i]] = 0
        for i in range(len(faroo_results_list)):
            unified_results[faroo_results_list[i]] = 0
        for i in range(len(ahmed_results_list)):
            unified_results[ahmed_results_list[i]] = 0

        unique_alt_count = len(unified_results)
        total_alt_count = len(google_results_list) + len(contextual_results_list) + len(bing_results_list) + len(
            faroo_results_list) + len(ahmed_results_list)
        x1 = 0.6
        x2 = 0.4

        google_serp_weight = 8 * (x1 * len(google_results_list) / unique_alt_count
                                  + x2 * len(google_results_list) / total_alt_count)
        contextual_weight = 2 * (x1 * len(contextual_results_list) / unique_alt_count
                                 + x2 * len(contextual_results_list) / total_alt_count)
        bing_weight = 3 * (x1 * len(bing_results_list) / unique_alt_count
                           + x2 * len(bing_results_list) / total_alt_count)
        faroo_weight = 3 * (x1 * len(faroo_results_list) / unique_alt_count
                            + x2 * len(faroo_results_list) / total_alt_count)
        google_ahmed_weight = 6 * (x1 * len(ahmed_results_list) / unique_alt_count
                                   + x2 * len(ahmed_results_list) / total_alt_count)
        total_weight = google_serp_weight + contextual_weight + bing_weight + faroo_weight + google_ahmed_weight
        google_serp_weight = google_serp_weight / total_weight
        contextual_weight = contextual_weight / total_weight
        bing_weight = bing_weight / total_weight
        faroo_weight = faroo_weight / total_weight
        google_ahmed_weight = google_ahmed_weight / total_weight

        for i in range(len(google_results_list)):
            if google_results_list[i] in unified_results:
                unified_results[google_results_list[i]] += i * google_serp_weight

        for key in unified_results.keys():
            if key not in google_results_list:
                unified_results[key] += len(google_results_list) * google_serp_weight

        for i in range(len(contextual_results_list)):
            if contextual_results_list[i] in unified_results:
                unified_results[contextual_results_list[i]] += i * contextual_weight

        for key in unified_results.keys():
            if key not in contextual_results_list:
                unified_results[key] += len(contextual_results_list) * contextual_weight

        for i in range(len(bing_results_list)):
            if bing_results_list[i] in unified_results:
                unified_results[bing_results_list[i]] += i * bing_weight

        for key in unified_results.keys():
            if key not in bing_results_list:
                unified_results[key] += len(bing_results_list) * bing_weight

        for i in range(len(faroo_results_list)):
            if faroo_results_list[i] in unified_results:
                unified_results[faroo_results_list[i]] += i * faroo_weight

        for key in unified_results.keys():
            if key not in faroo_results_list:
                unified_results[key] += len(faroo_results_list) * faroo_weight

        for i in range(len(ahmed_results_list)):
            if ahmed_results_list[i] in unified_results:
                unified_results[ahmed_results_list[i]] += i * google_ahmed_weight

        for key in unified_results.keys():
            if key not in ahmed_results_list:
                unified_results[key] += len(ahmed_results_list) * google_ahmed_weight
        return unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight

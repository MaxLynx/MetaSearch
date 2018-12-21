from django.db import models
import urllib.request
import json
from bs4 import BeautifulSoup
import operator


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
            text = google_result['link']
            if text[-1] == '/':
                text = text[:-1]
            google_results_list.append(text)
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
            text = contextual_result['url']
            if text[-1] == '/':
                text = text[:-1]
            contextual_results_list.append(text)
        return contextual_results_list

    @staticmethod
    def get_bing_results(query):
        url = 'https://www.bing.com/search?q=' + query
        req = urllib.request.Request(url)

        page = urllib.request.urlopen(req).read()
        soup = BeautifulSoup(page, 'html.parser')
        cites = soup.findAll('cite')
        bing_results_list = []
        for bing_result in cites:
            text = bing_result.text
            if text[0] != 'h':
                text = 'https://' + text
            bing_results_list.append(text)
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
            text = faroo_result['url']
            if text[-1] == '/':
                text = text[:-1]
            faroo_results_list.append(text)
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
            text = ahmed_result['link']
            if text[-1] == '/':
                text = text[:-1]
            ahmed_results_list.append(text)
        return ahmed_results_list

    @staticmethod
    def get_unified_results_borda_count_quality_weights(google_results_list, contextual_results_list, bing_results_list, faroo_results_list, ahmed_results_list):
        unified_results = {}

        unique_google_count = 0
        unique_contextual_count = 0
        unique_bing_count = 0
        unique_faroo_count = 0
        unique_ahmed_count = 0

        for i in range(len(google_results_list)):
            unified_results[google_results_list[i]] = 0
            if google_results_list[i] not in contextual_results_list and \
                    google_results_list[i] not in bing_results_list and \
                    google_results_list[i] not in faroo_results_list and \
                    google_results_list[i] not in ahmed_results_list:
                unique_google_count += 1
        for i in range(len(contextual_results_list)):
            if contextual_results_list[i] not in unified_results:
                unified_results[contextual_results_list[i]] = 0
                if contextual_results_list[i] not in google_results_list and \
                        contextual_results_list[i] not in bing_results_list and \
                        contextual_results_list[i] not in faroo_results_list and \
                        contextual_results_list[i] not in ahmed_results_list:
                    unique_contextual_count += 1
        for i in range(len(bing_results_list)):
            if bing_results_list[i] not in unified_results:
                unified_results[bing_results_list[i]] = 0
                if bing_results_list[i] not in google_results_list and \
                        bing_results_list[i] not in contextual_results_list and \
                        bing_results_list[i] not in faroo_results_list and \
                        bing_results_list[i] not in ahmed_results_list:
                    unique_bing_count += 1
        for i in range(len(faroo_results_list)):
            if faroo_results_list[i] not in unified_results:
                unified_results[faroo_results_list[i]] = 0
                if faroo_results_list[i] not in google_results_list and \
                        faroo_results_list[i] not in contextual_results_list and \
                        faroo_results_list[i] not in bing_results_list and \
                        faroo_results_list[i] not in ahmed_results_list:
                    unique_faroo_count += 1
        for i in range(len(ahmed_results_list)):
            if ahmed_results_list[i] not in unified_results:
                unified_results[ahmed_results_list[i]] = 0
                if ahmed_results_list[i] not in google_results_list and \
                        ahmed_results_list[i] not in contextual_results_list and \
                        ahmed_results_list[i] not in bing_results_list and \
                        ahmed_results_list[i] not in faroo_results_list:
                    unique_ahmed_count += 1

        unique_alt_count = unique_google_count + unique_bing_count + unique_contextual_count + unique_faroo_count + unique_ahmed_count
        total_alt_count = len(unified_results) - 2
        x1 = 0.6
        x2 = 0.4

        google_serp_weight = 8 * (x1 * unique_google_count / unique_alt_count
                                  + x2 * len(google_results_list) / total_alt_count)
        contextual_weight = 2 * (x1 * unique_contextual_count / unique_alt_count
                                 + x2 * len(contextual_results_list) / total_alt_count)
        bing_weight = 3 * (x1 * unique_bing_count / unique_alt_count
                           + x2 * len(bing_results_list) / total_alt_count)
        faroo_weight = 3 * (x1 * unique_faroo_count / unique_alt_count
                            + x2 * len(faroo_results_list) / total_alt_count)
        google_ahmed_weight = 6 * (x1 * unique_ahmed_count / unique_alt_count
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

    @staticmethod
    def get_unified_results_borda_count_stat_weights(google_results_list, contextual_results_list, bing_results_list,
                                                        faroo_results_list, ahmed_results_list):
        unified_results = {}

        unique_google_count = 0
        unique_contextual_count = 0
        unique_bing_count = 0
        unique_faroo_count = 0
        unique_ahmed_count = 0

        for i in range(len(google_results_list)):
            unified_results[google_results_list[i]] = 0
            if google_results_list[i] not in contextual_results_list and \
                    google_results_list[i] not in bing_results_list and \
                    google_results_list[i] not in faroo_results_list and \
                    google_results_list[i] not in ahmed_results_list:
                unique_google_count += 1
        for i in range(len(contextual_results_list)):
            if contextual_results_list[i] not in unified_results:
                unified_results[contextual_results_list[i]] = 0
                if contextual_results_list[i] not in google_results_list and \
                        contextual_results_list[i] not in bing_results_list and \
                        contextual_results_list[i] not in faroo_results_list and \
                        contextual_results_list[i] not in ahmed_results_list:
                    unique_contextual_count += 1
        for i in range(len(bing_results_list)):
            if bing_results_list[i] not in unified_results:
                unified_results[bing_results_list[i]] = 0
                if bing_results_list[i] not in google_results_list and \
                        bing_results_list[i] not in contextual_results_list and \
                        bing_results_list[i] not in faroo_results_list and \
                        bing_results_list[i] not in ahmed_results_list:
                    unique_bing_count += 1
        for i in range(len(faroo_results_list)):
            if faroo_results_list[i] not in unified_results:
                unified_results[faroo_results_list[i]] = 0
                if faroo_results_list[i] not in google_results_list and \
                        faroo_results_list[i] not in contextual_results_list and \
                        faroo_results_list[i] not in bing_results_list and \
                        faroo_results_list[i] not in ahmed_results_list:
                    unique_faroo_count += 1
        for i in range(len(ahmed_results_list)):
            if ahmed_results_list[i] not in unified_results:
                unified_results[ahmed_results_list[i]] = 0
                if ahmed_results_list[i] not in google_results_list and \
                        ahmed_results_list[i] not in contextual_results_list and \
                        ahmed_results_list[i] not in bing_results_list and \
                        ahmed_results_list[i] not in faroo_results_list:
                    unique_ahmed_count += 1

        unique_alt_count = unique_google_count + unique_bing_count + unique_contextual_count + unique_faroo_count + unique_ahmed_count
        total_alt_count = len(unified_results)
        math_expectation = len(google_results_list) / total_alt_count + len(contextual_results_list) / total_alt_count
        + len(bing_results_list) / total_alt_count + len(faroo_results_list) / total_alt_count + len(ahmed_results_list) / total_alt_count
        math_expectation /= 5
        math_expectation_of_squares = (len(google_results_list) / total_alt_count) ** 2 + (len(contextual_results_list) / total_alt_count) ** 2
        + (len(bing_results_list) / total_alt_count) ** 2 + (len(faroo_results_list) / total_alt_count) ** 2 + (len(ahmed_results_list) / total_alt_count) ** 2
        math_expectation_of_squares /= 5
        dispersion = math_expectation_of_squares - math_expectation ** 2
        x1 = dispersion
        print('Dispersion: ' + str(x1))
        x2 = 1 - dispersion
        google_serp_weight = 8 * (x1 * unique_google_count / unique_alt_count
                                  + x2 * len(google_results_list) / total_alt_count)
        contextual_weight = 2 * (x1 * unique_contextual_count / unique_alt_count
                                 + x2 * len(contextual_results_list) / total_alt_count)
        bing_weight = 3 * (x1 * unique_bing_count / unique_alt_count
                           + x2 * len(bing_results_list) / total_alt_count)
        faroo_weight = 3 * (x1 * unique_faroo_count / unique_alt_count
                            + x2 * len(faroo_results_list) / total_alt_count)
        google_ahmed_weight = 6 * (x1 * unique_ahmed_count / unique_alt_count
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

    @staticmethod
    def get_unified_results_condorcet_method_quality_weights(google_results_list, contextual_results_list,
                                                                 bing_results_list, faroo_results_list,
                                                                 ahmed_results_list):
        unified_results = {}

        unique_google_count = 0
        unique_contextual_count = 0
        unique_bing_count = 0
        unique_faroo_count = 0
        unique_ahmed_count = 0

        for i in range(len(google_results_list)):
            unified_results[google_results_list[i]] = {}
            if google_results_list[i] not in contextual_results_list and \
                        google_results_list[i] not in bing_results_list and \
                        google_results_list[i] not in faroo_results_list and \
                        google_results_list[i] not in ahmed_results_list:
                unique_google_count += 1
        for i in range(len(contextual_results_list)):
            if contextual_results_list[i] not in unified_results:
                unified_results[contextual_results_list[i]] = {}
                if contextual_results_list[i] not in google_results_list and \
                            contextual_results_list[i] not in bing_results_list and \
                            contextual_results_list[i] not in faroo_results_list and \
                            contextual_results_list[i] not in ahmed_results_list:
                    unique_contextual_count += 1
        for i in range(len(bing_results_list)):
            if bing_results_list[i] not in unified_results:
                unified_results[bing_results_list[i]] = {}
                if bing_results_list[i] not in google_results_list and \
                            bing_results_list[i] not in contextual_results_list and \
                            bing_results_list[i] not in faroo_results_list and \
                            bing_results_list[i] not in ahmed_results_list:
                    unique_bing_count += 1
        for i in range(len(faroo_results_list)):
            if faroo_results_list[i] not in unified_results:
                unified_results[faroo_results_list[i]] = {}
                if faroo_results_list[i] not in google_results_list and \
                            faroo_results_list[i] not in contextual_results_list and \
                            faroo_results_list[i] not in bing_results_list and \
                            faroo_results_list[i] not in ahmed_results_list:
                    unique_faroo_count += 1
        for i in range(len(ahmed_results_list)):
            if ahmed_results_list[i] not in unified_results:
                unified_results[ahmed_results_list[i]] = {}
                if ahmed_results_list[i] not in google_results_list and \
                            ahmed_results_list[i] not in contextual_results_list and \
                            ahmed_results_list[i] not in bing_results_list and \
                            ahmed_results_list[i] not in faroo_results_list:
                    unique_ahmed_count += 1

        unique_alt_count = unique_google_count + unique_bing_count + unique_contextual_count + unique_faroo_count + unique_ahmed_count
        total_alt_count = len(unified_results)
        x1 = 0.6
        x2 = 0.4

        google_serp_weight = 8 * (x1 * unique_google_count / unique_alt_count
                                      + x2 * len(google_results_list) / total_alt_count)
        contextual_weight = 2 * (x1 * unique_contextual_count / unique_alt_count
                                     + x2 * len(contextual_results_list) / total_alt_count)
        bing_weight = 3 * (x1 * unique_bing_count / unique_alt_count
                               + x2 * len(bing_results_list) / total_alt_count)
        faroo_weight = 3 * (x1 * unique_faroo_count / unique_alt_count
                                + x2 * len(faroo_results_list) / total_alt_count)
        google_ahmed_weight = 6 * (x1 * unique_ahmed_count / unique_alt_count
                                       + x2 * len(ahmed_results_list) / total_alt_count)

        total_weight = google_serp_weight + contextual_weight + bing_weight + faroo_weight + google_ahmed_weight
        google_serp_weight = google_serp_weight / total_weight
        contextual_weight = contextual_weight / total_weight
        bing_weight = bing_weight / total_weight
        faroo_weight = faroo_weight / total_weight
        google_ahmed_weight = google_ahmed_weight / total_weight

        for entry in unified_results.keys():
            for another_entry in unified_results.keys():
                if entry in google_results_list and another_entry in google_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(google_results_list)):
                        if google_results_list[i] == entry:
                            entry_rank = i
                        elif google_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += google_serp_weight
                        else:
                            unified_results[entry][another_entry] = google_serp_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= google_serp_weight
                        else:
                            unified_results[entry][another_entry] = -google_serp_weight
                if entry in contextual_results_list and another_entry in contextual_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(contextual_results_list)):
                        if contextual_results_list[i] == entry:
                            entry_rank = i
                        elif contextual_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += contextual_weight
                        else:
                            unified_results[entry][another_entry] = contextual_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= contextual_weight
                        else:
                            unified_results[entry][another_entry] = - contextual_weight
                if entry in bing_results_list and another_entry in bing_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(bing_results_list)):
                        if bing_results_list[i] == entry:
                            entry_rank = i
                        elif bing_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += bing_weight
                        else:
                            unified_results[entry][another_entry] = bing_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= bing_weight
                        else:
                            unified_results[entry][another_entry] = - bing_weight
                if entry in faroo_results_list and another_entry in faroo_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(faroo_results_list)):
                        if faroo_results_list[i] == entry:
                            entry_rank = i
                        elif faroo_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= faroo_weight
                        else:
                            unified_results[entry][another_entry] = faroo_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= faroo_weight
                        else:
                            unified_results[entry][another_entry] = - faroo_weight
                if entry in ahmed_results_list and another_entry in ahmed_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(ahmed_results_list)):
                        if ahmed_results_list[i] == entry:
                            entry_rank = i
                        elif ahmed_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += google_ahmed_weight
                        else:
                            unified_results[entry][another_entry] = google_ahmed_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= google_ahmed_weight
                        else:
                            unified_results[entry][another_entry] = - google_ahmed_weight
        for entry in unified_results.keys():
            sum = 0
            for another_entry in unified_results[entry].keys():
                # print(unified_results[entry])
                if unified_results[entry][another_entry] > 0:
                    sum += 1
                elif unified_results[entry][another_entry] < 0:
                    sum -= 1
            unified_results[entry] = sum

        ranked_unified_results = {}

        rank = len(unified_results)
        for entry in sorted(unified_results.items(), key=operator.itemgetter(1)):
            ranked_unified_results[entry[0]] = rank
            rank = rank - 1

        return ranked_unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight

    @staticmethod
    def get_unified_results_condorcet_method_stat_weights(google_results_list, contextual_results_list,
                                                             bing_results_list, faroo_results_list,
                                                             ahmed_results_list):
        unified_results = {}

        unique_google_count = 0
        unique_contextual_count = 0
        unique_bing_count = 0
        unique_faroo_count = 0
        unique_ahmed_count = 0

        for i in range(len(google_results_list)):
            unified_results[google_results_list[i]] = {}
            if google_results_list[i] not in contextual_results_list and \
                    google_results_list[i] not in bing_results_list and \
                    google_results_list[i] not in faroo_results_list and \
                    google_results_list[i] not in ahmed_results_list:
                unique_google_count += 1
        for i in range(len(contextual_results_list)):
            if contextual_results_list[i] not in unified_results:
                unified_results[contextual_results_list[i]] = {}
                if contextual_results_list[i] not in google_results_list and \
                        contextual_results_list[i] not in bing_results_list and \
                        contextual_results_list[i] not in faroo_results_list and \
                        contextual_results_list[i] not in ahmed_results_list:
                    unique_contextual_count += 1
        for i in range(len(bing_results_list)):
            if bing_results_list[i] not in unified_results:
                unified_results[bing_results_list[i]] = {}
                if bing_results_list[i] not in google_results_list and \
                        bing_results_list[i] not in contextual_results_list and \
                        bing_results_list[i] not in faroo_results_list and \
                        bing_results_list[i] not in ahmed_results_list:
                    unique_bing_count += 1
        for i in range(len(faroo_results_list)):
            if faroo_results_list[i] not in unified_results:
                unified_results[faroo_results_list[i]] = {}
                if faroo_results_list[i] not in google_results_list and \
                        faroo_results_list[i] not in contextual_results_list and \
                        faroo_results_list[i] not in bing_results_list and \
                        faroo_results_list[i] not in ahmed_results_list:
                    unique_faroo_count += 1
        for i in range(len(ahmed_results_list)):
            if ahmed_results_list[i] not in unified_results:
                unified_results[ahmed_results_list[i]] = {}
                if ahmed_results_list[i] not in google_results_list and \
                        ahmed_results_list[i] not in contextual_results_list and \
                        ahmed_results_list[i] not in bing_results_list and \
                        ahmed_results_list[i] not in faroo_results_list:
                    unique_ahmed_count += 1

        unique_alt_count = unique_google_count + unique_bing_count + unique_contextual_count + unique_faroo_count + unique_ahmed_count
        total_alt_count = len(unified_results) - 2
        math_expectation = len(google_results_list) / total_alt_count + len(contextual_results_list) / total_alt_count
        + len(bing_results_list) / total_alt_count + len(faroo_results_list) / total_alt_count + len(
            ahmed_results_list) / total_alt_count

        math_expectation /= 5
        math_expectation_of_squares = (len(google_results_list) / total_alt_count) ** 2 + (
                    len(contextual_results_list) / total_alt_count) ** 2
        + (len(bing_results_list) / total_alt_count) ** 2 + (len(faroo_results_list) / total_alt_count) ** 2 + (
                    len(ahmed_results_list) / total_alt_count) ** 2
        math_expectation_of_squares /= 5
        dispersion = math_expectation_of_squares - math_expectation ** 2
        x1 = dispersion
        print('Dispersion: ' + str(x1))
        x2 = 1 - dispersion

        google_serp_weight = 8 * (x1 * unique_google_count / unique_alt_count
                                  + x2 * len(google_results_list) / total_alt_count)
        contextual_weight = 2 * (x1 * unique_contextual_count / unique_alt_count
                                 + x2 * len(contextual_results_list) / total_alt_count)
        bing_weight = 3 * (x1 * unique_bing_count / unique_alt_count
                           + x2 * len(bing_results_list) / total_alt_count)
        faroo_weight = 3 * (x1 * unique_faroo_count / unique_alt_count
                            + x2 * len(faroo_results_list) / total_alt_count)
        google_ahmed_weight = 6 * (x1 * unique_ahmed_count / unique_alt_count
                                   + x2 * len(ahmed_results_list) / total_alt_count)

        total_weight = google_serp_weight + contextual_weight + bing_weight + faroo_weight + google_ahmed_weight
        google_serp_weight = google_serp_weight / total_weight
        contextual_weight = contextual_weight / total_weight
        bing_weight = bing_weight / total_weight
        faroo_weight = faroo_weight / total_weight
        google_ahmed_weight = google_ahmed_weight / total_weight

        for entry in unified_results.keys():
            for another_entry in unified_results.keys():
                if entry in google_results_list and another_entry in google_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(google_results_list)):
                        if google_results_list[i] == entry:
                            entry_rank = i
                        elif google_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += google_serp_weight
                        else:
                            unified_results[entry][another_entry] = google_serp_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= google_serp_weight
                        else:
                            unified_results[entry][another_entry] = -google_serp_weight
                if entry in contextual_results_list and another_entry in contextual_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(contextual_results_list)):
                        if contextual_results_list[i] == entry:
                            entry_rank = i
                        elif contextual_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += contextual_weight
                        else:
                            unified_results[entry][another_entry] = contextual_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= contextual_weight
                        else:
                            unified_results[entry][another_entry] = - contextual_weight
                if entry in bing_results_list and another_entry in bing_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(bing_results_list)):
                        if bing_results_list[i] == entry:
                            entry_rank = i
                        elif bing_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += bing_weight
                        else:
                            unified_results[entry][another_entry] = bing_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= bing_weight
                        else:
                            unified_results[entry][another_entry] = - bing_weight
                if entry in faroo_results_list and another_entry in faroo_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(faroo_results_list)):
                        if faroo_results_list[i] == entry:
                            entry_rank = i
                        elif faroo_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= faroo_weight
                        else:
                            unified_results[entry][another_entry] = faroo_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= faroo_weight
                        else:
                            unified_results[entry][another_entry] = - faroo_weight
                if entry in ahmed_results_list and another_entry in ahmed_results_list:
                    entry_rank = 0
                    another_entry_rank = 0
                    for i in range(len(ahmed_results_list)):
                        if ahmed_results_list[i] == entry:
                            entry_rank = i
                        elif ahmed_results_list[i] == another_entry:
                            another_entry_rank = i
                    if entry_rank < another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] += google_ahmed_weight
                        else:
                            unified_results[entry][another_entry] = google_ahmed_weight
                    elif entry_rank > another_entry_rank:
                        if another_entry in unified_results[entry]:
                            unified_results[entry][another_entry] -= google_ahmed_weight
                        else:
                            unified_results[entry][another_entry] = - google_ahmed_weight
        for entry in unified_results.keys():
            sum = 0
            for another_entry in unified_results[entry].keys():
                # print(unified_results[entry])
                if unified_results[entry][another_entry] > 0:
                    sum += 1
                elif unified_results[entry][another_entry] < 0:
                    sum -= 1
            unified_results[entry] = sum

        ranked_unified_results = {}

        rank = len(unified_results)
        for entry in sorted(unified_results.items(), key=operator.itemgetter(1)):
            ranked_unified_results[entry[0]] = rank
            rank = rank - 1

        return ranked_unified_results, google_serp_weight, contextual_weight, bing_weight, faroo_weight, google_ahmed_weight


import os
import json

labels_directory = r'C:\3D Datasets\dataset_org_norm\train'

"""
this piece of code is used to get all the labels from the MCB project and create a new_labels.json file which
contains all the labels and their respective search_query. the default query is just the label name formatted
with '+' and lower-cased.
"""


# used to gather the labels from the MCB project folder and save them to the labels json
def gather_labels(path):
    labels_dict = {'all_labels': []}
    for root, dirs, files in os.walk(os.path.abspath(path), topdown=False):
        for name in dirs:
            search_query = name.replace(' ', '+').lower()
            single_label = {'name': name, 'search_query': [search_query]}
            labels_dict['all_labels'].append(single_label)
    return labels_dict


def save_labels_json(labels_dict):
    json_string = json.dumps(labels_dict)
    json_file = open("new_labels.json", "w")
    json_file.write(json_string)
    json_file.close()


all_labels = gather_labels(labels_directory)
save_labels_json(all_labels)

from typing import Iterable, Dict
import multiprocessing

from apps.files_management.models import File, FileVersion
from apps.projects.models import Project, ProjectVersion

import pandas as pd
from lxml import etree as et
from tqdm import tqdm
import json
from functools import partial


NAMESPACES = {'tei': 'http://www.tei-c.org/ns/1.0', 'xml': 'http://www.w3.org/XML/1998/namespace'}


# pv = project version, fv = file version
def get_project_versions_files(project_id):
    project_versions = ProjectVersion.objects\
        .filter(project=project_id)\
        .order_by('id')

    get_fv_data = lambda fv: (fv.id, {'file': fv.file.name,
                                             'version': fv.number,
                                             'date': fv.creation_date,
                                             'author': fv.created_by.username})
    fv_hash = lambda fv: f'{fv.id}.{fv.number}'

    prev_files = set()
    data = []
    for idx, pv in enumerate(project_versions):
        files = pv.file_versions.all()
        modified_fv = filter(lambda fv: fv_hash(fv) not in prev_files, files)
        data.append({
            'version': str(pv),
            'date': pv.date,
            'files': tuple(map(get_fv_data, modified_fv))
            })
        prev_files = set(map(fv_hash, files))

    return data


def files_for_project_version(project: int, version: float)->Iterable[FileVersion]:
    [file_version_counter, commit_counter] = str(version).split('.')

    project_version = ProjectVersion.objects.get(
        project=project, 
        file_version_counter=file_version_counter,
        commit_counter=commit_counter)

    clean_xml = lambda xml: xml[len('<?xml version="1.0"?>'):] if xml.startswith('<?xml version="1.0"?>') else xml
    get_content = lambda fv: clean_xml(fv.get_rendered_content())

    file_contents = tuple((get_content(fv), fv.file.name) for fv in project_version.file_versions.all())

    #files_in_project_version = FileVersion.objects\
    #    .filter(file__in=project_version.project.files)\
    #    .filter(creation_date__le=project_version.date)\
    #    .distinct('file')

    return file_contents        


def create_summary_for_document(doc)->pd.DataFrame: 
    doc_raw, doc_name = doc
    doc_tree = et.fromstring(doc_raw.encode())

    header_tags = doc_tree.find('.//tei:teiHeader', namespaces=NAMESPACES).iter()
    body_tags = doc_tree.find('.//tei:text', namespaces=NAMESPACES).iter()

    stats_df = pd.DataFrame(columns=['document', 'tag', 'tag_id', 'location', 'attr_name', 'attr_value'])

    tag_count = 0
    for tag in header_tags:
        for attr_name, attr_value in tag.items():
            stats_df.loc[len(stats_df)] = {
                'document': doc_name,
                'tag': tag.tag,
                'tag_id': doc_name + str(tag_count),
                'location': 'header',
                'attr_name': attr_name,
                'attr_value': attr_value
            }
        tag_count += 1
        
    for tag in body_tags:
        for attr_name, attr_value in tag.items():
            stats_df.loc[len(stats_df)] = {
                'document': doc_name,
                'tag': tag.tag,
                'tag_id': doc_name + str(tag_count),
                'location': 'body',
                'attr_name': attr_name,
                'attr_value': attr_value
            }
        tag_count += 1

    return stats_df


def create_summary_for_document_collection(doc_gen: Iterable[str])->pd.DataFrame: 
    with multiprocessing.Pool() as p:
        stats_df = pd.concat(p.imap_unordered(create_summary_for_document, doc_gen))

    return stats_df

def get_tag_stats(row, n_docs, tag_g, attr_value_counts):
    return {
        'long_name': row[0],
        'name': row[0].split('}')[1] if '}' in row[0] else row[0],
        'count': int(row[1]['tag_id']['unique']),
        'coverage': float(round(100 * row[1]['document']['unique'] / n_docs, 2)),
        'distinct_doc_occurrences': int(row[1]['document']['unique']),
        'location': row[1]['location']['top'],
        'attributes': tuple({
                                'name': attr[0].split('}')[1] if '}' in attr[0] else attr[0],
                                'trend_percentage': float(round(round(
                                    100 * attr[1]['attr_value']['freq'] / attr[1]['attr_value']['count']),
                                    2)),
                                'trend_value': str(attr[1]['attr_value']['top']),
                                'distinct_values': int(attr_value_counts[row[0]][attr[0]].count()),
                                'coverage': float(
                                    round(100 * attr[1]['document']['count'] / row[1]['tag_id']['unique'],
                                          2)),
                                'values_json': json.dumps(
                                    list(attr_value_counts[row[0]][attr[0]].head().items()))
                            } for attr in
                            tag_g.get_group(row[0]).groupby('attr_name').describe().iterrows())
    }

def get_stats(stats_df):
    n_docs = len(stats_df['document'].unique())
    tag_g = stats_df.groupby('tag')
    tag_stats = tag_g.describe()
    attr_value_counts = stats_df \
                            .loc[:, ['tag', 'attr_name', 'attr_value']] \
        .groupby(['tag', 'attr_name']) \
        .attr_value \
        .value_counts()
    get_stats_fixed = partial(get_tag_stats, n_docs=n_docs, tag_g=tag_g, attr_value_counts=attr_value_counts)
    with multiprocessing.Pool() as p:
        stats = tuple(p.imap_unordered(get_stats_fixed, tag_stats.iterrows()))
    return stats

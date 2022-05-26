#!/usr/bin/env python3

import argparse
import datetime
import io
import json
import os
import pytz
import re
import requests
import sys
import uuid
from copy import copy
from dateutil.parser import parse as date_parse
from random import sample, randint, choice, random, shuffle
from xml.etree import ElementTree as ET

import lorem
from dicttoxml import dicttoxml
from faker import Faker


KOBO_CONF = 'kobo.json'


faker = Faker()


def get_config(asset_uid):
    if not os.path.exists(KOBO_CONF):
        print(f'Make sure you configure {KOBO_CONF} first.')
        sys.exit(1)

    with open('kobo.json', 'r') as f:
        conf = json.loads(f.read())

    token = conf['token']
    kf_url = conf['kf_url']
    kc_url = conf['kc_url']
    return {
        'data_url':f'{kf_url}/api/v2/assets/{asset_uid}/data',
        'asset_url':f'{kf_url}/api/v2/assets/{asset_uid}',
        'submission_url':f'{kc_url}/api/v1/submissions',
        'headers':{
            'Authorization': f'Token {token}'
        },
        'params':{
            'format': 'json'
        },
    }


def get_asset(asset_url, headers, params, *args, **kwargs):
    res = requests.get(asset_url, headers=headers, params=params)
    if res.status_code == 200:
        return res.json()


def submit_data(xml, _uuid, submission_url, headers, *args, **kwargs):
    file_tuple = (_uuid, io.BytesIO(xml))
    files = {'xml_submission_file': file_tuple}
    res = requests.Request(
        method='POST',
        url=submission_url,
        files=files,
        headers=headers,
    )
    session = requests.Session()
    res = session.send(res.prepare())
    return res.status_code


def get_uuid():
    return str(uuid.uuid4())


def get_instance_id(_uuid):
    return f'uuid:{_uuid}'


def get_version_id(deployment_data):
    return deployment_data['results'][0]['uid']


def get_version_string(deployment_data):
    count = deployment_data['count']
    date_obj = date_parse(deployment_data['results'][0]['date_deployed'])
    date_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return f"{count} ({date_str})"


def format_openrosa_datetime(dt=None):
    dt = dt or datetime.datetime.now(tz=pytz.UTC)
    if isinstance(dt, datetime.datetime):
        return dt.isoformat('T', 'milliseconds')
    elif isinstance(dt, datetime.time):
        return dt.isoformat('milliseconds')
    elif isinstance(dt, datetime.date):
        return dt.isoformat()
    return str(dt)


def get_point():
    def _get_item(s=0, e=1, r=6):
        return round(randint(s, e) * random(), r)
    lat = _get_item(-90, 90)
    lon = _get_item(-180, 180)
    return f'{lat} {lon} {_get_item(0,10, 1)} {_get_item(0,10, 1)}'


def get_random_datetime(_type='datetime'):
    dt = faker.date_time_between(start_date='-30y', end_date='now')
    dt = dt.astimezone(pytz.timezone(choice(pytz.all_timezones)))
    if _type == 'datetime':
        return format_openrosa_datetime(dt)
    if _type == 'time':
        return format_openrosa_datetime(dt.time())
    if _type == 'date':
        return format_openrosa_datetime(dt.date())


def get_asset_details(asset):
    return {
        'asset_uid':asset['uid'],
        'version':get_version_string(asset['deployed_versions']),
    }


def get_submission_misc(_uuid, deployment_data):
    return {
        'formhub':{'uuid':_uuid},
        '__version__':get_version_id(deployment_data),
        'meta':{'instanceID':get_instance_id(_uuid)}
    }


def get_submission_data(asset_content):
    survey = asset_content['survey']
    asset_choices = asset_content.get('choices', [])
    survey_choices = {}
    for item in asset_choices:
        ln = item['list_name']
        n = item['name']
        if ln not in survey_choices:
            survey_choices[ln] = [n]
        else:
            survey_choices[ln].append(n)

    result = {}
    for item in survey:
        name = item.get('name') or item.get('$autoname')
        if name is None:
            continue

        data_type = item.get('type')
        appearance = item.get('appearance')
        current_time = format_openrosa_datetime()

        choices = None
        if data_type in ['select_one', 'select_multiple']:
            choices = survey_choices[item['select_from_list_name']]

        # SELECT QUESTIONS
        if data_type == 'select_multiple':
            res = ' '.join(sample(choices, randint(0, len(choices))))
        elif data_type == 'select_one':
            res = choice(choices)
        elif data_type == 'rank':
            _choices = copy(choices)
            shuffle(_choices)
            res = ' '.join(_choices)

        # TEXT
        elif data_type == 'text':
            if appearance == 'multiline':
                res = lorem.get_sentence(count=randint(1, 20))
            else:
                res = lorem.get_word(count=randint(1, 5))

        # DATE AND TIME
        elif data_type in ['datetime', 'date', 'time']:
            res = get_random_datetime(data_type)

        # META
        elif data_type in ['start', 'end']:
            res = current_time

        # NUMBER QUESTIONS
        elif data_type in ['integer', 'range']:
            res = randint(0, 99999)
        elif data_type == 'decimal':
            res = round(random() * randint(0, 99999), randint(1,10))

        # GEO QUESTIONS
        elif data_type == 'geopoint':
            res = get_point()
        elif data_type == 'geotrace':
            res = ';'.join([get_point(), get_point()])
        elif data_type == 'geoshape':
            p1 = get_point()
            res = ';'.join(
                [p1] + [get_point() for _ in range(1, randint(2, 10))] + [p1]
            )

        result[name] = res

    return result


def get_submission(_uuid, asset):
    return {
        **get_submission_misc(_uuid, asset['deployed_versions']),
        **get_submission_data(asset['content'])
    }


def prepare_submission(asset):
    _uuid = get_uuid()

    asset_details = get_asset_details(asset)
    data = get_submission(_uuid, asset)

    xml = ET.fromstring(dicttoxml(data, attr_type=False))
    xml.tag = asset_details['asset_uid']
    xml.attrib = {
        'id': asset_details['asset_uid'],
        'version': asset_details['version'],
    }

    return ET.tostring(xml), _uuid


def main(asset_uid, count=1):
    config = get_config(asset_uid=asset_uid)
    asset = get_asset(**config)
    failure = 1
    res_codes = []
    for _ in range(count):
        xml, _uuid = prepare_submission(asset)
        res = submit_data(xml, _uuid, **config)
        if res == 201:
            success_current = len([rc == 201 for rc in res_codes])+1
            print(f'{_uuid}: Success # {success_current}')
        else:
            print(f'{_uuid}: Fail # {failure} ({res})')
            failure = failure + 1
        res_codes.append(res)

    successes = len([rc == 201 for rc in res_codes])
    print(
        f'{successes} successes of {count} tries to asset: {asset_uid}.'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='A CLI tool to submit random data to KoBo'
    )
    parser.add_argument('--asset-uid', '-a', type=str, help='Asset UID')
    parser.add_argument(
        '--count',
        '-c',
        type=int,
        default=1,
        help='Number of submissions to generate',
    )
    args = parser.parse_args()

    main(asset_uid=args.asset_uid, count=args.count)


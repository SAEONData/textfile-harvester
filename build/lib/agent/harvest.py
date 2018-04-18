import json
import logging
import os
import requests
from agent import config
# from agent.mapping import mapping

logger = logging.getLogger(__name__)


def handle_special_cases(indict, key, outdict):
    if key == 'DATE_ACQUIRED':
        date_dict = {'date': indict[key], 'dateType': 'Collected'}
        outdict['dates'].append(date_dict)
        title = "Landsat 8 Operational Land Imager and Thermal Infrared Sensor Collection 1 Level-1 {}".format(indict[key])
        title_dict = {'title': title, 'titleType': ''}
        outdict['titles'].append(title_dict)
    if key == 'FILE_DATE':
        date_dict = {'date': indict[key], 'dateType': 'Created'}
        outdict['dates'].append(date_dict)
        outdict['publicationYear'] = indict[key][:4]
    elif key == 'CORNER_UL_LAT_PRODUCT':
        if indict.get('CORNER_UL_LAT_PRODUCT') and \
           indict.get('CORNER_LL_LAT_PRODUCT') and \
           indict.get('CORNER_UL_LON_PRODUCT') and \
           indict.get('CORNER_LL_LON_PRODUCT'):
            outdict['geoLocations'] = [{
                'geoLocationBox': '{} {} {} {}'.format(
                    indict['CORNER_UL_LAT_PRODUCT'],
                    indict['CORNER_LL_LAT_PRODUCT'],
                    indict['CORNER_UL_LON_PRODUCT'],
                    indict['CORNER_LL_LON_PRODUCT'])}]
    elif key == 'LANDSAT_SCENE_ID':
        alt_dict = {
            'alternateIdentifier': indict[key],
            'dateType': 'Landsat Scene ID'}
        outdict['alternateIdentifiers'].append(alt_dict)
    return


def _parse_dict(indict):
    outdict = config.metadata_dict

    for key in indict:
        if key == 'DATE_ACQUIRED':
            date_dict = {'date': indict[key], 'dateType': 'Collected'}
            outdict['dates'].append(date_dict)
            title = "Landsat 8 Operational Land Imager and Thermal Infrared Sensor Collection 1 Level-1 {}".format(indict[key])
            title_dict = {'title': title, 'titleType': ''}
            outdict['titles'].append(title_dict)
        if key == 'FILE_DATE':
            date_dict = {'date': indict[key], 'dateType': 'Created'}
            outdict['dates'].append(date_dict)
            outdict['publicationYear'] = indict[key][:4]
        elif key == 'CORNER_UL_LAT_PRODUCT':
            if indict.get('CORNER_UL_LAT_PRODUCT') and \
               indict.get('CORNER_LL_LAT_PRODUCT') and \
               indict.get('CORNER_UL_LON_PRODUCT') and \
               indict.get('CORNER_LL_LON_PRODUCT'):
                outdict['geoLocations'] = [{
                    'geoLocationBox': '{} {} {} {}'.format(
                        indict['CORNER_UL_LAT_PRODUCT'],
                        indict['CORNER_LL_LAT_PRODUCT'],
                        indict['CORNER_UL_LON_PRODUCT'],
                        indict['CORNER_LL_LON_PRODUCT'])}]
        elif key == 'LANDSAT_SCENE_ID':
            alt_dict = {
                'alternateIdentifier': indict[key],
                'dateType': 'Landsat Scene ID'}
            outdict['alternateIdentifiers'].append(alt_dict)
        # Else ignore all others

    return outdict


def _harvest_file(filename):
    f = open(filename, 'r')
    rows = f.readlines()
    f.close()

    adict = dict()
    for row in rows:
        # print(row)
        row = row.strip()
        if row.startswith('GROUP'):
            continue
        if row.startswith('END'):
            continue
        row_list = row.split('=')
        if len(row_list) != 2:
            print('_harvest_file {}: cannot process row {}'.format(
                filename, row))
            # TODO
            continue
        key = row_list[0].strip()
        val = row_list[1].strip().strip('"')
        if key in adict:
            print('_harvest_file {}: dupliate key {}'.format(
                filename, key))
            continue
        adict[key] = val
        # print('"{}": ["value": "XXXXX", "default": "ZZZZZ"],'.format(key))
    # print(adict)
    return adict


def _upload_record(record, upload_server_url, upload_user, upload_password):
    output = {'success': False}

    data = {
        'jsonData': json.dumps(record),
        'metadataType': 'DataCite'
    }
    url = "{}/jsonCreateMetadataAsJson".format(upload_server_url)
    if config.upload_user:
        response = requests.post(
            url=url,
            data=data,
            auth=requests.auth.HTTPBasicAuth(
                config.upload_user, config.upload_password),
        )
    else:
        response = requests.post(
            url=url,
            data=data
        )
    if response.status_code != 200:
        output['error'] = 'Request failed with return code: %s' % (
            response.status_code)
        return output

    output['success'] = True
    output['results'] = response.text
    return output


def harvest(kwargs):
    output = {'success': False}
    source_dir = config.source_dir
    if kwargs.get('source_dir'):
        source_dir = kwargs.get('source_dir')

    if not os.path.exists(source_dir):
        output['error'] = 'source_dir {} does not exists'.format(
            source_dir)
        return output

    if os.listdir(source_dir) == []:
        output['error'] = 'source_dir {} is empty'.format(
            source_dir)
        return output

    upload_server_url = config.upload_server_url
    if kwargs.get('upload_server_url'):
        upload_server_url = kwargs.get('upload_server_url')

    upload_user = config.upload_user
    if kwargs.get('upload_user'):
        upload_user = kwargs.get('upload_user')

    upload_password = config.upload_password
    if kwargs.get('upload_password'):
        upload_password = kwargs.get('upload_password')

    results = []
    for filename in os.listdir(source_dir):
        print('Process file {}'.format(filename))
        afile = os.path.join(source_dir, filename)
        if not os.path.isfile(afile):
            print('Item {} is not a file'.format(filename))
            continue

        adict = _harvest_file(afile)
        datacite = _parse_dict(adict)
        result = _upload_record(
            datacite, upload_server_url, upload_user, upload_password)
        results.append(result)

    output['success'] = True
    output['results'] = results
    return output

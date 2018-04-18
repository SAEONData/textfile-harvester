#!/usr/bin/env python

import cherrypy
import xml.etree.ElementTree as ET
from agent.config import server_port
from agent.harvest import harvest
from agent.utils import get_request_host


class AgentAPI(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def harvest(self, **kwargs):
        output = {'success': False}
        response = harvest(kwargs)

        if not response['success']:
            output['error'] = response['error']
            return output

        output['success'] = True
        output['results'] = response['results']

        return output
        # data = {'param1': 'one'}
        # return Template(filename='agent/harvester.html').render(data=data)

    @cherrypy.expose
    def default(self, *args, **kwargs):
        request = cherrypy.request
        host = get_request_host(request)
        url = "http://{}".format(host)
        cherrypy.log('root')

        root = ET.Element("html")
        body = ET.SubElement(root, "body")
        child = ET.SubElement(body, "h2")
        child.text = 'Welcome to the SAEON Textfile Harvesting Agent'
        api = ET.SubElement(body, "h3")
        api.text = 'API'
        ET.SubElement(api, "br")
        search = ET.SubElement(api, "a", {
            'href': '{}/harvest'.format(url)
        })
        search.text = 'Harvest'
        child = ET.SubElement(api, "br")
        child = ET.SubElement(api, "span", {
            'style': 'font-size: 12'})
        child.text = "Harvest satellite textfiles and upload them into a SAEON CKAN metadata server"
        child = ET.SubElement(api, "br")
        child = ET.SubElement(api, "span", {
            'style': 'font-size: 12'})
        child.text = 'Arguments:'
        child = ET.SubElement(api, "br")
        child = ET.SubElement(api, "span", {
            'style': 'font-size: 12'})
        child.text = '* source_dir: the directory on the local file system where the text files reside'
        child = ET.SubElement(api, "br")
        child = ET.SubElement(api, "span", {
            'style': 'font-size: 12'})
        child.text = '* upload_server_url: URL of server to which harvested records are to be uploaded'
        child = ET.SubElement(api, "br")
        child = ET.SubElement(api, "span", {
            'style': 'font-size: 12'})
        child.text = '* upload_user: user name to access upload_server_url'
        child = ET.SubElement(api, "br")
        child = ET.SubElement(api, "span", {
            'style': 'font-size: 12'})
        child.text = '* upload_password: password of user to access upload_server_url'

        return ET.tostring(root)


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_port': server_port})
    cherrypy.config.update({'engine.autoreload.on': True})
    cherrypy.quickstart(AgentAPI(), '/')

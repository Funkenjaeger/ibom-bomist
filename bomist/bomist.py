import swagger_client as swagger_client
from swagger_client.rest import ApiException
import ast
import copy
from PySide6.QtCore import QAbstractItemModel, QObject


def ast_decorator(function):
    def wrapper(*args):
        api_response = function(*args)
        return ast.literal_eval(api_response)
    return wrapper


class BomistApi:
    def __init__(self):
        self.storage_api = swagger_client.StorageApi()
        self.parts_api = swagger_client.PartsApi()
        self.projects_api = swagger_client.ProjectsApi()
        self.inventory_api = swagger_client.InventoryApi()

    @ast_decorator
    def get_parts(self):
        return self.parts_api.get_parts()

    @ast_decorator
    def get_part(self, id):
        return self.parts_api.get_parts_id(id)

    @ast_decorator
    def get_all_storage(self):
        return self.storage_api.get_storage()

    @ast_decorator
    def get_storage(self, id):
        return self.storage_api.get_storage_id(id)

    @ast_decorator
    def get_projects(self):
        return self.projects_api.get_projects()

    @ast_decorator
    def get_project(self, id):
        return self.projects_api.get_projects_id(id)

    @ast_decorator
    def get_project_revs(self, id):
        return self.projects_api.get_projects_id_revs(id)

    @ast_decorator
    def get_project_bom(self, id, revid):
        return self.projects_api.get_projects_id_revs_revid_bom(id, revid)

    @ast_decorator
    def get_project_builds(self, id, revid):
        return self.projects_api.get_projects_id_revs_revid_builds(id, revid)

    @ast_decorator
    def get_project_build(self, id, revid, buildid):
        return self.projects_api.\
            get_projects_id_revs_revid_builds_buildid(id, revid, buildid)

    @ast_decorator
    def get_inventory(self, id):
        return self.inventory_api.get_inventory_id(id)

    def project_build_tree(self):
        projects = []
        projs = self.get_projects()
        for p in projs:
            proj = {}
            proj['mpn'] = p['project']['mpn']
            proj['id'] = p['project']['id']
            proj['revs'] = []
            projects.append(proj)
            revs = self.get_project_revs(proj['id'])
            for r in revs:
                rev = {}
                rev['revcode'] = r['project_rev']['revCode']
                rev['revid'] = r['project_rev']['id']
                rev['builds'] = []
                proj['revs'].append(rev)
                builds = self.get_project_builds(proj['id'], rev['revid'])
                for b in builds:
                    build = {}
                    build['buildcode'] = b['project_build']['code']
                    build['buildid'] = b['project_build']['id']
                    rev['builds'].append(build)
        return projects

    def build_components(self, id, revid, buildid):
        build = self.get_project_build(id, revid, buildid)
        components = []
        for c in build:
            component = self._build_component(c)
            for designator in component.designators:
                component_instance = copy.deepcopy(component)
                component_instance.designators = [designator]
                components.append(component_instance)
        # components = [self._build_component(c) for c in build]
        return components

    def _build_component(self, component):
        item = component['project_build_item']
        bom_entry = item['bom_entry']
        c = BuildComponent()
        c.designators = bom_entry['designators']
        c.dnp = bom_entry['dnp']
        c.source = item['source']
        if c.source != '':
            c.source = self.get_storage(c.source)[0]['storage']['fullName']
        if 'part' in item:
            part = item['part']
            c.value = part['value']
            c.package = part['package']
            c.mpn = part['mpn']
            c.manufacturer = part['manufacturer']
            c.label = part['label']
            c.description = part['description']
        else:
            c.value = bom_entry['value']
            c.package = bom_entry['package']
            c.mpn = ''
            c.manufacturer = ''
            c.label = None
            c.description = ''
        return c

class BuildComponent:
    def __init__(self):
        self.designators = []
        self.dnp = None
        self.source = ''
        self.value = ''
        self.package = ''
        self.mpn = ''
        self.manufacturer = ''
        self.label = ''
        self.description = ''
        self.source = ''

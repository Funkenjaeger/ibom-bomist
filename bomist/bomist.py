import swagger_client as swagger_client
import ast
import copy
import json
import attr
import typing


@attr.s
class BuildComponent(object):
    # def __init__(self):
    designators: typing.List[str] = attr.ib(factory=list)
    dnp: bool = attr.ib(default=False)
    source: str = attr.ib(default='')
    value: str = attr.ib(default='')
    package: str = attr.ib(default='')
    mpn: str = attr.ib(default='')
    manufacturer: str = attr.ib(default='')
    label: str = attr.ib(default='')
    description: str = attr.ib(default='')


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

    def get_build_by_names(self, mpn, revcode, buildcode):
        projects = self.get_projects()
        mpns = [self.get_part(p['project']['part'])[0]['part']['mpn']
                for p in projects]
        id = projects[mpns.index(mpn)]['project']['id']
        revs = self.get_project_revs(id)
        revcodes = [r['project_rev']['revCode'] for r in revs]
        revid = revs[revcodes.index(revcode)]['project_rev']['id']
        builds = self.get_project_builds(id, revid)
        buildcodes = [b['project_build']['code'] for b in builds]
        buildid = builds[buildcodes.index(buildcode)]['project_build']['id']
        return self.get_project_build(id, revid, buildid)

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


class BuildParser:
    def __init__(self):
        self.file_path = None
        self.bom_entries = []

    def parse(self, file_path):
        self.file_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            b = json.load(f)
            for entry in b:
                component = BuildComponent()
                component.designators = entry['bom_entry']['designators']
                component.dnp = entry['bom_entry']['dnp']
                component.source = entry['part']['storage']
                component.value = entry['bom_entry']['value']
                component.package = entry['bom_entry']['package']
                if 'part' in entry:
                    component.mpn = entry['part']['mpn']
                    component.manufacturer = entry['part'].get('manufacturer',
                                                               '')
                    component.label = entry['part']['label']
                    component.description = entry['part'].get('description', '')
                self.bom_entries.append(component)
            print('foo')

    def get_entry(self, designator):
        idxs = [idx for idx, x in enumerate(self.bom_entries)
                if designator in x.designators]
        if len(idxs) == 1:
            return self.bom_entries[idxs[0]]
        else:
            return None

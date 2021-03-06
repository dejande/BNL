'''
Copyright (c) 2013 Brookhaven National Laboratory

All rights reserved. Use is subject to license terms and conditions.

Created on Feb 17, 2014
@author: dejan.dezman@cosylab.com

'''

import sys
import time

if sys.version_info[0] != 2 or sys.version_info[1] < 6:
    print("This library requires at least Python version 2.6")
    sys.exit(1)

import requests
# _requests_version=[int(x) for x in requests.__version__.split('.')]
# if _requests_version[0] < 1 or sys.version_info[1] < 1:
#    print("This library requires at least Python-requests version 1.1.x")
#    sys.exit(1)

import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

from requests import auth
from requests import HTTPError

from copy import copy

import urllib

try:
    import json
except ImportError:
    import simplejson as json

from _conf import _conf


class SSLAdapter(HTTPAdapter):
    '''An HTTPS Transport Adapter that uses an arbitrary SSL version.'''
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version

        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=self.ssl_version)


class IDODSClient(object):
    '''
    IDODSClient provides a client connection object to perform
    save, retrieve, and update operations for the NSLS II insertion device online data service.
    '''

    def __init__(self, BaseURL=None, username=None, password=None):
        '''
        BaseURL = the url of the insertion device online data service
        username =
        password =
        '''
        # self.__jsonheader = {'content-type': 'application/json', 'accept': 'application/json'}
        self.__jsonheader = {'content-type': 'application/x-www-form-urlencoded', 'accept': 'application/json'}
        self.__resource = 'test/'

        try:
            self.__baseURL = self.__getdefaultconfig('BaseURL', BaseURL)
            self.__userName = self.__getdefaultconfig('username', username)
            self.__password = self.__getdefaultconfig('password', password)

            if self.__userName and self.__password:
                # self.__auth = (self.__userName, self.__password)
                self.__auth = auth.HTTPBasicAuth(self.__userName, self.__password)

            else:
                self.__auth = None

            self.__session = requests.Session()

            # specify ssl version. Use SSL v3 for secure connection, https.
            self.__session.mount('https://', SSLAdapter(ssl_version=ssl.PROTOCOL_SSLv3))

            requests.post(self.__baseURL + self.__resource, headers=copy(self.__jsonheader), auth=self.__auth).raise_for_status()
            # requests.get(self.__baseURL + self.__resource, headers=copy(self.__jsonheader), auth=self.__auth).raise_for_status()

        except Exception as e:
            raise Exception('Failed to create client: ' + str(e))

    def __getdefaultconfig(self, arg, value):
        if value is None and _conf.has_option('DEFAULT', arg):
            return _conf.get('DEFAULT', arg)
        else:
            return value

    def retrieveVendor(self, name, description=None):
        '''
        Retrieves vendor by its name and description
        Wildcard matching is supported for both name and description.

        :param name: vendor name
        :type name: str

        :param description: description for a vendor
        :type description: str

        :return: a map with structure:

            .. code-block:: python

                {'id': {
                    'id': ,
                    'name': ,
                    'description':
                    }
                 ...
                }

        :Raises: HTTPError
        '''

        # Try to retrieve vendor
        url = 'vendor/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveVendor(self, name, description=None):
        '''Saves vendor and its description into database

        :param name: vendor name
        :type name: str

        :param dtype: device type

        :param description: a brief description containing up to 255 characters
        :type description: str

        :return: a map with structure:

            .. code-block:: python

                {'id': vendor_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'savevendor/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateVendor(self, old_name, name, description=None):
        '''
        Updates vendor and its description

        :param name: vendor name
        :type name: str

        :param old_name: update vendor by its old name
        :type old_name: str

        :param description: a brief description containing up to 255 characters
        :type description: str

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatevendor/'

        # Set parameters
        params = {
            'vendor_id': None,
            'old_name': old_name,
            'name': name,
            'description': description
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveComponentType(self, name, description=None):
        '''
        Retrieves a component type using the key words:

        - name
        - description

        :param name: component type name
        :type name: str

        :param description: description for this device
        :type desctiprion: str

        :return: a map with structure:

            .. code-block: python

                {'id1':
                    {'id': device type id,
                    'name': device type name,
                    'description': device type description,
                    'prop1key': prop1value
                    ...
                    'propNkey': propNvalue
                    },
                 ...
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'cmpnttype/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveComponentType(self, name, description=None, props=None):
        '''Saves a component type using the key words:

        - name
        - description
        - props

        :param name: component type name
        :type name: str

        :param description: description for this device
        :type desctiprion: str

        :param props: component type properties
        :type props: python dict

        :return: a map with structure:

            .. code-block: python

                {'id': device type id}

        :Raises: HTTPError

        '''

        # Set URL
        url = 'savecmpnttype/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        # Add props
        if props:
            params['props'] = json.dumps(props)

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateComponentType(self, old_name, name, description=None, props=None):
        '''
        Updates description of a device type.
        Once a device type is saved, changes are not allowed since changes could cause potential colflicts.

        - old_name
        - name
        - description
        - props

        :param old_name: current component type name
        :type old_name: str

        :param name: device type name
        :type name: str

        :param description: description for this device
        :type desctiprion: str

        :param props: component type properties
        :type props: python dict

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatecmpnttype/'

        # Set parameters
        params = {
            'component_type_id': None,
            'old_name': old_name,
            'name': name,
            'description': description
        }

        # Add props
        if props:
            params['props'] = json.dumps(props)

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveComponentTypePropertyType(self, name):
        '''
        Retrieves component type property type by its name

        - name: property type name

        :return: a map with structure:

            .. code-block:: python

                {
                    'id': {
                        'id': ,              # int
                        'name': ,           # string
                        'description': ,    # string
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'cmpnttypeproptype/'

        # Set parameters
        params = {
            'name': name
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveComponentTypePropertyType(self, name, description=None):
        '''
        Inserts new component type property type into database

        - name: name of the component type property type M
        - description: description of the component type property type O

        :return: a map with structure:

            .. code-block:: python

                {'id': propertytypeid}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'savecmpnttypeproptype/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateComponentTypePropertyType(self, old_name, name, description=None):
        '''
        Inserts new component type property type into database

        - old_name: name of the component type property type we want to update M
        - name: name of the component type property type M
        - description: description of the component type property type O

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatecmpnttypeproptype/'

        # Set parameters
        params = {
            'property_type_id': None,
            'old_name': old_name,
            'name': name,
            'description': description
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveInventory(self, serial_no, cmpnt_type_name=None, vendor_name=None, name=None):
        '''
        Retrieves an insertion device from the inventory by device inventory name and type.
        Wildcard matching is supported for inventory name and device type. ::

            * for multiple character matching
            ? for single character matching


        :param serial_no: serial number
        :type serial_no: str

        :param cmpnt_type_name: component type name
        :type cmpnt_type_name: str

        :param vendor_name: vendor name
        :type vendor_name: str

        :param name: inventory name
        :type name: str

        :return: a map with structure:

            .. code-block:: python

                {'id': { 'name':,                       # string
                         'serialno':,                   # string
                         'cmpnt_type_name':             # string
                         'typeinto':                    # string
                         'vendor':,                     # string
                         'length': ,                    # float
                         'up_corrector_position': ,     # float
                         'middle_corrector_position': , # float
                         'down_corrector_position':,    # float
                         'gap_min': ,                   # float
                         'gap_max': ,                   # float
                         'gap_tolerance':,              # float
                         'phase1_min':,                 # float
                         'phase1_max':,                 # float
                         'phase2_min':,                 # float
                         'phase2_max':,                 # float
                         'phase3_min':,                 # float
                         'phase3_max':,                 # float
                         'phase4_min':,                 # float
                         'phase4_max':,                 # float
                         'phase_tolerance':,            # float
                         'k_max_linear':,               # float
                         'k_max_circular':,             # float
                         'phase_mode_p':,               # string
                         'phase_mode_a1':,              # string
                         'phase_mode_a2':               # string
                         'prop_keys':                   ['key1', 'key2']

                        }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'inventory/'

        # Set parameters
        params = {
            'serial_no': serial_no,
            'cmpnt_type_name': cmpnt_type_name,
            'vendor_name': vendor_name,
            'name': name
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInventory(self, serial_no, cmpnt_type_name, vendor_name, name=None, alias=None, props=None):
        '''
        Saves insertion device into the inventory using any of the acceptable key words:

        - name:  name to identify that device from vendor
        - cmpnt_type: device type name
        - alias: alias name, if applicable
        - serialno: serial number
        - vendor: vendor name
        - props: properties with structure as below

        .. code-block:: python

            {
                'length': ,                    # float
                'up_corrector_position': ,     # float
                'middle_corrector_position': , # float
                'down_corrector_position':,    # float
                'gap_min': ,                   # float
                'gap_max': ,                   # float
                'gap_tolerance':,              # float
                'phase1_min':,                 # float
                'phase1_max':,                 # float
                'phase2_min':,                 # float
                'phase2_max':,                 # float
                'phase3_min':,                 # float
                'phase3_max':,                 # float
                'phase4_min':,                 # float
                'phase4_max':,                 # float
                'phase_tolerance':,            # float
                'k_max_linear':,               # float
                'k_max_circular':,             # float
                'phase_mode_p':,               # string
                'phase_mode_a1':,              # string
                'phase_mode_a2':               # string
            }

        :param name: insertion device name, which is usually different from its field name (the name after installation).
        :type name: str

        :param cmpnt_type_name: component type name
        :type cmpnt_type_name: str

        :param alias: alias name, if applicable
        :type alias: str

        :param serial_no: serial number
        :type serial_no: str

        :param vendor: name of vendor
        :type vendor: str

        :param props: a map to describe the property of an insertion device as described above
        :type props: object

        :return: a map with structure:

            .. code-block:: python

                {'id': inventory_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saveinventory/'

        # Set parameters
        params = {
            'serial_no': serial_no,
            'cmpnt_type_name': cmpnt_type_name,
            'vendor_name': vendor_name,
            'alias': alias,
            'name': name
        }

        # Add props
        if props:
            params['props'] = json.dumps(props)

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInventory(self, inventory_id, serial_no=None, cmpnt_type_name=None, vendor_name=None, name=None, alias=None, props=None):
        '''
        Update inventory using any of the acceptable key words:

        - inventory_id:  inventory id from the database table
        - name:  name to identify that device from vendor
        - cmpnt_type_name: device type name
        - alias: alias name, if applicable
        - serial_no: serial number
        - vendor_name: vendor name
        - props: properties with structure as below

        .. code-block:: python

            {
                'length': ,                    # float
                'up_corrector_position': ,     # float
                'middle_corrector_position': , # float
                'down_corrector_position':,    # float
                'gap_min': ,                   # float
                'gap_max': ,                   # float
                'gap_tolerance':,              # float
                'phase1_min':,                 # float
                'phase1_max':,                 # float
                'phase2_min':,                 # float
                'phase2_max':,                 # float
                'phase3_min':,                 # float
                'phase3_max':,                 # float
                'phase4_min':,                 # float
                'phase4_max':,                 # float
                'phase_tolerance':,            # float
                'k_max_linear':,               # float
                'k_max_circular':,             # float
                'phase_mode_p':,               # string
                'phase_mode_a1':,              # string
                'phase_mode_a2':               # string
            }

        :param name: insertion device name, which is usually different from its field name (the name after installation).
        :type name: str

        :param cmpnt_type_name: component type name
        :type cmpnt_type_name: str

        :param alias: alias name, if applicable
        :type alias: str

        :param serial_no: serial number
        :type serial_no: str

        :param vendor_name: name of vendor
        :type vendor_name: str

        :param props: a map to describe the property of an insertion device as described above
        :type props: object

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updateinventory/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'serial_no': serial_no,
            'cmpnt_type_name': cmpnt_type_name,
            'vendor_name': vendor_name,
            'name': name,
            'alias': alias
        }

        # Add props
        if props:
            params['props'] = json.dumps(props)

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveInventoryPropertyTemplate(self, name, cmpnt_type_name=None):
        '''
        Retrieves inventory property template by its name

        :param name: Inventory property name
        :type name: str

        :param cmpnt_type_name: component type name
        :type cmpnt_type_name: str

        :return: a map with structure:

            .. code-block:: python

                {
                    'id': {
                        'id': ,              # int
                        'cmpnt_type_name': , # string
                        'name': ,            # string
                        'description': ,     # string
                        'default': ,         # string
                        'unit':              # string
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'inventoryproptmplt/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'name': name
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInventoryPropertyTemplate(self, cmpnt_type_name, name, description=None, default=None, unit=None):
        '''
        Inserts new inventory property template into database

        :param cmpnt_type_name: component type name M
        :type cmpnt_type_name: str

        :param name: property template name M
        :type name: str

        :param description: property template description O
        :type description: str

        :param default: property template default value O
        :type default: str

        :param unit: property template unit O
        :type unit: str

        :return: a map with structure:

            .. code-block:: python

                {'id': propertytemplateid}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saveinventoryproptmplt/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        # Add default
        if default:
            params['default'] = default

        # Add unit
        if unit:
            params['unit'] = unit

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInventoryPropertyTemplate(self, tmplt_id, cmpnt_type_name, name, description=None, default=None, unit=None):
        '''
        Updates inventory property template in a database

        :param tmplt_id: property template id M
        :type tmplt_id: int

        :param cmpnt_type_name: component type name M
        :type cmpnt_type_name: str

        :param name: property template name M
        :type name: str

        :param description: property template description O
        :type description: str

        :param default: property template default value O
        :type default: str

        :param unit: property template unit O
        :type unit: str

        :return: True if update succeeded

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updateinventoryproptmplt/'

        # Set parameters
        params = {
            'unit': unit,
            'default': default,
            'description': description,
            'tmplt_id': tmplt_id,
            'cmpnt_type_name': cmpnt_type_name,
            'name': name
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveInstall(self, name, description=None, cmpnt_type_name=None, coordinatecenter=None):
        '''Retrieves insertion device installation using any of the acceptable key words:

        :param name: installation name, which is its label in the field
        :type name: str

        :param description: installation description
        :type description: str

        :param cmpnt_type_name: component type name of the device
        :type cmpnt_type_name: str

        :param coordinatecenter: coordinate center number
        :type coordinatecenter: str

        :return: a map with structure:

            .. code-block:: python

                {'id': {
                        'id':                     #int,
                        'name':                   #string,
                        'description':            #string,
                        'cmpnt_type_name':             #string,
                        'cmpnt_type_description': #string,
                        'coordinatecenter':       #float,
                        'key1':                   #str,
                        ...
                        'prop_keys':              ['key1', 'key2']
                    }
                }

        :Raises: ValueError, MySQLError
        '''

        # Set URL
        url = 'install/'

        # Set parameters
        params = {
            'name': name,
            'description': description,
            'cmpnt_type_name': cmpnt_type_name,
            'coordinatecenter': coordinatecenter
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInsertionDevice(
            self, install_name=None, coordinate_center=None, project=None,
            beamline=None, beamline_desc=None, install_desc=None,
            inventory_name=None, down_corrector=None, up_corrector=None,
            length=None, gap_max=None, gap_min=None, gap_tolerance=None,
            phase1_max=None, phase1_min=None, phase2_max=None,
            phase2_min=None, phase3_max=None, phase3_min=None,
            phase4_max=None, phase4_min=None, phase_tolerance=None,
            k_max_circular=None, k_max_linear=None, phase_mode_a1=None,
            phase_mode_a2=None, phase_mode_p=None, type_name=None, type_desc=None
            ):
        '''
        Saves insertion device

        :param install_name: installation name
        :type install_name: str

        :param coordinate_center: coordinate center
        :type coordinate_center: float

        :param project: project name
        :type project: str

        :param beamline: beamline name
        :type beamline: str

        :param beamline_desc: beamline description
        :type beamline_desc: str

        :param install_desc: install description
        :type install_desc: str

        :param inventory_name: inventory name
        :type inventory_name: str

        :param down_corrector: inventory property down corrector
        :type down_corrector: str

        :param up_corrector: inventory property up corrector
        :type up_corrector: str

        :param length: inventory property length
        :type length: str

        :param gap_max: invnetory property gap maximum
        :type gap_max: str

        :param gap_min: inventory property gap minimum
        :type gap_min: str

        :param gap_tolerance: inventory property gap tolerance
        :type gap_tolerance: str

        :param phase1_max: inventory property phase1 maximum
        :type phase1_max: str

        :param phase1_min: inventory property phase1 minimum
        :type phase1_min: str

        :param phase2_max: inventory prperty phase2 maximum
        :type phase2_max: str

        :param phase2_min: inventory property phase2 minimum
        :type phase2_min: str

        :param phase3_max: inventory property phase3 maximum
        :type phase3_max: str

        :param phase3_min: inventory property phase3 minimum
        :type phase3_min: str

        :param phase4_max: inventory property phase4 maximum
        :type phase4_max: str

        :param phase4_min: inventory property phase4 minimum
        :type phase4_min: str

        :param phase_tolerance: inventory property phase tolerance
        :type phase_tolerance: str

        :param k_max_circular: inventory property k maximum circular
        :type k_max_circular: str

        :param k_max_linear: inventory property k maximum linear
        :type k_max_linear: str

        :param phase_mode_a1: inventory property phase mode a1
        :type phase_mode_a1: str

        :param phase_mode_a2: inventory property phase mode a2
        :type phase_mode_a2: str

        :param phase_mode_p: inventory property phase mode p
        :type phase_mode_p: str

        :param type_name: component type name
        :type type_name: str

        :param type_desc: component type description
        :type type_desc: str

        :return: True, if successful

        :raise: HTTPError
        '''

        # Set URL
        url = 'saveinsertiondevice/'

        # Set parameters
        params = {
            'install_name': install_name,
            'coordinate_center': coordinate_center,
            'project': project,
            'beamline': beamline,
            'beamline_desc': beamline_desc,
            'install_desc': install_desc,
            'inventory_name': inventory_name,
            'down_corrector': down_corrector,
            'up_corrector': up_corrector,
            'length': length,
            'gap_max': gap_max,
            'gap_min': gap_min,
            'gap_tolerance': gap_tolerance,
            'phase1_max': phase1_max,
            'phase1_min': phase1_min,
            'phase2_max': phase2_max,
            'phase2_min': phase2_min,
            'phase3_max': phase3_max,
            'phase3_min': phase3_min,
            'phase4_max': phase4_max,
            'phase4_min': phase4_min,
            'phase_tolerance': phase_tolerance,
            'k_max_circular': k_max_circular,
            'k_max_linear': k_max_linear,
            'phase_mode_a1': phase_mode_a1,
            'phase_mode_a2': phase_mode_a2,
            'phase_mode_p': phase_mode_p,
            'type_name': type_name,
            'type_desc': type_desc
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInstall(self, name, description=None, cmpnt_type_name=None, coordinatecenter=None):
        '''
        Saves insertion device installation

        :param name: installation name, which is its label in the field
        :type name: str

        :param description: installation description
        :type description: str

        :param cmpnt_type_name: component type of the device
        :type cmpnt_type_name: str

        :param coordinatecenter: coordinate center number
        :type coordinatecenter: float

        :raises:
            HTTPError

        :returns:
            {'id': new install id}
        '''

        # Set URL
        url = 'saveinstall/'

        # Set parameters
        params = {
            'name': name,
            'description': description,
            'cmpnt_type_name': cmpnt_type_name,
            'coordinatecenter': coordinatecenter
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInstall(self, old_name, name, description=None, cmpnt_type_name=None, coordinatecenter=None):
        '''
        Updates insertion device installation using any of the acceptable key words:

        :param old_name: installation name, which is its label in the field
        :type old_name: str

        :param name: installation name, which is its label in the field
        :type name: str

        :param description: installation description
        :type description: str

        :param cmpnt_type_name: component type of the device
        :type cmpnt_type_name: str

        :param coordinatecenter: coordinate center number
        :type coordinatecenter: float

        raises:
            HTTPError

        returns:
            True, if successful
        '''

        # Set URL
        url = 'updateinstall/'

        # Set parameters
        params = {
            'old_name': old_name,
            'name': name,
            'description': description,
            'cmpnt_type_name': cmpnt_type_name,
            'coordinatecenter': coordinatecenter
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInstallRelProperty(self, install_rel_parent, install_rel_child, install_rel_property_type_name, install_rel_property_value):
        '''
        Saves install relationahip property into database

        :param install_rel_parent: name of the parent in the install relationship
        :type install_rel_parent: str

        :param install_rel_child: name of the child in the install relationship
        :type install_rel_child: str

        :param install_rel_property_type_name: name of the install relationship property type
        :type install_rel_property_type_name: str

        :param install_rel_property_value: value of the install relationship property
        :type install_rel_property_value: str

        :raises: HTTPError

        :returns: {'id': new install rel property id}
        '''

        # Set URL
        url = 'saveinstallrelprop/'

        # Set parameters
        params = {
            'install_rel_parent': install_rel_parent,
            'install_rel_child': install_rel_child,
            'install_rel_property_type_name': install_rel_property_type_name,
            'install_rel_property_value': install_rel_property_value
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInstallRelProperty(self, install_rel_parent, install_rel_child, install_rel_property_type_name, install_rel_property_value):
        '''
        Updates install relationship property in the database

        :param install_rel_parent: name of the parent in the install relationship
        :type install_rel_parent: str

        :param install_rel_child: name of the child in the install relationship
        :type install_rel_child: str

        :param install_rel_property_type_name: name of the install relationship property type
        :type install_rel_property_type_name: str

        :param install_rel_property_value: value of the install relationship property
        :type install_rel_property_value: str

        :raises: HTTPError

        :returns: True, if successful
        '''

        # Set URL
        url = 'updateinstallrelprop/'

        # Set parameters
        params = {
            'install_rel_parent': install_rel_parent,
            'install_rel_child': install_rel_child,
            'install_rel_property_type_name': install_rel_property_type_name,
            'install_rel_property_value': install_rel_property_value
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveInstallRel(self, install_rel_id=None, parent_install=None, child_install=None, description=None, order=None, date=None, expected_property=None):
        '''
        Retrieves install relationship from the database. A specific relationship can be retrieved or all the children of a specific parent or
        all the parents of a specific child.

        :param install_rel_id: id of the install_rel table
        :type install_rel_id: int

        :param parent_install: name of the parent install element
        :type parent_install: str

        :param child_install: name of the child install element
        :type child_install: str

        :param description: description of a relationship
        :type description: str

        :param order: order number of child element in the parent element; accepts a range in a tuple
        :type order: order number of child element in the parent element; accepts a range in a tuple

        :param date: date of the device installation; accepts a range in a tuple
        :type date: str

        :param expected_property: if we want to search for relationships with a specific property set to a specific value, we
              can prepare a dict and pass it to the function e.g. {'beamline': 'xh*'} will return all of the
              beamlines with names starting with xh or {'beamline': None} will return all of the beamlines

        :type expected_property: dict

        :return: a map with structure:

            .. code-block: python

                {
                    'id': {
                        'id':           #int,
                        'parentid':     #int,
                        'parentname':   #string,
                        'childid':      #int,
                        'childname':    #string,
                        'description':  #string,
                        'order':        #int,
                        'date':         #string,
                        'prop1key':     #string,
                        ...
                        'propNkey':     #string
                    }
                }

        :raises: HTTPError
        '''

        # Set URL
        url = 'installrel/'

        # Set parameters
        params = {
            'install_rel_id': install_rel_id,
            'parent_install': parent_install,
            'child_install': child_install,
            'description': description,
            'order': order,
            'date': date
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInstallRel(self, parent_install, child_install, description=None, order=None, props=None):
        '''
        Saves install relationship in the database.

        :param parent_install: id of the parent element
        :type parent_install: int

        :param child_install: id of the child element
        :type child_install: int

        :param description: description of the relationship
        :type description: str

        :param order: order of the child in the relationship
        :type order: int

        :param props: dict structure:

            .. code-block: python

                {
                    'key1': 'value1',
                    ...
                    'keyN': 'valueN'
                }

        :type props: dict

        :return: a map with structure:

            .. code-block: python

                {'id': id of the saved install rel}

        :raises: HTTPError
        '''

        # Set URL
        url = 'saveinstallrel/'

        # Set parameters
        params = {
            'parent_install': parent_install,
            'child_install': child_install
        }

        # Add description
        if description:
            params['description'] = description

        # Add order
        if order:
            params['order'] = order

        # Add props
        if props:
            params['props'] = json.dumps(props)

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInstallRel(self, parent_install, child_install, description=None, order=None, props=None):
        '''
        Updates install relationship.

        :param parent_install: name of the parent element we want to update
        :type parent_install: str

        :param child_install: name of the child element we want to update
        :type child_install: str

        :param description: description of the relationship
        :type description: str

        :param order: order of the child in the relationship
        :type order: int

        :param props: dict structure

            .. code-block:: python

                {
                    'key1': 'value1',
                    ...
                    'keyN': 'valueN'
                }

        :type props: dict

        returns:
            True, if successful

        raises:
            HTTPError
        '''

        # Set URL
        url = 'updateinstallrel/'

        # Set parameters
        params = {
            'parent_install': parent_install,
            'child_install': child_install,
            'description': description,
            'order': order
        }

        # Add props
        if props:
            params['props'] = json.dumps(props)

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveInstallRelPropertyType(self, name):
        '''
        Retrieves install relationship property type by its name

        - name: property type name

        :return: a map with structure:

            .. code-block:: python

                {
                    'id': {
                        'id': ,             # int
                        'name': ,           # string
                        'description': ,    # string
                        'unit': ,          # string
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'installrelproptype/'

        # Set parameters
        params = {
            'name': name
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInstallRelPropertyType(self, name, description=None, unit=None):
        '''
        Inserts new install relationship property type into database

        - name: name of the install relationship property type M
        - description: description of the install relationship property type O
        - unit: unit used for this property type O

        :return: a map with structure:

            .. code-block:: python

                {'id': propertytypeid}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saveinstallrelproptype/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        # Add unit
        if unit:
            params['unit'] = unit

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInstallRelPropertyType(self, old_name, name, description=None, unit=None):
        '''
        Updates install relationship property type

        :param old_name: name of the install relationship property type we want to update O
        :type old_name: str

        :param name: name of the install relationship property type M
        :type name: str

        :param description: description of the install relationship property type O
        :type description: str

        :param unit: units used for this property type O
        :type unit: str

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updateinstallrelproptype/'

        # Set parameters
        params = {
            'old_name': old_name,
            'name': name,
            'description': description,
            'unit': unit
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveInventoryToInstall(self, inventory_to_install_id, install_name, inventory_id):
        '''
        Retrieves installed devices or specific map

        :param inventory_to_install_id: id of the inventory to the install map
        :type inventory_to_install_id: int

        :param install_name: label name after installation
        :type install_name: str

        :param inventory_id: id in inventory
        :type inventory_id: int
        :type inv_name: str

        :return: a map with structure:

            .. code-block:: python

                {'id': {
                        'id': #int,
                        'installid': #int,
                        'installname': #string,
                        'inventoryid': #int,
                        'inventoryname': #string
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'inventorytoinstall/'

        # Set parameters
        params = {
            'inventory_to_install_id': inventory_to_install_id,
            'install_name': install_name,
            'inventory_id': inventory_id
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveInventoryToInstall(self, install_name, inventory_id):
        '''
        Links a device as installed after it is installed into field using the key words:

        :param install_name: label name after installation
        :type install_name: str

        :param inventory_id: id in its inventory
        :type inventory_id: int

        :return: a map with structure:

            .. code-block:: python

                {'id': id of new inventorytoinstall record}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saveinventorytoinstall/'

        # Set parameters
        params = {
            'install_name': install_name,
            'inventory_id': inventory_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateInventoryToInstall(self, inventory_to_install_id, install_name, inventory_id):
        '''
        Updates a device as installed when its installation has been changed using the key words:

        :param install_name: label name after installation
        :type install_name: str

        :param inventory_id: id in its inventory
        :type inventory_id: int

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updateinventorytoinstall/'

        # Set parameters
        params = {
            'inventory_to_install_id': inventory_to_install_id,
            'install_name': install_name,
            'inventory_id': inventory_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveDataMethod(self, name, description=None):
        '''Retrieves a method name and its description which is used when producing a data set for an insertion device.

        :param name: name of the method
        :type name: str

        :param description: description of this method
        :type description: str

        :return: a map with structure:

            .. code-block:: python

                {'id':
                    {'id': data method id,
                     'name': method name,
                     'description': description of this method
                    }
                }

        :Raises: HTTPError
        '''

        # Try to retrieve data method
        url = 'datamethod/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveDataMethod(self, name, description=None):
        '''Saves a method with its description which is used when producing a data set for an insertion device.

        :param name: name of the method
        :type name: str

        :param description: description of this method
        :type description: str

        :return: a map with structure:

            .. code-block:: python

                {'id': method_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'savedatamethod/'

        # Set parameters
        params = {
            'name': name
        }

        # Add description
        if description:
            params['description'] = description

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateDataMethod(self, old_name, name, description=None):
        '''
        Updates the data method by id or name.

        :param datamethod_id: id of the data method we want to update 
        :type datamethod_id: int

        :param old_name: name of the method we want to update 
        :type old_name: str

        :param name: name of the method
        :type name: str

        :param description: description of this method
        :type description: str

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatedatamethod/'

        # Set parameters
        params = {
            'datamethod_id': None,
            'old_name': old_name,
            'name': name,
            'description': description
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveOfflineData(self, **kws):
        '''
        Retrieves insertion device offline data using any of the acceptable key words:

        - offlineid
        - description
        - gap
        - phase1
        - phase2
        - phase3
        - phase4
        - phasemode
        - polarmode
        - status
        - method_name
        - inventory_id
        - with_data

        :param offlineid: id of the offline data we want to retrieve
        :type offlineid: int

        :param description: a brief description for this data entry
        :type description: str

        :param gap: gap when this data set was produced
        :type gap: float

        :param phase1: phase 1 when this data set was produced
        :type phase1: float

        :param phase2: phase 2 when this data set was produced
        :type phase2: float

        :param phase3: phase 3 when this data set was produced
        :type phase3: float

        :param phase4: phase 4 when this data set was produced
        :type phase4: float

        :param phasemode: description for the mode of phase, which is determined by gap/phase
        :type phasemode: str

        :param polarmode: description for the mode of polar, which is determined by gap/phase
        :type polarmode: str

        :param status: status of this data set
        :type status: int

        :param method_name: name of method used to produce the data
        :type method_name: str

        :param inventory_id: id of inventory used to produce the data
        :type inventory_id: int

        :param with_data: Should data be returned together with the result?
        :type with_data: True/False

        :return: a map with structure:

            .. code-block:: python

                {'offlinedata_id': {
                        'username': ,      # string
                        'description': ,   # string
                        'date': ,          # timestamp
                        'gap':,            # float
                        'phase1': ,        # float
                        'phase2': ,        # float
                        'phase3':,         # float
                        'phase4':,         # float
                        'phasemode':,      # string
                        'polarmode':,      # string
                        'status':,         # int
                        'data_file_name':, # string
                        'data_file_ts':,   # string
                        'data_id':,        # int
                        'script_name':,    # string
                        'script':,         # string
                        'method_name':,    # string
                        'methoddesc':,     # string
                        'inventory_name':, # string
                        'inventory_id':,   # int
                        'data':            # string, base64 encoded file content
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'offlinedata/'

        # Set parameters
        params = {}

        # Add offline id
        if 'offlineid' in kws:
            params['offlineid'] = kws['offlineid']

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add gap
        if 'gap' in kws:
            params['gap'] = kws['gap']

        # Add phase1
        if 'phase1' in kws:
            params['phase1'] = kws['phase1']

        # Add phase2
        if 'phase2' in kws:
            params['phase2'] = kws['phase2']

        # Add phase3
        if 'phase3' in kws:
            params['phase3'] = kws['phase3']

        # Add phase4
        if 'phase4' in kws:
            params['phase4'] = kws['phase4']

        # Add phasemode
        if 'phasemode' in kws:
            params['phasemode'] = kws['phasemode']

        # Add polarmode
        if 'polarmode' in kws:
            params['polarmode'] = kws['polarmode']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add method name
        if 'method_name' in kws:
            params['method_name'] = kws['method_name']

        # Add inventory id
        if 'inventory_id' in kws:
            params['inventory_id'] = kws['inventory_id']

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        returnData = r.json()

        # Append data if with_data is set
        if 'with_data' in kws and kws['with_data'] is True:

            # Set URL
            url = 'rawdata/'

            # Go through all returned offline data and append data
            offlineDataKeys = returnData.keys()

            for key in offlineDataKeys:
                offlineData = returnData[key]

                # Set parameters
                params = {
                    'raw_data_id': offlineData['data_id']
                }

                result = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
                self.__raise_for_status(r.status_code, r.text)
                resultData = result.json()

                resultKeys = resultData.keys()
                resultObject = resultData[resultKeys[0]]
                returnData[key]['data'] = resultObject['data']

        return returnData

    def retrieveInstallOfflineData(self, install_name, **kws):
        '''
        Retrieves insertion device offline data using any of the acceptable key words:

        - install_name
        - description
        - date
        - gap
        - phase1
        - phase2
        - phase3
        - phase4
        - phasemode
        - polarmode
        - status
        - method_name
        - with_data

        :param description: a brief description for this data entry
        :type description: str

        :param date: offline data date
        :type date: str

        :param gap: gap when this data set was produced
        :type gap: float

        :param phase1: phase 1 when this data set was produced
        :type phase1: float

        :param phase2: phase 2 when this data set was produced
        :type phase2: float

        :param phase3: phase 3 when this data set was produced
        :type phase3: float

        :param phase4: phase 4 when this data set was produced
        :type phase4: float

        :param phasemode: description for the mode of phase, which is determined by gap/phase
        :type phasemode: str

        :param polarmode: description for the mode of polar, which is determined by gap/phase
        :type polarmode: str

        :param status: status of this data set
        :type status: int

        :param method_name: name of method used to produce the data
        :type method_name: str

        :param install_name: name of install item
        :type install_name: str

        :param with_data: Should data be returned together with the result?
        :type with_data: True/False

        :return: a map with structure:

            .. code-block:: python

                {'offlinedata_id': {
                        'install_name': ,  # string
                        'username': ,      # string
                        'description': ,   # string
                        'date': ,          # timestamp
                        'gap':,            # float
                        'phase1': ,        # float
                        'phase2': ,        # float
                        'phase3':,         # float
                        'phase4':,         # float
                        'phasemode':,      # string
                        'polarmode':,      # string
                        'status':,         # int
                        'data_file_name':, # string
                        'data_file_ts':,   # string
                        'data_id':,        # int
                        'script_name':,    # string
                        'script':,         # string
                        'method_name':,    # string
                        'methoddesc':,     # string
                        'inventory_name':, # string
                        'data':            # string, base64 encoded file content
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'offlinedatainstall/'

        # Set parameters
        params = {
            'install_name': install_name
        }

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add date
        if 'date' in kws:
            params['date'] = kws['date']

        # Add gap
        if 'gap' in kws:
            params['gap'] = kws['gap']

        # Add phase1
        if 'phase1' in kws:
            params['phase1'] = kws['phase1']

        # Add phase2
        if 'phase2' in kws:
            params['phase2'] = kws['phase2']

        # Add phase3
        if 'phase3' in kws:
            params['phase3'] = kws['phase3']

        # Add phase4
        if 'phase4' in kws:
            params['phase4'] = kws['phase4']

        # Add phasemode
        if 'phasemode' in kws:
            params['phasemode'] = kws['phasemode']

        # Add polarmode
        if 'polarmode' in kws:
            params['polarmode'] = kws['polarmode']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add method name
        if 'method_name' in kws:
            params['method_name'] = kws['method_name']

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        returnData = r.json()

        # Append data if with_data is set
        if 'with_data' in kws and kws['with_data'] is True:

            # Set URL
            url = 'rawdata/'

            # Go through all returned offline data and append data
            offlineDataKeys = returnData.keys()

            for key in offlineDataKeys:
                offlineData = returnData[key]

                # Set parameters
                params = {
                    'raw_data_id': offlineData['data_id']
                }

                result = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
                self.__raise_for_status(r.status_code, r.text)
                resultData = result.json()

                resultKeys = resultData.keys()
                resultObject = resultData[resultKeys[0]]
                returnData[key]['data'] = resultObject['data']

        return returnData

    def saveMethodAndOfflineData(
            self, inventory_id, method=None,
            method_desc=None, data_desc=None, data_file_name=None,
            data_file_path=None, status=None, gap=None, phase1=None, phase2=None,
            phase3=None, phase4=None, phase_mode=None, polar_mode=None
            ):
        '''
        Saves data method and offline data into the database

        :param inventory_id: inventory id
        :type inventory_id: int

        :param username: username of the user who saved the offline data
        :type username: str

        :param method: data method name
        :type method: str

        :param method_desc: data method description
        :type method_desc: str

        :param data_desc: offline data description
        :type data_desc: str

        :param data_file_name: data file name
        :type data_file_name: str

        :param data_id: id of the saved raw data
        :type data_id: int

        :param status: is offline data Active = 1 or Obsolete - 0
        :type status: int

        :param gap: gap
        :type gap: float

        :param phase1: phase1
        :type phase1: float

        :param phase2: phase2
        :type phase2: float

        :param phase3: phase3
        :type phase3: float

        :param phase4: phase4
        :type phase4: float

        :param phase_mode: phase mode
        :type phase_mode: str

        :param polar_mode: polar mode
        :type polar_mode: str

        :return: a map with structure:

            .. code-block:: python

                {'id': offline_data_id}

        :raise: HTTPError
        '''

        # Set URL
        url = 'savemethodofflinedata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'method': method,
            'method_desc': method_desc,
            'data_desc': data_desc,
            'data_file_name': data_file_name,
            'status': status,
            'gap': gap,
            'phase1': phase1,
            'phase2': phase2,
            'phase3': phase3,
            'phase4': phase4,
            'phase_mode': phase_mode,
            'polar_mode': polar_mode
        }

        fileName = data_file_path

        with open(fileName, 'rb') as f:
            ur = self.__session.post(self.__baseURL+'saverawdata/', files={'file': f}, auth=self.__auth)
            self.__raise_for_status(ur.status_code, ur.text)

        params['data_id'] = ur.json()['id']

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveOfflineData(self, inventory_id, **kws):
        '''
        Saves insertion device offline data using any of the acceptable key words:

        - inventory_id
        - username
        - description
        - gap
        - phase1
        - phase2
        - phase3
        - phase4
        - phasemode
        - polarmode
        - status
        - data_file_name
        - data_file_ts
        - data
        - script_name
        - script
        - method_name

        :param inventory_id: name of the inventory that the offline data is connected to
        :type inventory_id: str

        :param username: author who first created this data entry 
        :type username: str

        :param description: a brief description for this data entry
        :type description: str

        :param gap: gap when this data set was produced
        :type gap: float

        :param phase1: phase 1 when this data set was produced
        :type phase1: float

        :param phase2: phase 2 when this data set was produced
        :type phase2: float

        :param phase3: phase 3 when this data set was produced
        :type phase3: float

        :param phase4: phase 4 when this data set was produced
        :type phase4: float

        :param phasemode: description for the mode of phase, which is determined by gap/phase
        :type phasemode: str

        :param polarmode: description for the mode of polar, which is determined by gap/phase
        :type polarmode: str

        :param status: status of this data set
        :type status: int

        :param data_file_name: file name of the data
        :type data_file_name: str

        :param data_file_ts: time stamp of data file with format like "YYYY-MM-DD HH:MM:SS"
        :type data_file_ts: str

        :param data: real data dumped into JSON string
        :type data: str

        :param script_name: name of script to produce the data
        :type script_name: str

        :param script: script to produce the data
        :type script: str

        :param method_name: name of method used to produce the data
        :type method_name: str

        :return: a map with structure:

            .. code-block:: python

                {'id': offline_data_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saveofflinedata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id
        }

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add username
        if 'username' in kws:
            params['username'] = kws['username']

        # Add gap
        if 'gap' in kws:
            params['gap'] = kws['gap']

        # Add phase1
        if 'phase1' in kws:
            params['phase1'] = kws['phase1']

        # Add phase2
        if 'phase2' in kws:
            params['phase2'] = kws['phase2']

        # Add phase3
        if 'phase3' in kws:
            params['phase3'] = kws['phase3']

        # Add phase4
        if 'phase4' in kws:
            params['phase4'] = kws['phase4']

        # Add phasemode
        if 'phasemode' in kws:
            params['phasemode'] = kws['phasemode']

        # Add polarmode
        if 'polarmode' in kws:
            params['polarmode'] = kws['polarmode']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add data file name
        if 'data_file_name' in kws:
            params['data_file_name'] = kws['data_file_name']

        # Add data file timestamp
        if 'data_file_ts' in kws:
            params['data_file_ts'] = kws['data_file_ts']

        # Add data
        if 'data' in kws:
            fileName = kws['data']

            with open(fileName, 'rb') as f:
                ur = self.__session.post(self.__baseURL+'saverawdata/', files={'file': f}, auth=self.__auth)
                self.__raise_for_status(ur.status_code, ur.text)

            params['data_id'] = ur.json()['id']

        # Add script_name
        if 'script_name' in kws:
            params['script_name'] = kws['script_name']

        # Add script
        if 'script' in kws:
            params['script'] = kws['script']

        # Add method name
        if 'method_name' in kws:
            params['method_name'] = kws['method_name']

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateOfflineData(self, offline_data_id, **kws):
        '''
        Updates insertion device offline data by its id

        parameters:
        - inventory_id
        - username
        - description
        - gap
        - phase1
        - phase2
        - phase3
        - phase4
        - phasemode
        - polarmode
        - status
        - data_file_name
        - data_file_ts
        - data
        - script_name
        - script
        - method_name

        :param inventory_id: id of the inventory that the offline data is connected to
        :type inventory_id: int

        :param username: author who first created this data entry 
        :type username: str

        :param description: a brief description for this data entry
        :type description: str

        :param gap: gap when this data set was produced
        :type gap: float

        :param phase1: phase 1 when this data set was produced
        :type phase1: float

        :param phase2: phase 2 when this data set was produced
        :type phase2: float

        :param phase3: phase 3 when this data set was produced
        :type phase3: float

        :param phase4: phase 4 when this data set was produced
        :type phase4: float

        :param phasemode: description for the mode of phase, which is determined by gap/phase
        :type phasemode: str

        :param polarmode: description for the mode of polar, which is determined by gap/phase
        :type polarmode: str

        :param status: status of this data set
        :type status: int

        :param data_file_name: file name of the data
        :type data_file_name: str

        :param data_file_ts: time stamp of data file with format like "YYYY-MM-DD HH:MM:SS"
        :type data_file_ts: str

        :param data: real data dumped into JSON string
        :type data: str

        :param script_name: name of script to produce the data
        :type script_name: str

        :param script: script to produce the data
        :type script: str

        :param method_name: name of method used to produce the data
        :type method_name: str

        :return: True, if successful

        :Raises: HTTPError
        '''
        # Set URL
        url = 'updateofflinedata/'

        # Set parameters
        params = {
            'offline_data_id': offline_data_id
        }

        # Add inventory id
        if 'inventory_id' in kws:
            params['inventory_id'] = kws['inventory_id']

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add username
        if 'username' in kws:
            params['username'] = kws['username']

        # Add gap
        if 'gap' in kws:
            params['gap'] = kws['gap']

        # Add phase1
        if 'phase1' in kws:
            params['phase1'] = kws['phase1']

        # Add phase2
        if 'phase2' in kws:
            params['phase2'] = kws['phase2']

        # Add phase3
        if 'phase3' in kws:
            params['phase3'] = kws['phase3']

        # Add phase4
        if 'phase4' in kws:
            params['phase4'] = kws['phase4']

        # Add phasemode
        if 'phasemode' in kws:
            params['phasemode'] = kws['phasemode']

        # Add polarmode
        if 'polarmode' in kws:
            params['polarmode'] = kws['polarmode']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add data file name
        if 'data_file_name' in kws:
            params['data_file_name'] = kws['data_file_name']

        # Add data file timestamp
        if 'data_file_ts' in kws:
            params['data_file_ts'] = kws['data_file_ts']

        # Add data
        if 'data' in kws:
            fileName = kws['data']

            with open(fileName, 'rb') as f:
                ur = self.__session.post(self.__baseURL+'saverawdata/', files={'file': f}, auth=self.__auth)
                self.__raise_for_status(ur.status_code, ur.text)

            params['data_id'] = ur.json()['id']

        # Add script_name
        if 'script_name' in kws:
            params['script_name'] = kws['script_name']

        # Add script
        if 'script' in kws:
            params['script'] = kws['script']

        # Add method name
        if 'method_name' in kws:

            # Check method name
            if kws['method_name'] is None:
                self.__raise_for_status(400, 'If method name is passed it should not be None!')

            params['method_name'] = kws['method_name']

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def deleteOfflineData(self, offline_data_id):
        '''
        Deletes offline data

        :param offline_data_id: offline data id
        :type offline_data_id: int

        :return: True, if successful

        :Raises: HTTPError
        '''
        # Set URL
        url = 'deleteofflinedata/'

        # Set parameters
        params = {
            'offline_data_id': offline_data_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveOnlineData(self, **kws):
        '''
        Retrieves insertion device online data using any of the acceptable key words:

        :param onlineid: id of the online data we want to update 
        :type onlineid: int

        :param install_name: device name that the data belongs to
        :type install_name: str

        :param username: author who updated this data entry
        :type username: str

        :param description: a brief description for this data entry
        :type description: str

        :param rawdata_path: file path to the common location where the data file is stored
        :type rawdata_path: str

        :param status: status of this data set
        :type status: int

        :param meas_time: measurement time
        :type meas_time: str

        :return: a map with structure:

            .. code-block:: python

                {'id': {
                        'id':,                      #int
                        'installid':,               #int
                        'install_name':,            #string
                        'username':,                #string
                        'description':,             #string
                        'rawdata_path':,            #string
                        'date':,                    #date
                        'status':,                  #int
                        'feedforward_file_name':,   #int
                        'feedforward_data':,        #base64 string
                        'is_ascii':,                #boolean
                        'meas_time':,               #string
                    }
                }

        :Raises: HTTPError
        '''

        # Set URL
        url = 'onlinedata/'

        # Set parameters
        params = {}

        # Add online id
        if 'onlineid' in kws:
            params['onlineid'] = kws['onlineid']

        # Add install name
        if 'install_name' in kws:
            params['install_name'] = kws['install_name']

        # Add username
        if 'username' in kws:
            params['username'] = kws['username']

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add rawdata_path
        if 'rawdata_path' in kws:
            params['rawdata_path'] = kws['rawdata_path']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add meas_time
        if 'meas_time' in kws:
            params['meas_time'] = kws['meas_time']

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        returnData = r.json()

        return returnData

    def saveOnlineData(self, install_name, **kws):
        '''
        Saves insertion device online data using any of the acceptable key words:

        :param install_name: device name that the data belongs to
        :type install_name: str

        :param username: author who updated this data entry
        :type username: str

        :param description: a brief description for this data entry
        :type description: str

        :param rawdata_path: file path to the common location where the data file is stored
        :type rawdata_path: str

        :param status: status of this data set
        :type status: int

        :param feedforward_file_name: feedforward file name
        :type feedforward_file_name: str

        :param feedforward_data: feedforward data
        :type feedforward_data: blob

        :param meas_time: measurement time
        :type meas_time: str

        :return: a map with structure:

            .. code-block:: python

                {'id': data id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saveonlinedata/'

        # Set parameters
        params = {
            'install_name': install_name
        }

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add username
        if 'username' in kws:
            params['username'] = kws['username']

        # Add rawdata_path
        if 'rawdata_path' in kws:
            params['rawdata_path'] = kws['rawdata_path']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add feedforward_file_name
        if 'feedforward_file_name' in kws:
            params['feedforward_file_name'] = kws['feedforward_file_name']

        # Add feedforward_file_name
        filesDict = None

        if 'feedforward_data' in kws:
            # params['feedforward_data'] = kws['feedforward_data']
            filesDict = {'file': kws['feedforward_data']}

        # Add meas_time
        if 'meas_time' in kws:
            params['meas_time'] = kws['meas_time']

        r = self.__session.post(self.__baseURL+url, data=params, files=filesDict, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateOnlineData(self, online_data_id, **kws):
        '''
        Updates insertion device online data using any of the acceptable key words:

        :param install_name: device name that the data belongs to
        :type install_name: str

        :param username: author who updated this data entry
        :type username: str

        :param description: a brief description for this data entry
        :type description: str

        :param rawdata_path: file path to the common location where the data file is stored
        :type rawdata_path: str

        :param status: status of this data set
        :type status: int

        :param feedforward_file_name: feedforward file name
        :type feedforward_file_name: str

        :param feedforward_data: feedforward data
        :type feedforward_data: blob

        :param meas_time: measurement time
        :type meas_time: str

        :return: True, if successful

        :Raises: HTTPError
        '''
        # Set URL
        url = 'updateonlinedata/'

        # Set parameters
        params = {
            'online_data_id': online_data_id
        }

        # Add install name
        if 'install_name' in kws:

            # Check install name
            if kws['install_name'] is None:
                self.__raise_for_status(400, 'If install name is passed it should not be None!')

            params['install_name'] = kws['install_name']

        # Add description
        if 'description' in kws:
            params['description'] = kws['description']

        # Add username
        if 'username' in kws:
            params['username'] = kws['username']

        # Add rawdata_path
        if 'rawdata_path' in kws:
            params['rawdata_path'] = kws['rawdata_path']

        # Add status
        if 'status' in kws:
            params['status'] = kws['status']

        # Add feedforward_file_name
        if 'feedforward_file_name' in kws:
            params['feedforward_file_name'] = kws['feedforward_file_name']

        # Add feedforward_data
        filesDict = None

        if 'feedforward_data' in kws:
            # params['feedforward_data'] = kws['feedforward_data']
            filesDict = {'file': kws['feedforward_data']}

        # Add meas_time
        if 'meas_time' in kws:
            params['meas_time'] = kws['meas_time']

        r = self.__session.post(self.__baseURL+url, data=params, files=filesDict, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def deleteOnlineData(self, online_data_id):
        '''
        Deletes online data

        :param online_data_id: online data id
        :type online_data_id: int

        :return: True, if successful

        :Raises: HTTPError
        '''
        # Set URL
        url = 'deleteonlinedata/'

        # Set parameters
        params = {
            'online_data_id': online_data_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def uploadFile(self, data, file_name):
        '''
        Uploads a file

        params:
            - data: path to the file
            - file_name: name of the file
        '''

        with open(data, 'rb') as f:

            # Set parameters
            params = {
                'file_name': file_name
            }

            r = self.__session.post(self.__baseURL+'file/', files={'file': f}, data=params, auth=self.__auth)
            self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def idodsInstall(self):
        '''
        Saves common data into the database

        :return: True, if successful

        :Raises: HTTPError
        '''

        # Try to retrieve data method
        url = 'idods_install/'

        r = self.__session.post(self.__baseURL+url, verify=False, headers=self.__jsonheader, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveRotCoilData(self, inventory_id):
        '''
        Retrieves rotation coil data

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :return: a dictionary with structure:

            .. code-block:: python

                {
                    'id': {
                        rot_coil_data_id,
                        inventory_id,
                        alias,
                        meas_coil_id,
                        ref_radius,
                        magnet_notes,
                        login_name,
                        cond_curr,
                        meas_loc,
                        run_number,
                        sub_device,
                        current_1,
                        current_2,
                        current_3,
                        up_dn_1,
                        up_dn_2,
                        up_dn_3,
                        analysis_number,
                        integral_xfer_function,
                        orig_offset_x,
                        orig_offset_y,
                        b_ref_int,
                        roll_angle,
                        meas_notes,
                        meas_date,
                        author,
                        a1,
                        a2,
                        a3,
                        b1,
                        b2,
                        b3,
                        a4_21,
                        b4_21,
                        data_issues,
                        data_usage,
                        inventory_name
                    },
                    ...
                }

        :Raises: HTTPError
        '''

        # Try to retrieve data
        url = 'rotcoildata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveRotCoilData(
            self, inventory_id, alias=None, meas_coil_id=None, ref_radius=None, magnet_notes=None, login_name=None, cond_curr=None,
            meas_loc=None, run_number=None, sub_device=None, current_1=None, current_2=None, current_3=None, up_dn_1=None, up_dn_2=None, up_dn_3=None,
            analysis_number=None, integral_xfer_function=None, orig_offset_x=None, orig_offset_y=None, b_ref_int=None, roll_angle=None,
            meas_notes=None, author=None, a1=None, a2=None, a3=None, b1=None, b2=None, b3=None, a4_21=None, b4_21=None, data_issues=None, data_usage=None
            ):
        '''
        Saves rotation coil data

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :param alias: alias name
        :type alias: str

        :param meas_coil_id: ID  of device used for this measurement
        :type meas_coil_id: str

        :param ref_radius: reference radius
        :type ref_radius: double

        :param magnet_notes: comment for this magnet measurement data set
        :type magnet_notes: str

        :param login_name: user Name of user who generated this data set
        :type login_name: str

        :param cond_curr: condition current
        :type cond_curr: double

        :param meas_loc: measurement location
        :type meas_loc: str

        :param run_number: Which run was this data produced in?
        :type run_number: str

        :param sub_device: name of the sub device
        :type sub_device: str

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn_1: direction of 1 st current
        :type up_dn_1: str

        :param up_dn_2: direction of 2 nd current
        :type up_dn_2: str

        :param up_dn_3: direction of 4 rd current
        :type up_dn_3: str

        :param analysis_number: Analysis that this data belongs to
        :type analysis_number: str

        :param integral_xfer_function: integral transfer function
        :type integral_xfer_function: double

        :param orig_offset_x: horizontal origin offset
        :type orig_offset_x: double

        :param orig_offset_y: vertical origin offset
        :type orig_offset_y: double

        :param b_ref_int: integrated reference field
        :type b_ref_int: double

        :param roll_angle: rolling angle
        :type roll_angle: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param author: who measured it
        :type author: str

        :param a1: magnetic field (a1)
        :type a1: double

        :param a2: magnetic field (a2)
        :type a2: double

        :param a3: magnetic field (a3)
        :type a3: double

        :param b1: magnetic field (b1)
        :type b1: double

        :param b2: magnetic field (b2)
        :type b2: double

        :param b3: magnetic field (b3)
        :type b3: double

        :param a4_21: high order magnetic field (a4 to a21)
        :type a4_21: str

        :param b4_21: high order magnetic field (b4 to b21)
        :type b4_21: str

        :param data_issues: Reserved: special field to note each measure point
        :type data_issues: str

        :param data_usage: Reserved
        :type data_usage: int

        :return: a map with structure:

            .. code-block:: python

                {'id': rot_coil_data_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'saverotcoildata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'alias': alias,
            'meas_coil_id': meas_coil_id,
            'ref_radius': ref_radius,
            'magnet_notes': magnet_notes,
            'login_name': login_name,
            'cond_curr': cond_curr,
            'meas_loc': meas_loc,
            'run_number': run_number,
            'sub_device': sub_device,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn_1': up_dn_1,
            'up_dn_2': up_dn_2,
            'up_dn_3': up_dn_3,
            'analysis_number': analysis_number,
            'integral_xfer_function': integral_xfer_function,
            'orig_offset_x': orig_offset_x,
            'orig_offset_y': orig_offset_y,
            'b_ref_int': b_ref_int,
            'roll_angle': roll_angle,
            'meas_notes': meas_notes,
            'author': author,
            'a1': a1,
            'a2': a2,
            'a3': a3,
            'b1': b1,
            'b2': b2,
            'b3': b3,
            'a4_21': a4_21,
            'b4_21': b4_21,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateRotCoilData(
            self, rot_coil_data_id, inventory_id=None, alias=None, meas_coil_id=None, ref_radius=None, magnet_notes=None, login_name=None, cond_curr=None,
            meas_loc=None, run_number=None, sub_device=None, current_1=None, current_2=None, current_3=None, up_dn_1=None, up_dn_2=None, up_dn_3=None,
            analysis_number=None, integral_xfer_function=None, orig_offset_x=None, orig_offset_y=None, b_ref_int=None, roll_angle=None,
            meas_notes=None, author=None, a1=None, a2=None, a3=None, b1=None, b2=None, b3=None, a4_21=None, b4_21=None, data_issues=None, data_usage=None
            ):
        '''
        Updates rotation coil data

        :param rot_coil_data_id: id of the data in the database
        :type rot_coil_data_id: int

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :param alias: alias name
        :type alias: str

        :param meas_coil_id: ID  of device used for this measurement
        :type meas_coil_id: str

        :param ref_radius: reference radius
        :type ref_radius: double

        :param magnet_notes: comment for this magnet measurement data set
        :type magnet_notes: str

        :param login_name: user Name of user who generated this data set
        :type login_name: str

        :param cond_curr: condition current
        :type cond_curr: double

        :param meas_loc: measurement location
        :type meas_loc: str

        :param run_number: Which run was this data produced in?
        :type run_number: str

        :param sub_device: name of the sub device
        :type sub_device: str

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn_1: direction of 1 st current
        :type up_dn_1: str

        :param up_dn_2: direction of 2 nd current
        :type up_dn_2: str

        :param up_dn_3: direction of 4 rd current
        :type up_dn_3: str

        :param analysis_number: Analysis that this data belongs to
        :type analysis_number: str

        :param integral_xfer_function: integral transfer function
        :type integral_xfer_function: double

        :param orig_offset_x: horizontal origin offset
        :type orig_offset_x: double

        :param orig_offset_y: vertical origin offset
        :type orig_offset_y: double

        :param b_ref_int: integrated reference field
        :type b_ref_int: double

        :param roll_angle: rolling angle
        :type roll_angle: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param author: who measured it
        :type author: str

        :param a1: magnetic field (a1)
        :type a1: double

        :param a2: magnetic field (a2)
        :type a2: double

        :param a3: magnetic field (a3)
        :type a3: double

        :param b1: magnetic field (b1)
        :type b1: double

        :param b2: magnetic field (b2)
        :type b2: double

        :param b3: magnetic field (b3)
        :type b3: double

        :param a4_21: high order magnetic field (a4 to a21)
        :type a4_21: str

        :param b4_21: high order magnetic field (b4 to b21)
        :type b4_21: str

        :param data_issues: Reserved: special field to note each measure point
        :type data_issues: str

        :param data_usage: Reserved
        :type data_usage: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updaterotcoildata/'

        # Set parameters
        params = {
            'rot_coil_data_id': rot_coil_data_id,
            'inventory_id': inventory_id,
            'alias': alias,
            'meas_coil_id': meas_coil_id,
            'ref_radius': ref_radius,
            'magnet_notes': magnet_notes,
            'login_name': login_name,
            'cond_curr': cond_curr,
            'meas_loc': meas_loc,
            'run_number': run_number,
            'sub_device': sub_device,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn_1': up_dn_1,
            'up_dn_2': up_dn_2,
            'up_dn_3': up_dn_3,
            'analysis_number': analysis_number,
            'integral_xfer_function': integral_xfer_function,
            'orig_offset_x': orig_offset_x,
            'orig_offset_y': orig_offset_y,
            'b_ref_int': b_ref_int,
            'roll_angle': roll_angle,
            'meas_notes': meas_notes,
            'author': author,
            'a1': a1,
            'a2': a2,
            'a3': a3,
            'b1': b1,
            'b2': b2,
            'b3': b3,
            'a4_21': a4_21,
            'b4_21': b4_21,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def deleteRotCoilData(self, inventory_id, rot_coil_data_id=None):
        '''
        Deletes one or more sets of rotation coil data

        :param inventory_id: name of the device in the inventory
        :type inventory_id: str

        :param rot_coil_data_id: id of data in the table
        :type rot_coil_data_id: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'deleterotcoildata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'rot_coil_data_id': rot_coil_data_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveHallProbeData(self, inventory_id):
        '''
        Retrieves Hall probe data

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :return: a dictionary with structure:

            .. code-block:: python

                {
                    'id': {
                        hall_probe_id,
                        inventory_id,
                        alias,
                        meas_date,
                        measured_at_location,
                        sub_device,
                        run_identifier,
                        login_name,
                        conditioning_current,
                        current_1,
                        current_2,
                        current_3,
                        up_dn1,
                        up_dn2,
                        up_dn3,
                        mag_volt_1,
                        mag_volt_2,
                        mag_volt_3,
                        x,
                        y,
                        z,
                        bx_t,
                        by_t,
                        bz_t,
                        meas_notes,
                        data_issues,
                        data_usage,
                        inventory_name
                    },
                    ...
                }

        :Raises: HTTPError
        '''

        # Try to retrieve data
        url = 'hallprobedata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveHallProbeData(
            self, inventory_id, sub_device, alias=None, measured_at_location=None,
            run_identifier=None, login_name=None, conditioning_current=None, current_1=None, current_2=None,
            current_3=None, up_dn1=None, up_dn2=None, up_dn3=None, mag_volt_1=None, mag_volt_2=None, mag_volt_3=None,
            x=None, y=None, z=None, bx_t=None, by_t=None, bz_t=None, meas_notes=None, data_issues=None, data_usage=None
            ):
        '''
        Saves Hall probe data

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :param alias: alias name
        :type alias: str

        :param sub_device: sub device name
        :type sub_device: str

        :param measured_at_location: Location where data was measured
        :type measured_at_location: str

        :param run_identifier:  Run that this data was produced in
        :type run_identifier: str

        :param login_name: Name of user who generated this data set
        :type login_name: str

        :param conditioning_current: condition current
        :type conditioning_current: double

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn1: direction of 1 st current
        :type up_dn1: str

        :param up_dn2: direction of 2 nd current
        :type up_dn2: str

        :param up_dn3: direction of 3 rd current
        :type up_dn3: str

        :param mag_volt_1: voltage at 1 st current given to magnet
        :type mag_volt_1: double

        :param mag_volt_2: voltage at 2 nd current given to magnet
        :type mag_volt_2: double

        :param mag_volt_3: voltage at 3 rd current given to magnet
        :type mag_volt_3: double

        :param x: x position
        :type x: double

        :param y: y position
        :type y: double

        :param z: z position
        :type z: double

        :param bx_t: magnetic field along x axis
        :type bx_t: double

        :param by_t: magnetic field along y axis
        :type by_t: double

        :param bz_t: magnetic field along z axis
        :type bz_t: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param data_issues: reserved
        :type data_issues: str

        :param data_usage: reserved
        :type data_usage: int

        :return: a map with structure:

            .. code-block:: python

                {'id': hall_probe_data_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'savehallprobedata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'sub_device': sub_device,
            'alias': alias,
            'measured_at_location': measured_at_location,
            'run_identifier': run_identifier,
            'login_name': login_name,
            'conditioning_current': conditioning_current,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn1': up_dn1,
            'up_dn2': up_dn2,
            'up_dn3': up_dn3,
            'mag_volt_1': mag_volt_1,
            'mag_volt_2': mag_volt_2,
            'mag_volt_3': mag_volt_3,
            'x': x,
            'y': y,
            'z': z,
            'bx_t': bx_t,
            'by_t': by_t,
            'bz_t': bz_t,
            'meas_notes': meas_notes,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateHallProbeData(
            self, hall_probe_id, inventory_id=None, sub_device=None, alias=None, measured_at_location=None,
            run_identifier=None, login_name=None, conditioning_current=None, current_1=None, current_2=None,
            current_3=None, up_dn1=None, up_dn2=None, up_dn3=None, mag_volt_1=None, mag_volt_2=None, mag_volt_3=None,
            x=None, y=None, z=None, bx_t=None, by_t=None, bz_t=None, meas_notes=None, data_issues=None, data_usage=None
            ):
        '''
        Updates Hall probe data

        :param hall_probe_id: id of the Hall probe
        :type hall_probe_id: int

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :param alias: alias name
        :type alias: str

        :param sub_device: sub device name
        :type sub_device: str

        :param measured_at_location: Location where data was measured
        :type measured_at_location: str

        :param run_identifier:  Run that this data was produced in
        :type run_identifier: str

        :param login_name: Name of user who generated this data set
        :type login_name: str

        :param conditioning_current: condition current
        :type conditioning_current: double

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn1: direction of 1 st current
        :type up_dn1: str

        :param up_dn2: direction of 2 nd current
        :type up_dn2: str

        :param up_dn3: direction of 3 rd current
        :type up_dn3: str

        :param mag_volt_1: voltage at 1 st current given to magnet
        :type mag_volt_1: double

        :param mag_volt_2: voltage at 2 nd current given to magnet
        :type mag_volt_2: double

        :param mag_volt_3: voltage at 3 rd current given to magnet
        :type mag_volt_3: double

        :param x: x position
        :type x: double

        :param y: y position
        :type y: double

        :param z: z position
        :type z: double

        :param bx_t: magnetic field along x axis
        :type bx_t: double

        :param by_t: magnetic field along y axis
        :type by_t: double

        :param bz_t: magnetic field along z axis
        :type bz_t: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param data_issues: reserved
        :type data_issues: str

        :param data_usage: reserved
        :type data_usage: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatehallprobedata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'hall_probe_id': hall_probe_id,
            'sub_device': sub_device,
            'alias': alias,
            'measured_at_location': measured_at_location,
            'run_identifier': run_identifier,
            'login_name': login_name,
            'conditioning_current': conditioning_current,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn1': up_dn1,
            'up_dn2': up_dn2,
            'up_dn3': up_dn3,
            'mag_volt_1': mag_volt_1,
            'mag_volt_2': mag_volt_2,
            'mag_volt_3': mag_volt_3,
            'x': x,
            'y': y,
            'z': z,
            'bx_t': bx_t,
            'by_t': by_t,
            'bz_t': bz_t,
            'meas_notes': meas_notes,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def deleteHallProbeData(self, inventory_id, hall_probe_id=None):
        '''
        Deletes one or more sets of Hall probe data

        :param inventory_id: id of the device in the inventory
        :type inventory_id: int

        :param hall_probe_id: id of data in the table
        :type hall_probe_id: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'deletehallprobedata/'

        # Set parameters
        params = {
            'inventory_id': inventory_id,
            'hall_probe_id': hall_probe_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveComponentTypeRotCoilData(self, cmpnt_type_name):
        '''
        Retrieves rotation coil data

        :param cmpnt_type_name: name of the device in the inventory
        :type cmpnt_type_name: str

        :return: a dictionary with structure:

            .. code-block:: python

                {
                    'id': {
                        rot_coil_data_id,
                        cmpnt_type_id,
                        alias,
                        meas_coil_id,
                        ref_radius,
                        magnet_notes,
                        login_name,
                        cond_curr,
                        meas_loc,
                        run_number,
                        sub_device,
                        current_1,
                        current_2,
                        current_3,
                        up_dn_1,
                        up_dn_2,
                        up_dn_3,
                        analysis_number,
                        integral_xfer_function,
                        orig_offset_x,
                        orig_offset_y,
                        b_ref_int,
                        roll_angle,
                        meas_notes,
                        meas_date,
                        author,
                        a1,
                        a2,
                        a3,
                        b1,
                        b2,
                        b3,
                        a4_21,
                        b4_21,
                        data_issues,
                        data_usage,
                        cmpnt_type_name
                    },
                    ...
                }

        :Raises: HTTPError
        '''

        # Try to retrieve data
        url = 'ctrotcoildata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveComponentTypeRotCoilData(
            self, cmpnt_type_name, alias=None, meas_coil_id=None, ref_radius=None, magnet_notes=None, login_name=None, cond_curr=None,
            meas_loc=None, run_number=None, sub_device=None, current_1=None, current_2=None, current_3=None, up_dn_1=None, up_dn_2=None, up_dn_3=None,
            analysis_number=None, integral_xfer_function=None, orig_offset_x=None, orig_offset_y=None, b_ref_int=None, roll_angle=None,
            meas_notes=None, author=None, a1=None, a2=None, a3=None, b1=None, b2=None, b3=None, a4_21=None, b4_21=None, data_issues=None, data_usage=None
            ):
        '''
        Saves rotation coil data

        :param cmpnt_type_name: name of the component type
        :type cmpnt_type_name: str

        :param alias: alias name
        :type alias: str

        :param meas_coil_id: ID  of device used for this measurement
        :type meas_coil_id: str

        :param ref_radius: reference radius
        :type ref_radius: double

        :param magnet_notes: comment for this magnet measurement data set
        :type magnet_notes: str

        :param login_name: user Name of user who generated this data set
        :type login_name: str

        :param cond_curr: condition current
        :type cond_curr: double

        :param meas_loc: measurement location
        :type meas_loc: str

        :param run_number: Run that this data was produced in
        :type run_number: str

        :param sub_device: name of the sub device
        :type sub_device: str

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn_1: direction of 1 st current
        :type up_dn_1: str

        :param up_dn_2: direction of 2 nd current
        :type up_dn_2: str

        :param up_dn_3: direction of 4 rd current
        :type up_dn_3: str

        :param analysis_number: Analysis that this data belongs to
        :type analysis_number: str

        :param integral_xfer_function: integral transfer function
        :type integral_xfer_function: double

        :param orig_offset_x: horizontal origin offset
        :type orig_offset_x: double

        :param orig_offset_y: vertical origin offset
        :type orig_offset_y: double

        :param b_ref_int: integrated reference field
        :type b_ref_int: double

        :param roll_angle: rolling angle
        :type roll_angle: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param author: who measured it
        :type author: str

        :param a1: magnetic field (a1)
        :type a1: double

        :param a2: magnetic field (a2)
        :type a2: double

        :param a3: magnetic field (a3)
        :type a3: double

        :param b1: magnetic field (b1)
        :type b1: double

        :param b2: magnetic field (b2)
        :type b2: double

        :param b3: magnetic field (b3)
        :type b3: double

        :param a4_21: high order magnetic field (a4 to a21)
        :type a4_21: str

        :param b4_21: high order magnetic field (b4 to b21)
        :type b4_21: str

        :param data_issues: Reserved: special field to note each measure point
        :type data_issues: str

        :param data_usage: Reserved
        :type data_usage: int

        :return: a map with structure:

            .. code-block:: python

                {'id': rot_coil_data_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'savectrotcoildata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'alias': alias,
            'meas_coil_id': meas_coil_id,
            'ref_radius': ref_radius,
            'magnet_notes': magnet_notes,
            'login_name': login_name,
            'cond_curr': cond_curr,
            'meas_loc': meas_loc,
            'run_number': run_number,
            'sub_device': sub_device,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn_1': up_dn_1,
            'up_dn_2': up_dn_2,
            'up_dn_3': up_dn_3,
            'analysis_number': analysis_number,
            'integral_xfer_function': integral_xfer_function,
            'orig_offset_x': orig_offset_x,
            'orig_offset_y': orig_offset_y,
            'b_ref_int': b_ref_int,
            'roll_angle': roll_angle,
            'meas_notes': meas_notes,
            'author': author,
            'a1': a1,
            'a2': a2,
            'a3': a3,
            'b1': b1,
            'b2': b2,
            'b3': b3,
            'a4_21': a4_21,
            'b4_21': b4_21,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateComponentTypeRotCoilData(
            self, rot_coil_data_id, cmpnt_type_name, alias=None, meas_coil_id=None, ref_radius=None, magnet_notes=None, login_name=None, cond_curr=None,
            meas_loc=None, run_number=None, sub_device=None, current_1=None, current_2=None, current_3=None, up_dn_1=None, up_dn_2=None, up_dn_3=None,
            analysis_number=None, integral_xfer_function=None, orig_offset_x=None, orig_offset_y=None, b_ref_int=None, roll_angle=None,
            meas_notes=None, author=None, a1=None, a2=None, a3=None, b1=None, b2=None, b3=None, a4_21=None, b4_21=None, data_issues=None, data_usage=None
            ):
        '''
        Updates rotation coil data

        :param rot_coil_data_id: id of the data in the database
        :type rot_coil_data_id: int

        :param cmpnt_type_name: name of the component type
        :type cmpnt_type_name: str

        :param alias: alias name
        :type alias: str

        :param meas_coil_id: ID  of device used for this measurement
        :type meas_coil_id: str

        :param ref_radius: reference radius
        :type ref_radius: double

        :param magnet_notes: comment for this magnet measurement data set
        :type magnet_notes: str

        :param login_name: user Name of user who generated this data set
        :type login_name: str

        :param cond_curr: condition current
        :type cond_curr: double

        :param meas_loc: measurement location
        :type meas_loc: str

        :param run_number: Run that this data was produced in
        :type run_number: str

        :param sub_device: name of the sub device
        :type sub_device: str

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn_1: direction of 1 st current
        :type up_dn_1: str

        :param up_dn_2: direction of 2 nd current
        :type up_dn_2: str

        :param up_dn_3: direction of 4 rd current
        :type up_dn_3: str

        :param analysis_number: Analysis that this data belongs to
        :type analysis_number: str

        :param integral_xfer_function: integral transfer function
        :type integral_xfer_function: double

        :param orig_offset_x: horizontal origin offset
        :type orig_offset_x: double

        :param orig_offset_y: vertical origin offset
        :type orig_offset_y: double

        :param b_ref_int: integrated reference field
        :type b_ref_int: double

        :param roll_angle: rolling angle
        :type roll_angle: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param author: who measured it
        :type author: str

        :param a1: magnetic field (a1)
        :type a1: double

        :param a2: magnetic field (a2)
        :type a2: double

        :param a3: magnetic field (a3)
        :type a3: double

        :param b1: magnetic field (b1)
        :type b1: double

        :param b2: magnetic field (b2)
        :type b2: double

        :param b3: magnetic field (b3)
        :type b3: double

        :param a4_21: high order magnetic field (a4 to a21)
        :type a4_21: str

        :param b4_21: high order magnetic field (b4 to b21)
        :type b4_21: str

        :param data_issues: Reserved: special field to note each measure point
        :type data_issues: str

        :param data_usage: Reserved
        :type data_usage: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatectrotcoildata/'

        # Set parameters
        params = {
            'rot_coil_data_id': rot_coil_data_id,
            'cmpnt_type_name': cmpnt_type_name,
            'alias': alias,
            'meas_coil_id': meas_coil_id,
            'ref_radius': ref_radius,
            'magnet_notes': magnet_notes,
            'login_name': login_name,
            'cond_curr': cond_curr,
            'meas_loc': meas_loc,
            'run_number': run_number,
            'sub_device': sub_device,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn_1': up_dn_1,
            'up_dn_2': up_dn_2,
            'up_dn_3': up_dn_3,
            'analysis_number': analysis_number,
            'integral_xfer_function': integral_xfer_function,
            'orig_offset_x': orig_offset_x,
            'orig_offset_y': orig_offset_y,
            'b_ref_int': b_ref_int,
            'roll_angle': roll_angle,
            'meas_notes': meas_notes,
            'author': author,
            'a1': a1,
            'a2': a2,
            'a3': a3,
            'b1': b1,
            'b2': b2,
            'b3': b3,
            'a4_21': a4_21,
            'b4_21': b4_21,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def deleteComponentTypeRotCoilData(self, cmpnt_type_name, rot_coil_data_id=None):
        '''
        Deletes one or more sets of rotation coil data

        :param cmpnt_type_name: name of the component type
        :type cmpnt_type_name: str

        :param rot_coil_data_id: id of data in the table
        :type rot_coil_data_id: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'deletectrotcoildata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'rot_coil_data_id': rot_coil_data_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def retrieveComponentTypeHallProbeData(self, cmpnt_type_name):
        '''
        Retrieves Hall probe data

        :param cmpnt_type_name: name of the device in the inventory
        :type cmpnt_type_name: str

        :return: a dictionary with structure:

            .. code-block:: python

                {
                    'id': {
                        hall_probe_id,
                        cmpnt_type_id,
                        alias,
                        meas_date,
                        measured_at_location,
                        sub_device,
                        run_identifier,
                        login_name,
                        conditioning_current,
                        current_1,
                        current_2,
                        current_3,
                        up_dn1,
                        up_dn2,
                        up_dn3,
                        mag_volt_1,
                        mag_volt_2,
                        mag_volt_3,
                        x,
                        y,
                        z,
                        bx_t,
                        by_t,
                        bz_t,
                        meas_notes,
                        data_issues,
                        data_usage,
                        cmpnt_type_name
                    },
                    ...
                }

        :Raises: HTTPError
        '''

        # Try to retrieve data
        url = 'cthallprobedata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name
        }

        r = self.__session.get(self.__baseURL+url, params=params, verify=False, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def saveComponentTypeHallProbeData(
            self, cmpnt_type_name, sub_device, alias=None, measured_at_location=None,
            run_identifier=None, login_name=None, conditioning_current=None, current_1=None, current_2=None,
            current_3=None, up_dn1=None, up_dn2=None, up_dn3=None, mag_volt_1=None, mag_volt_2=None, mag_volt_3=None,
            x=None, y=None, z=None, bx_t=None, by_t=None, bz_t=None, meas_notes=None, data_issues=None, data_usage=None
            ):
        '''
        Saves Hall probe data

        :param cmpnt_type_name: name of the component type
        :type cmpnt_type_name: str

        :param alias: alias name
        :type alias: str

        :param sub_device: sub device name
        :type sub_device: str

        :param measured_at_location: Location where data was measured
        :type measured_at_location: str

        :param run_identifier:  Run that this data was produced in
        :type run_identifier: str

        :param login_name: Name of user who generated this data set
        :type login_name: str

        :param conditioning_current: condition current
        :type conditioning_current: double

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn1: direction of 1 st current
        :type up_dn1: str

        :param up_dn2: direction of 2 nd current
        :type up_dn2: str

        :param up_dn3: direction of 3 rd current
        :type up_dn3: str

        :param mag_volt_1: voltage at 1 st current given to magnet
        :type mag_volt_1: double

        :param mag_volt_2: voltage at 2 nd current given to magnet
        :type mag_volt_2: double

        :param mag_volt_3: voltage at 3 rd current given to magnet
        :type mag_volt_3: double

        :param x: x position
        :type x: double

        :param y: y position
        :type y: double

        :param z: z position
        :type z: double

        :param bx_t: magnetic field along x axis
        :type bx_t: double

        :param by_t: magnetic field along y axis
        :type by_t: double

        :param bz_t: magnetic field along z axis
        :type bz_t: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param data_issues: reserved
        :type data_issues: str

        :param data_usage: reserved
        :type data_usage: int

        :return: a map with structure:

            .. code-block:: python

                {'id': hall_probe_data_id}

        :Raises: HTTPError
        '''

        # Set URL
        url = 'savecthallprobedata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'sub_device': sub_device,
            'alias': alias,
            'measured_at_location': measured_at_location,
            'run_identifier': run_identifier,
            'login_name': login_name,
            'conditioning_current': conditioning_current,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn1': up_dn1,
            'up_dn2': up_dn2,
            'up_dn3': up_dn3,
            'mag_volt_1': mag_volt_1,
            'mag_volt_2': mag_volt_2,
            'mag_volt_3': mag_volt_3,
            'x': x,
            'y': y,
            'z': z,
            'bx_t': bx_t,
            'by_t': by_t,
            'bz_t': bz_t,
            'meas_notes': meas_notes,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def updateComponentTypeHallProbeData(
            self, hall_probe_id, cmpnt_type_name, sub_device=None, alias=None, measured_at_location=None,
            run_identifier=None, login_name=None, conditioning_current=None, current_1=None, current_2=None,
            current_3=None, up_dn1=None, up_dn2=None, up_dn3=None, mag_volt_1=None, mag_volt_2=None, mag_volt_3=None,
            x=None, y=None, z=None, bx_t=None, by_t=None, bz_t=None, meas_notes=None, data_issues=None, data_usage=None
            ):
        '''
        Updates Hall probe data

        :param hall_probe_id: id of the Hall probe
        :type hall_probe_id: int

        :param cmpnt_type_name: name of the component type
        :type cmpnt_type_name: str

        :param alias: alias name
        :type alias: str

        :param sub_device: sub device name
        :type sub_device: str

        :param measured_at_location: Location where data was measured
        :type measured_at_location: str

        :param run_identifier:  Run that this data was produced in
        :type run_identifier: str

        :param login_name: Name of user who generated this data set
        :type login_name: str

        :param conditioning_current: condition current
        :type conditioning_current: double

        :param current_1: 1 st measurement current
        :type current_1: double

        :param current_2: 2 nd measurement current
        :type current_2: double

        :param current_3: 3 rd measurement current
        :type current_3: double

        :param up_dn1: direction of 1 st current
        :type up_dn1: str

        :param up_dn2: direction of 2 nd current
        :type up_dn2: str

        :param up_dn3: direction of 3 rd current
        :type up_dn3: str

        :param mag_volt_1: voltage at 1 st current given to magnet
        :type mag_volt_1: double

        :param mag_volt_2: voltage at 2 nd current given to magnet
        :type mag_volt_2: double

        :param mag_volt_3: voltage at 3 rd current given to magnet
        :type mag_volt_3: double

        :param x: x position
        :type x: double

        :param y: y position
        :type y: double

        :param z: z position
        :type z: double

        :param bx_t: magnetic field along x axis
        :type bx_t: double

        :param by_t: magnetic field along y axis
        :type by_t: double

        :param bz_t: magnetic field along z axis
        :type bz_t: double

        :param meas_notes: comments for each measuring data point
        :type meas_notes: str

        :param data_issues: reserved
        :type data_issues: str

        :param data_usage: reserved
        :type data_usage: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'updatecthallprobedata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'hall_probe_id': hall_probe_id,
            'sub_device': sub_device,
            'alias': alias,
            'measured_at_location': measured_at_location,
            'run_identifier': run_identifier,
            'login_name': login_name,
            'conditioning_current': conditioning_current,
            'current_1': current_1,
            'current_2': current_2,
            'current_3': current_3,
            'up_dn1': up_dn1,
            'up_dn2': up_dn2,
            'up_dn3': up_dn3,
            'mag_volt_1': mag_volt_1,
            'mag_volt_2': mag_volt_2,
            'mag_volt_3': mag_volt_3,
            'x': x,
            'y': y,
            'z': z,
            'bx_t': bx_t,
            'by_t': by_t,
            'bz_t': bz_t,
            'meas_notes': meas_notes,
            'data_issues': data_issues,
            'data_usage': data_usage
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def deleteComponentTypeHallProbeData(self, cmpnt_type_name, hall_probe_id=None):
        '''
        Deletes one or more sets of Hall probe data

        :param cmpnt_type_name: name of the component type
        :type cmpnt_type_name: str

        :param hall_probe_id: id of data in the table
        :type hall_probe_id: int

        :return: True or HTTPError

        :Raises: HTTPError
        '''

        # Set URL
        url = 'deletecthallprobedata/'

        # Set parameters
        params = {
            'cmpnt_type_name': cmpnt_type_name,
            'hall_probe_id': hall_probe_id
        }

        r = self.__session.post(self.__baseURL+url, data=params, headers=self.__jsonheader, verify=False, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def testAuth(self):
        '''
        Test auth

        :Raises: HTTPError
        '''

        url = 'test/'

        r = self.__session.post(self.__baseURL+url, verify=False, headers=self.__jsonheader, auth=self.__auth)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    def testCall(self):
        '''
        Test call without auth

        :Raises: HTTPError
        '''

        url = 'testcall/'

        r = self.__session.post(self.__baseURL+url, headers=self.__jsonheader)
        self.__raise_for_status(r.status_code, r.text)

        return r.json()

    @classmethod
    def __raise_for_status(self, status_code, reason):
        http_error_msg = ''

        if 400 <= status_code < 500:
            http_error_msg = '%s Client Error: %s' % (status_code, reason)

        elif 500 <= status_code < 600:
            http_error_msg = '%s Server Error: %s' % (status_code, reason)

        if http_error_msg:
            http_error = HTTPError(http_error_msg)
            http_error.response = self
            raise http_error

    def saveDevice(self, device_name, cmpnt_type_name, device_description=None, device_coordinatecenter=None, cmpnt_type_description=None, cmpnt_type_props=None):
        '''
        Saves insertion device installation

        :param device_name: installation name, which is its label in the field
        :type device_name: str
        
        :param cmpnt_type_name: component type of the device
        :type cmpnt_type_name: str

        :param device_description: installation description
        :type device_description: str

        :param device_coordinatecenter: coordinate center number
        :type device_coordinatecenter: float

        :param cmpnt_type_description: installation description
        :type cmpnt_type_description: str    

        :param  cmpnt_type_props: component type properties
        :type  cmpnt_type_props: python dict    

        :raises:
            HTTPError

        :returns:
            new device id
        '''
        # Save component type if it does not exist
        if len(self.retrieveComponentType(cmpnt_type_name)) == 0:
            self.saveComponentType(cmpnt_type_name, description=cmpnt_type_description, props=cmpnt_type_props)

        # Save device if it does not exist
        if len(self.retrieveInstall(device_name)) == 0:
            return self.saveInstall(device_name, cmpnt_type_name=cmpnt_type_name, description=device_description, coordinatecenter=device_coordinatecenter)['id']

    def retrieveDevice(self, device_name, description=None, cmpnt_type_name=None, coordinatecenter=None):
        '''Retrieves insertion device installation using any of the acceptable key words:

        :param device_name: installation name, which is its label in the field
        :type device_name: str

        :param description: installation description
        :type description: str

        :param cmpnt_type_name: component type name of the device
        :type cmpnt_type_name: str

        :param coordinatecenter: coordinate center number
        :type coordinatecenter: str

        :return: a map with structure:

            .. code-block:: python

                {
                    'id':                     #int,
                    'name':                   #string,
                    'description':            #string,
                    'cmpnt_type_name':        #string,
                    'cmpnt_type_description': #string,
                    'coordinatecenter':       #float,
                    'key1':                   #str,
                    ...
                    'prop_keys':              ['key1', 'key2']
                }

        :Raises: ValueError, MySQLError
        '''
        return self.retrieveInstall(device_name, description, cmpnt_type_name, coordinatecenter)

    def updateDevice(self, device_name_old, device_name_new, description=None, cmpnt_type_name=None, coordinatecenter=None):
        '''
        Updates a device installation using any of the acceptable key words:

        :param device_name_old: installation name, which is its label in the field
        :type device_name_old: str

        :param device_name_new: installation name, which is its label in the field
        :type device_name_new: str

        :param description: installation description
        :type description: str

        :param cmpnt_type_name: component type of the device
        :type cmpnt_type_name: str

        :param coordinatecenter: coordinate center number
        :type coordinatecenter: float

        raises:
            HTTPError

        returns:
            True, if successful
        '''
        return self.updateInstall(device_name_old, device_name_new, description, cmpnt_type_name, coordinatecenter)
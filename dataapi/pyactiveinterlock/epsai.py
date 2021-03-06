""" 
Created on Aug 15, 2013

@author: shengb
@updated: dejan.dezman@cosylab.com Mar 15th, 2014

"""

import logging
import MySQLdb

from utils import (_checkParameter, _checkWildcardAndAppend, _generateUpdateQuery)

from _mysql_exceptions import MySQLError

try:
    from django.utils import simplejson as json
except ImportError:
    import json

__all__ = []
__version__ = [1, 0, 0]

class epsai(object):
    '''
    Data API for the active interlock system.
    '''
    def __init__(self, conn, transaction=None):
        '''initialize active interlock class.
        
        :param conn: MySQL connection object
        :type conn: object

        :param transaction: Django MySQL transaction object. If this is set, it uses Django's transaction manager to manage each transaction.
        :type transaction: object
        
        :returns:  epsai -- class object
        
        '''
        self.logger = logging.getLogger('interlock')
        hdlr = logging.FileHandler('/var/tmp/active_interlock.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr) 
        self.logger.setLevel(logging.DEBUG)

        self.conn = conn
        
        self.returnDateFormat = "%Y-%m-%d %H:%M:%S"
        
        # use django transaction manager
        self.transaction = transaction
        
        # Define all the properties for id table
        self.id_props = [['cell', '', ''], ['type', '', ''], ['set', '', ''], ['str_sect', '', ''], ['defined_by', '', ''], ['s1_name', '', ''], ['s1_pos', 'm', ''], ['s1_pos_from', 'm', ''], ['s2_name', '', ''], ['s2_pos', 'm', ''], ['s2_pos_from', 'm', ''], ['s3_pos', 'm', ''], ['s3_pos_from', 'm', ''], ['max_offset', 'mm', 'approvable'], ['max_angle', 'mrad', 'approvable'], ['extra_offset', '', 'approvable'], ['x_offset_s1', 'mm', 'approvable'], ['x_offset_origin_s1', 'mm', 'approvable'], ['x_offset_s2', 'mm', 'approvable'], ['x_offset_origin_s2', 'mm', 'approvable'], ['x_offset_s3', 'mm', 'approvable'], ['x_angle', 'mrad', 'approvable'], ['y_offset_s1', 'mm', 'approvable'], ['y_offset_origin_s1', 'mm', 'approvable'], ['y_offset_s2', 'mm', 'approvable'], ['y_offset_origin_s2', 'mm', 'approvable'], ['y_offset_s3', 'mm', 'approvable'], ['y_angle', 'mrad', 'approvable'], ['safe_current', 'mA', 'approvable'], ['in_use', '', 'approvable']]
        self.id_props_dict = {
            'cell': ['cell', '', ''],
            'type': ['type', '', ''],
            'set': ['set', '', ''],
            'str_sect': ['str_sect', '', ''],
            'defined_by': ['defined_by', '', ''],
            's1_name': ['s1_name', '', ''],
            's1_pos': ['s1_pos', 'm', ''],
            's1_pos_from': ['s1_pos_from', 'm', ''],
            's2_name': ['s2_name', '', ''],
            's2_pos': ['s2_pos', 'm', ''],
            's2_pos_from': ['s2_pos_from', 'm', ''],
            's3_pos': ['s3_pos', 'm', ''],
            's3_pos_from': ['s3_pos_from', 'm', ''],
            'max_offset': ['max_offset', 'mm', 'approvable'],
            'max_angle': ['max_angle', 'mrad', 'approvable'],
            'extra_offset': ['extra_offset', '', 'approvable'],
            'x_offset_s1': ['x_offset_s1', 'mm', 'approvable'],
            'x_offset_origin_s1': ['x_offset_origin_s1', 'mm', 'approvable'],
            'x_offset_s2': ['x_offset_s2', 'mm', 'approvable'],
            'x_offset_origin_s2': ['x_offset_origin_s2', 'mm', 'approvable'],
            'x_offset_s3': ['x_offset_s3', 'mm', 'approvable'],
            'x_angle': ['x_angle', 'mrad', 'approvable'],
            'y_offset_s1': ['y_offset_s1', 'mm', 'approvable'],
            'y_offset_origin_s1': ['y_offset_origin_s1', 'mm', 'approvable'],
            'y_offset_s2': ['y_offset_s2', 'mm', 'approvable'],
            'y_offset_origin_s2': ['y_offset_origin_s2', 'mm', 'approvable'],
            'y_offset_s3': ['y_offset_s3', 'mm', 'approvable'],
            'y_angle': ['y_angle', 'mrad', 'approvable'],
            'safe_current': ['safe_current', 'mA', 'approvable'],
            'in_use': ['in_use', '', 'approvable']
        }
        
        # Define all the properties for the bm table
        self.bm_props = [['bm_cell', '', ''], ['bm_sequence', '', 'approvable'], ['bm_type', '', ''], ['bm_s', 'm', ''], ['bm_aiolh', 'mm', 'approvable'], ['bm_aiorh', 'mm', 'approvable'], ['bm_aiolv', 'mm', 'approvable'], ['bm_aiorv', 'mm', 'approvable'], ['bm_safe_current', 'mA', 'approvable'], ['bm_in_use', '', 'approvable']]
        self.bm_props_dict = {
            'bm_cell': ['bm_cell', '', ''],
            'bm_sequence': ['bm_sequence', '', 'approvable'],
            'bm_type': ['bm_type', '', ''],
            'bm_s': ['bm_s', 'm', ''],
            'bm_aiolh': ['bm_aiolh', 'mm', 'approvable'],
            'bm_aiorh': ['bm_aiorh', 'mm', 'approvable'],
            'bm_aiolv': ['bm_aiolv', 'mm', 'approvable'],
            'bm_aiorv': ['bm_aiorv', 'mm', 'approvable'],
            'bm_safe_current': ['bm_safe_current', 'mA', 'approvable'],
            'bm_in_use': ['bm_in_use', '', 'approvable']
        }
        
    def copyActiveInterlock(self, status, description, modified_by):
        '''
        Copies existing active interlock dataset to an editable status
        
        Current statuses:
        
         - 0: editable
         - 1: approved
         - 2: active
         - 3: backup
         - 4: history
        
        :param status: status of the active interlock being copied
        :type status: int
        
        :param description: active interlock description
        :type description: str
        
        :param modified_by: user requesting this update
        :type modified_by: str
            
        :Returns: boolean
            
            The return code: ::
                
                True, if successful.
                Exception, if there is an error.
        
        :Raises: MySQLError, ValueError
        '''
        
        # Get active interlock header
        ai = self.retrieveActiveInterlockHeader(status)
        
        if len(ai) == 0:
            raise ValueError("There is no active interlock with status %s", status)
        
        # Delete devices with status 0
        self.deleteActiveInterlock(0)
        
        # Create new header with status 0
        self.saveActiveInterlockHeader(description, modified_by)
        
        # Retrieve devices
        devices = self.retrieveDevice(None, status, "*", "*")
        
        # Go through devices and copy all of them
        for deviceId in devices.keys():
            deviceObj = devices[deviceId]
            deviceProps = {}
            approveProps = []
            
            if deviceObj['definition'] == 'bm':
                
                for prop in self.bm_props:
                    try:
                        deviceProps[prop[0]] = deviceObj[prop[0]]

                        if prop[2] == 'approvable':
                            approveProps.append(prop[0])
                    except KeyError:
                        self.logger.info("No value for key %s of SR-BPM " % prop[0])
            
            else:
                
                for prop in self.id_props:
                    try:
                        deviceProps[prop[0]] = deviceObj[prop[0]]

                        if prop[2] == 'approvable':
                            approveProps.append(prop[0])
                    except KeyError:
                        self.logger.info("No value for key %s of ID-BPM " % prop[0])

            
            newDeviceObj = self.saveDevice(0, deviceObj['name'], deviceObj['definition'], deviceObj['logic'], deviceProps)
            self.approveCells(newDeviceObj['id'], json.dumps(approveProps))

        return True
        
    def updateActiveInterlockStatus(self, ai_id, status, new_status, modified_by):
        '''
        Updates status of a dataset.
        
        Current statuses:
        
         - 0: editable
         - 1: approved
         - 2: active
         - 3: backup
         - 4: history
        
        :param ai_id: internal id of an active interlock dataset
        :type ai_id: int
        
        :param status: current status code
        :type status: int
        
        :param new_status: new status code
        :type new_status: int
        
        :param modified_by: user requesting this update
        :type modified_by: str
        
        :param definition: is bm (bending magnet) or id (insertion device) being updated?
        :type definition: str
            
        :Returns: boolean
            
            The return code: ::
                
                True, if successful.
                Exception, if there is an error.
        
        :Raises: MySQLError, ValueError
        '''

        # Convert
        new_status = int(new_status)
        
        # Check that id or status is set
        if ai_id == None and status == None:
            raise ValueError("Id or status should be provided to update status!")
        
        # Get active interlock id from status
        if status != None and ai_id == None:
            ai = self.retrieveActiveInterlockHeader(status)
            aiKeys = ai.keys()
            
            # If there is no dataset with this status, return True
            if len(aiKeys) == 0:
                return True
            
            aiObj = ai[aiKeys[0]]
            ai_id = aiObj['id']
        
        # Move statuses
        if new_status >= 2 and new_status < 4:
            self.updateActiveInterlockStatus(None, new_status, new_status + 1, modified_by)
        
        # Delete dataset that currently has this status
        if new_status == 0 or new_status == 1:
            self.deleteActiveInterlock(new_status)
        
        # Check if all properties are approved
        if new_status == 1:
            devices = self.retrieveDevice(None, 0, "*", "*")
            
            # Go through all the devices
            for deviceId in devices.keys():
                propertyStatuses = devices[deviceId]['prop_statuses']
                countUnapproved = propertyStatuses.values().count(2)
                
                if countUnapproved > 0:
                    raise ValueError("Dataset cannot be approved if there are unapproved device properties!")
        
        # Define query dict
        queryDict = {}
        whereDict = {}
        
        # Set status
        queryDict['status'] = new_status
        queryDict['modified_date'] = "now"
        queryDict['modified_by'] = modified_by
        
        # Set where
        whereDict['active_interlock_id'] = ai_id
        
        # Generate SQL
        sqlVals = _generateUpdateQuery('active_interlock', queryDict, None, None, whereDict)
        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])

            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
            
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error when updating active interlock status:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error when updating active interlock status:\n%s (%d)' % (e.args[1], e.args[0]))

    def saveDeviceProperties(self):
        '''
        Saves new active interlock device.
        When creating a new active interlock device, all necessary property types must be created.
        '''
        
        # Get current properties
        propTypes = self.retrieveActiveInterlockPropType('*')
        
        # If table is empty, add properties in it
        if len(propTypes) == 0:
            
            # Save all id properties into the database
            for prop in self.id_props:
                self.saveActiveInterlockPropType(prop[0], prop[1], prop[2])
            
            # Save all bm properties into the database
            for prop in self.bm_props:
                self.saveActiveInterlockPropType(prop[0], prop[1], prop[2])
        
    def retrieveActiveInterlockProp(self, aid_id, prop_type_name):
        '''
        Retrieves properties of the active interlock device
        
        :param aid_id: active interlock device ID
        :type aid_id: int
        
        :param prop_type_name: active interlock property  type name
        :type prop_type_name: str
        
        :returns: Python dictionary with structure:
            
            .. code-block:: python
            
                {'id':
                    'id':            , #int, property id
                    'aid_id':        , #int, active interlock device ID
                    'value':         , #str, property value
                    'status':        , #int, property status
                    'date':          , #str, date property was set
                    'name':          , #str, name of the property type
                    'description':   , #str, description of the property type
                    'unit':          , #str, property unit
                }
        '''
        
        # Check active interlock device ID
        _checkParameter('active interlock device ID', aid_id, 'prim')
        
        # Check property type name
        _checkParameter('prop type name', prop_type_name)
        
        # Generate SQL statement
        sql = '''
        SELECT
            aip.active_interlock_prop_id,
            aip.value,
            aip.status,
            aip.date,
            aipt.name,
            aipt.description,
            aipt.unit
        FROM active_interlock_prop aip
        LEFT JOIN active_interlock_prop_type aipt ON(aip.active_interlock_prop_type_id = aipt.active_interlock_prop_type_id)
        WHERE
        '''
        
        vals = []
        
        # Append active interlock id
        sql += " aip.active_interlock_device_id = %s "
        vals.append(aid_id)
        
        # Append property type name
        sqlVals = _checkWildcardAndAppend('aipt.name', prop_type_name, sql, vals, 'AND')
        
        try:
            # Execute sql
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])

            # Get any one since it should be unique
            res = cur.fetchall()
            resdict = {}

            # Generate return dictionary
            for r in res:
                resdict[r[0]] = {
                    'id': r[0],
                    'aid_id': aid_id,
                    'value': r[1],
                    'status': r[2],
                    'date': r[3].strftime(self.returnDateFormat),
                    'name': r[4],
                    'description': [5],
                    'unit': r[6]
                }

            return resdict

        except MySQLdb.Error as e:
            self.logger.info('Error when fetching active interlock property:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when fetching active interlock property:\n%s (%d)' %(e.args[1], e.args[0]))
        
    def saveActiveInterlockProp(self, aid_id, prop_type_name, value):
        '''
        Saves active interlock property into database. Property type must exist before saving property value.
        
        :param aid_id: Id of the saved active interlock
        :type aid_id: int
        
        :param prop_type_name: Name of the property type
        :type prop_type_name: string
        
        :param value: Value of the property
        :type value: string
        
        :returns:
            Python dictionary with structure::
            
                {'id': id of the new property}
        
        :raises:
            ValueError, MySQLError
        '''
        
        # Check active interlock device ID
        _checkParameter('active interlock device ID', aid_id, 'prim')
        
        # Retrieve property type name
        existingPropType = self.retrieveActiveInterlockPropType(prop_type_name)
        
        # Check if property type exists in the database
        if len(existingPropType) == 0:
            
            if prop_type_name in self.id_props_dict:
                prop_type = self.id_props_dict[prop_type_name]
            
            else:
                prop_type = self.bm_props_dict[prop_type_name]
            
            self.saveActiveInterlockPropType(prop_type_name, prop_type[1], prop_type[2])
            existingPropType = self.retrieveActiveInterlockPropType(prop_type_name)
        
        propTypeKeys = existingPropType.keys()
        propTypeObject = existingPropType[propTypeKeys[0]]
        
        # Set status
        status = 0
        
        if propTypeObject['description'] == 'approvable':
            status = 2
        
        sql = '''
        INSERT INTO active_interlock_prop (active_interlock_device_id, active_interlock_prop_type_id, value, status, date)
        VALUES
        (%s, %s, %s, %s, NOW())
        '''

        try:
            # Execute sql
            cur = self.conn.cursor()
            cur.execute(sql, (aid_id, propTypeObject['id'], value, status))

            # Get last row id
            propid = cur.lastrowid

            # Create transaction
            if self.transaction == None:
                self.conn.commit()

            return {'id': propid}

        except MySQLdb.Error as e:

            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()

            self.logger.info('Error when saving active interlock property:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when saving active interlock property:\n%s (%d)' %(e.args[1], e.args[0]))

    def updateActiveInterlockProp(self, aid_id, prop_type_name, value):
        '''
        Updates active interlock property in the database. Property type must exist before property value can be saved.
        
        :param ai_id: active interlock ID
        :type ai_id: int
        
        :param prop_type_name: name of the property type
        :type prop_type_name: str
        
        :param value: value of the property
        :type value: str
        
        :returns: boolean or Exception.
            True, if successful
        
        :raises:
            MySQLError, ValueError
        '''
        
        # Define query dict
        queryDict = {}
        whereDict = {}
        
        # Check property type
        proptype = self.retrieveActiveInterlockPropType(prop_type_name)
        
        if len(proptype) == 0:
            
            if prop_type_name in self.id_props_dict:
                prop_type = self.id_props_dict[prop_type_name]
            
            else:
                prop_type = self.bm_props_dict[prop_type_name]
            
            self.saveActiveInterlockPropType(prop_type_name, prop_type[1], prop_type[2])
            proptype = self.retrieveActiveInterlockPropType(prop_type_name)
        
        typeKeys = proptype.keys()
        typeObject = proptype[typeKeys[0]]
        whereDict['active_interlock_prop_type_id'] = typeObject['id']
        
        # Set status to unapproved if property is approvable
        if typeObject['description'] == 'approvable':
            queryDict['status'] = 2
        
        # Check active interlock device ID
        _checkParameter('active interlock device ID', aid_id, 'prim')
        whereDict['active_interlock_device_id'] = aid_id
        
        # Set value parameter
        queryDict['value'] = value
        
        # Generate SQL
        sqlVals = _generateUpdateQuery('active_interlock_prop', queryDict, None, None, whereDict)
        
        try:
            # Insert ai property data into database
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])
            
            # Create transactions
            if self.transaction == None:
                self.conn.commit()
                
            return True
        
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()

            self.logger.info('Error when updating active interlock property:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when updating active interlock property:\n%s (%d)' %(e.args[1], e.args[0]))

    def approveCells(self, aid_id, prop_types):
        '''
        Approves cells passed in the properties list. Status of the properties will be changed
        from unapproved (2) to approved (3)
        
        :param aid_id: active interlock device ID
        :type aid_id: int
        
        :param props: list of property type names that should be updated
        :type props: list
        
        :returns:
                True, if successful.
                Exception, if there is an error.
        '''
        
        # Define query dict
        queryDict = {}
        whereDict = {}
        
        # Check active interlock device ID
        _checkParameter('active interlock device ID', aid_id, 'prim')
        whereDict['active_interlock_device_id'] = aid_id
        
        try:
            
            # Convert to json
            if isinstance(prop_types, (dict)) == False:
                prop_types = json.loads(prop_types)
            
            # Go through all of the properties
            for prop in prop_types:
                
                if prop == 'num_unapproved':
                    continue
                
                # Check property type
                proptype = self.retrieveActiveInterlockPropType(prop)
                
                if len(proptype) == 0:
                    raise ValueError("Property type (%s) doesn't exist in the database!" % prop)
                
                typeKeys = proptype.keys()
                typeObject = proptype[typeKeys[0]]
                whereDict['active_interlock_prop_type_id'] = typeObject['id']
                
                # Set status parameter
                queryDict['status'] = 3
                
                # Generate SQL
                sqlVals = _generateUpdateQuery('active_interlock_prop', queryDict, None, None, whereDict)
                
                cur = self.conn.cursor()
                cur.execute(sqlVals[0], sqlVals[1])
        
            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
        
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error when updating active interlock device property:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error when updating active interlock device property:\n%s (%d)' % (e.args[1], e.args[0]))

    def retrieveDevice(self, ai_id = None, ai_status = None, name = None, definition = None, aid_id = None):
        '''
        Retrieves devices with the given active interlock name and definition. Name can also be a wildcard
        character to select all devices.
        
        :param ai_id: active interlock ID
        :type ai_id: int
        
        :param ai_status: active interlock status
        :type ai_status: int
        
        :param name: device name
        :type name: str
        
        :param definition: type of the dataset (bm/id)
        :type definition: str
        
        :param aid_id: active interlock device ID
        :type aid_id: int
        
        :returns:
            Retrieved Python dictionary with structure::
            
                {'id':
                    {'id':              , #int, id of the device in the database
                     'ai_id':           , #int, id of the active interlock
                     'name':            , #str, name of the device
                     'definition':      , #str, definition of the device
                     'logic':           , #str, name of the logic
                     'shape':           , #str, shape of the logic
                     'logic_code':      , #int, logic code
                     'prop1key':        , #str, first property
                     ...
                     'propNkey':        , #str, Nth property
                     'prop_statuses': {
                             'prop1key': , #int, status of the property,
                             ...
                             'propNkey': , #int, status of the property
                         },
                     'prop_units': {
                             'prop1key': , #string, property unit,
                             ...
                             'propNkey': , #string, property unit
                         }
                    }
                }
        
        :raises:
            ValueError, MySQLError
        '''
        
        # Check that status or id is set
        if ai_status == None and ai_id == None and aid_id == None:
            raise ValueError("Status or id must be provided to retrieve device from the database!")
        
        # Check active interlock id
        if ai_id != None:
            _checkParameter('active interlock id', ai_id, 'prim')
        
        # Check active interlock device ID
        if aid_id != None:
            _checkParameter('active interlock device ID', aid_id, 'prim')
        
        # Check status
        if ai_status != None:
            _checkParameter('active interlock status', ai_status, 'prim')
            
            if ai_id == None:
                ai = self.retrieveActiveInterlockHeader(ai_status)
                aiKeys = ai.keys()
                
                # Check the number of active interlocks
                if len(aiKeys) == 0:
                    return {}
                
                aiObject = ai[aiKeys[0]]
                ai_id = aiObject['id']
        
        # Check name
        _checkParameter('name', name)
        
        # Check definition
        _checkParameter('definition', definition)
        
        # Generate SQL statement
        vals = []
        sql = '''
        SELECT
            aid.active_interlock_device_id,
            aid.device_name,
            aid.definition,
            ail.name,
            ail.shape,
            ail.logic_code,
            aid.active_interlock_id
        FROM active_interlock_device aid
        LEFT JOIN active_interlock_logic ail ON(aid.active_interlock_logic_id = ail.active_interlock_logic_id)
        WHERE 1=1
        '''
        
        # Append active interlock id
        if ai_id != None:
            sql += " AND aid.active_interlock_id = %s "
            vals.append(ai_id)
        
        # Append active interlock device ID
        if aid_id != None:
            sql += " AND aid.active_interlock_device_id = %s "
            vals.append(int(aid_id))
        
        # Append device name
        sqlVals = _checkWildcardAndAppend('aid.device_name', name, sql, vals, 'AND')
        
        # Append definition
        sqlVals = _checkWildcardAndAppend('aid.definition', definition, sqlVals[0], sqlVals[1], 'AND')
        
        try:
            # Execute sql
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])

            # Get any one since it should be unique
            res = cur.fetchall()
            resdict = {}

            # Generate return dictionary
            for r in res:
                resdict[r[0]] = {
                    'id': r[0],
                    'ai_id': r[5],
                    'name': r[1],
                    'definition': r[2],
                    'logic': r[3],
                    'shape': r[4],
                    'logic_code': r[5],
                    'prop_statuses': {}
                }
                
                # Retrieve properties
                prop = self.retrieveActiveInterlockProp(r[0], '*')
                propKeys = prop.keys()
                
                numUnapproved = 0
                
                for key in propKeys:
                    resdict[r[0]][prop[key]['name']] = prop[key]['value']
                    propStatus = prop[key]['status']
                    
                    if propStatus == 2:
                        numUnapproved += 1
                    
                    resdict[r[0]]['prop_statuses'][prop[key]['name']] = propStatus
                    
                resdict[r[0]]['prop_statuses']['num_unapproved'] = numUnapproved

            return resdict

        except MySQLdb.Error as e:
            self.logger.info('Error when fetching active interlock device:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when fetching active interlock device:\n%s (%d)' %(e.args[1], e.args[0]))

    def saveDevice(self, ai_status, name, definition, logic, props, ai_id = None):
        '''
        Saves new device into database
        
        :param ai_id: active interlock ID
        :type ai_id: int
        
        :param ai_status: active interlock status
        :type ai_status: int
        
        :param name: active interlock device name
        :type name: str
        
        :param definition: definition of device. It can be bm (bending magnet) or id (insertion device)
        :type definition: str
        
        :param logic: name of the logic that must be saved in the database
        :type logic: str
        
        :param props: device property values in a Python dictionary format.
            
            Property dictionary for bending magnet should have the following structure::
            
                {
                    'bm_cell': '',
                    'bm_sequence': '',
                    'bm_type': '',
                    'bm_s': '',
                    'bm_aiolh': '',
                    'bm_aiorh': '',
                    'bm_aiolv': '',
                    'bm_aiorv': '',
                    'bm_safe_current': '',
                    'bm_in_use': ''
                }
            
            and property dictionary for insertion device should have the following structure::
                
                {
                    'cell': '',
                    'type': '',
                    'set': '',
                    'str_sect': '',
                    'defined_by': '',
                    's1_name': '',
                    's1_pos': '',
                    's1_pos_from': '',
                    's2_name': '',
                    's2_pos': '',
                    's2_pos_from': '',
                    's3_pos': '',
                    's3_pos_from': '',
                    'max_offset': '',
                    'max_angle': '',
                    'extra_offset': '',
                    'x_offset_s1': '',
                    'x_offset_origin_s1': '',
                    'x_offset_s2': '',
                    'x_offset_origin_s2': '',
                    'x_offset_s3': '',
                    'x_angle': '',
                    'y_offset_s1': '',
                    'y_offset_origin_s1': '',
                    'y_offset_s2': '',
                    'y_offset_origin_s2': '',
                    'y_offset_s3': '',
                    'y_angle': '',
                    'safe_current': '',
                    'in_use': ''
                }
            
        :type props: dict
        
        :return:
            Python dictionary with structure::
            
                 {'id': ID of the saved device}
        
        :raises:
            ValueError, MySQLError
        '''
        
        # Check that status or id is set
        if ai_status == None and ai_id == None:
            raise ValueError("Status or id must be provided to retrieve device from the database!")
        
        # Check active interlock id
        if ai_id != None:
            _checkParameter('active interlock id', ai_id, 'prim')
        
        # Check status
        if ai_status != None:
            _checkParameter('active interlock status', ai_status, 'prim')
            
            if ai_id == None:
                ai = self.retrieveActiveInterlockHeader(ai_status)
                aiKeys = ai.keys()
                aiObject = ai[aiKeys[0]]
                ai_id = aiObject['id']
        
        # Check name
        _checkParameter('name', name)
        
        # Check definition
        _checkParameter('definition', definition)
        
        # Get logic
        logic = self.retrieveActiveInterlockLogic(logic)
        
        if len(logic) == 0:
            raise ValueError("Logic (%s) doesn't exist in the database!" % logic)

        logicKeys = logic.keys()
        logicObject = logic[logicKeys[0]]
        
        # Generate SQL statement
        sql = '''
        INSERT INTO active_interlock_device (active_interlock_id, active_interlock_logic_id, device_name, definition)
        VALUES (%s, %s, %s, %s)
        '''

        try:
            # Execute sql
            cur = self.conn.cursor()
            cur.execute(sql, (ai_id, logicObject['id'], name, definition))

            # Get last row id
            deviceid = cur.lastrowid

            # Convert to json
            if isinstance(props, (dict)) == False:
                props = json.loads(props)

            # Save properties
            for datum in props:
                value = props[datum]
                
                self.saveActiveInterlockProp(deviceid, datum, value)

            # Create transaction
            if self.transaction == None:
                self.conn.commit()

            return {'id': deviceid}

        except MySQLdb.Error as e:

            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()

            self.logger.info('Error when saving active interlock device:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when saving active interlock device:\n%s (%d)' %(e.args[1], e.args[0]))

    def updateDevice(self, aid_id, name = None, logic = None):
        '''
        Updates device name and logic
        
        :param aid_id: active interlock device ID
        :type aid_id: int
        
        :param name: device name
        :type name: string
        
        :param logic: device logic name
        :type logic: string
        
        :return:
                True, if successful.
        '''
        
        # Define query dict
        queryDict = {}
        whereDict = {}
        
        # Check if there is something to update
        if name == None and logic == None:
            raise ValueError("There is nothing to update!")
        
        # Check logic
        if logic != None:
            retrieveLogic = self.retrieveActiveInterlockLogic(logic)
            
            if len(retrieveLogic) == 0:
                raise ValueError("There is no logic (%s) in the database!" % logic)
            
            logicKeys = retrieveLogic.keys()
            logicObj = retrieveLogic[logicKeys[0]]
            queryDict['active_interlock_logic_id'] = logicObj['id']
        
        # Set where
        whereDict['active_interlock_device_id'] = aid_id
        
        # Set name
        if name != None:
            queryDict['device_name'] = name
            
        # Generate SQL
        sqlVals = _generateUpdateQuery('active_interlock_device', queryDict, None, None, whereDict)
        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])

            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
            
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error when updating active interlock device:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error when updating active interlock device:\n%s (%d)' % (e.args[1], e.args[0]))

    def deleteDevice(self, aid_id):
        '''
        Deletes active interlock device by active interlock device ID
        
        :param aid_id: active interlock device ID
        :type aid_id: int
        
        :returns:
                True, if successful.
        
        :Raises:
            MySQLError
        '''

        # Check id
        _checkParameter('device id', aid_id, "prim")
        
        # Delete properties
        sqlP = '''
        DELETE FROM active_interlock_prop WHERE
        active_interlock_device_id = %s
        '''
        
        # Delete device
        sqlD = '''
        DELETE FROM active_interlock_device
        WHERE active_interlock_device_id = %s
        '''
        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlP, aid_id)
            cur.execute(sqlD, aid_id)

            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
            
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error while deleting active interlock device:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error while deleting active interlock device:\n%s (%d)' % (e.args[1], e.args[0]))

    def deleteActiveInterlock(self, status):
        '''
        Deletes active interlock by active interlock status
        
        :param status: active interlock status
        :type status: int
        
        :returns:
                True, if successful.
        
        :Raises:
            MySQLError
        '''
        
        # Get active interlock id with specific status
        ai = self.retrieveActiveInterlockHeader(status)
        aiKeys = ai.keys()
        
        # Check the length of the list
        if len(aiKeys) == 0:
            return {}
        
        aiObj = ai[aiKeys[0]]
        
        ai_id = aiObj['id']
        
        # Delete properties
        sqlP = '''
        DELETE FROM active_interlock_prop WHERE
        active_interlock_device_id IN (
            SELECT active_interlock_device_id
            FROM active_interlock_device
            WHERE active_interlock_id = %s
        );
        '''
        
        # Delete active interlock header
        sqlH = '''
        DELETE FROM active_interlock
        WHERE active_interlock_id = %s
        '''
        
        # Delete devices
        sqlD = '''
        DELETE FROM active_interlock_device
        WHERE active_interlock_id = %s
        '''
        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlP, ai_id)
            cur.execute(sqlD, ai_id)
            cur.execute(sqlH, ai_id)

            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
            
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error while deleting active interlock:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error while deleting active interlock:\n%s (%d)' % (e.args[1], e.args[0]))

    def retrieveStatusInfo(self):
        '''
        Retrieves information about active interlock status. The returned Python dictionary will include the number of datasets in each status.
        
        :returns:
            Returned Python dictionary with structure::
            
                {'status':
                    {
                        'status':,      #int
                        'num':,         #int
                        'ai_id':,       #int
                        'description':  #string
                    }
                }
        '''
        
        resdict = {}
        
        # Retrieve 0 status
        zero = self.retrieveActiveInterlockHeader(status=0)
        
        resdict[0] = {
            'status': 0,
            'num': len(zero)
        }
        
        # Append ai id
        if len(zero) > 0:
            zeroKeys = zero.keys()
            resdict[0]['ai_id'] = zeroKeys[0]
            resdict[0]['description'] = zero[zeroKeys[0]]['description']
        
        # Retrieve 1 status
        one = self.retrieveActiveInterlockHeader(status=1)
        
        resdict[1] = {
            'status': 1,
            'num': len(one)
        }
        
        # Append ai id
        if len(one) > 0:
            keys = one.keys()
            resdict[1]['ai_id'] = keys[0]
            resdict[1]['description'] = one[keys[0]]['description']
        
        # Retrieve 2 status
        two = self.retrieveActiveInterlockHeader(status=2)
        
        resdict[2] = {
            'status': 2,
            'num': len(two)
        }
        
        # Append ai id
        if len(two) > 0:
            keys = two.keys()
            resdict[2]['ai_id'] = keys[0]
            resdict[2]['description'] = two[keys[0]]['description']
        
        # Retrieve 3 status
        three = self.retrieveActiveInterlockHeader(status=3)
        
        resdict[3] = {
            'status': 3,
            'num': len(three)
        }
        
        # Append ai id
        if len(three) > 0:
            keys = three.keys()
            resdict[3]['ai_id'] = keys[0]
            resdict[3]['description'] = three[keys[0]]['description']
        
        # Retrieve 4 status
        four = self.retrieveActiveInterlockHeader(status=4)
        
        resdict[4] = {
            'status': 4,
            'num': len(four),
            'ai_id': 'multiple',
            'description': {}
        }
        
        # Go through headers
        for key in four.keys():
            obj = four[key]
            resdict[4]['description'][key] = obj['description']
        
        return resdict

    def downloadActiveInterlock(self, status, modified_by):
        '''
        Retrieves complete dataset by status and sets it to active if previous status is approved
        
        :param status: status of the active interlock to download
        :type status: int
        
        :param modified_by: user that last modified the active interlock dataset
        :type modified_by: string
        
        :return:
        
            Python dictionary with structure::
        
             {'bm':{
                     bm data
                 },
              'id': {
                    id data
                },
              'logic': {
                    logic data
                }
             }
        '''
        
        resdict = {}
        
        header = self.retrieveActiveInterlockHeader(status)
        
        # Check if header exists
        if len(header) == 0:
            resdict['result'] = "No dataset available"
            return resdict
        
        headerKeys = header.keys()
        headerObj = header[headerKeys[0]]
        
        # Get bm devices
        bm = self.retrieveDevice(headerObj['id'], None, "*", "bm")
        resdict['bm'] = bm
        
        # Get id devices
        idDev = self.retrieveDevice(headerObj['id'], None, "*", "id")
        resdict['id'] = idDev
        
        # Get logic
        logic = self.retrieveActiveInterlockLogic("*")
        resdict['logic'] = logic
        
        # Update status
        if str(status) == "1":
            self.updateActiveInterlockStatus(None, 1, 2, modified_by)
        
        return resdict

    def retrieveActiveInterlockHeader(self, status=None, id=None, datefrom=None, dateto=None):
        '''
        Retrieves a dataset according its saved time, status or ID.
        
        :param status: Current status.
        :type status: int
        
        :param id: ID in the database.
        :type id: int
        
        :param datefrom: data saved after this time. Default is None, which means data from very beginning. It has format as **yyyy-MM-dd hh:mm:ss** since dates in MySql are represented with this format.
        :type datafrom: datetime
        
        :param dateto: data saved before this time. Default is None, which means data till current. It has format as **yyyy-MM-dd hh:mm:ss** since dates in MySql are represented with this format.
        :type datato: datetime
        
        :param withdata: get dataset. Default is true, which means always gets data by default. Otherwise, only device names are retrieved for desired dataset.
        :type withdata: boolean
        
        :Returns:
            Python dictionary with structure::
        
             {'id': {
                     'status':,.
                     'id':,
                     'description':,
                     'created_by':,
                     'created_date':,
                     'modified_by':,
                     'modified_date':
                 }
             }
            
        :Raises: MySQLError, ValueError
        
        '''
        
        sql = '''
        select ai.active_interlock_id, ai.status, ai.description, 
        ai.created_by, ai.created_date, ai.modified_by, ai.modified_date
        from active_interlock ai
        where
        '''

        vals=[]
        
        # Check that status or id is set
        if status == None and id == None:
            raise ValueError("Status or id must be provided to retrieve active interlock header from the database!")
        
        # Append status
        if status != None:
            sqlVals = _checkWildcardAndAppend('ai.status', status, sql, vals)
            sql = sqlVals[0]
            vals = sqlVals[1]
            
        # Append id
        if id != None:
            sqlVals = _checkWildcardAndAppend('ai.active_interlock_id', id, sql, vals)
            sql = sqlVals[0]
            vals = sqlVals[1]
        
        # Append date from
        if datefrom != None:
            sql+= ' AND ai.created_date >= %s '
            vals.append(datefrom)
            
        # Append date to
        if dateto != None:
            sql+= ' AND ai.created_date <= %s '
            vals.append(dateto)
        
        try:
            # Execute sql
            cur=self.conn.cursor()
            cur.execute(sql, vals)
            res = cur.fetchall()
            
            resdict = {}
            
            # Generate return dictionary
            for r in res:
                tmp = {'status': r[1]}
                
                tmp['id'] = r[0]
                
                if r[2] != None:
                    tmp['description'] = r[2]
                
                if r[3] != None:
                    tmp['created_by'] = r[3]
                
                if r[4] != None:
                    tmp['created_date'] = r[4].strftime(self.returnDateFormat)
                
                if r[5] != None:
                    tmp['modified_by'] = r[5]
                
                if r[6] != None:
                    tmp['modified_date'] = r[6].strftime(self.returnDateFormat)

                resdict[r[0]] = tmp
    
            return resdict
            
        except MySQLdb.Error as e:
            self.logger.info('Error when fetching active interlock dataset headers:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when fetching active interlock dataset headers:\n%s (%d)' %(e.args[1], e.args[0]))

    def saveActiveInterlockHeader(self, description=None, created_by=None):
        '''
        Saves a new active interlock.
            
        :param description: comments or any other notes for this dataset.
        :type description: str
        
        :param created_by: the person who set this dataset.
        :type created_by: str
        
        :Returns: Active interlock internal ID if saved successfully.
            
        :Raises: ValueError, MySQLError

        '''
        
        # Check for created by parameter
        _checkParameter('author', created_by)
        
        # Create property types if there are none
        #self.saveDeviceProperties()
        
        # Save header onformation of a active interlock dataset
        sql = '''
        INSERT INTO active_interlock (created_date, status, created_by, description) VALUES (NOW(), 0, %s, %s)
        '''
        
        try:
            # Execute sql
            cur = self.conn.cursor()
            cur.execute(sql, (created_by, description))

            # Get last row id
            headerid = cur.lastrowid

            # Create transaction
            if self.transaction == None:
                self.conn.commit()

            return {'id': headerid}

        except MySQLdb.Error as e:

            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()

            self.logger.info('Error when saving active interlock header:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when saving active interlock header:\n%s (%d)' %(e.args[1], e.args[0]))

    def updateActiveInterlockHeader(self, description=None, modified_by=None):
        '''
        Updates active interlock header
        
        :param ai_id: active interlock ID
        :type ai_id: int
        
        :param description: active interlock description
        :type description: string
        
        :param modified_by: user that modified active interlock
        :type modified_by: string
        
        :return:
                True, if successful.
        '''
        
        # Define query dict
        queryDict = {}
        whereDict = {}
        
        # Set where
        whereDict['status'] = 0
        
        # Set description
        queryDict['description'] = description
            
        # Generate SQL
        sqlVals = _generateUpdateQuery('active_interlock', queryDict, None, None, whereDict)
        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])

            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
            
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error when updating active interlock:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error when updating active interlock:\n%s (%d)' % (e.args[1], e.args[0]))

    def retrieveActiveInterlockPropType(self, name, unit=None, description=None):
        '''
        Retrieve active interlock property type information with the given name, unit, and/or description.
        Each device involved in the active interlock system has some properties like offset, AIHOL/AIVOL, AIHAL/AIVAL, safe current, etc.
        
        Wildcard matching is supported with:
        
            - ``*`` to match multiple characters, 
            - ``?`` to match single characters.

        :param name: property type name.
        :type name: str
        
        :param unit: unit of given property type.
        :type unit: str
        
        :param description: description of given property type.
        :type description: str
        
        :returns:
            
            A Python dictionary is returned with each field as a list which could be converted into a table. Its structure is::
            
                {'id: 
                    {
                        'label':     , # str, columns's name
                        'id':          , # int, internal id of property type
                        'name':        , # str, active interlock property type name 
                        'unit':        , # str, active interlock property type unit
                        'description': , # str, property type description
                        'date':        , # datetime, when this entry was created
                    }
                }
        
        :raises: MySQLError, ValueError
        '''
        
        # Check name parameter
        _checkParameter('name', name)
        
        # Generate SQL statement
        vals = []
        sql = '''
        select active_interlock_prop_type_id, name, unit, description, created_date
        from active_interlock_prop_type where
        '''
        
        # Append name
        sqlVals = _checkWildcardAndAppend('name', name, sql, vals)

        # Append unit
        if unit != None:
            sqlVals = _checkWildcardAndAppend('unit', unit, sqlVals[0], sqlVals[1], 'AND')
            
        # Append description
        if description != None:
            sqlVals = _checkWildcardAndAppend('description', description, sqlVals[0], sqlVals[1], 'AND')
            
        try:
            # Execute SQL
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])
            
            res = cur.fetchall()
            resdict = {}
            
            # Generate return dictionary
            for r in res:
                resdict[r[0]] = {
                    'id': r[0],
                    'name': r[1],
                    'unit': r[2],
                    'description': r[3],
                    'date': r[4].strftime(self.returnDateFormat)
                }

            return resdict
        
        except MySQLdb.Error as e:
            self.logger.info('Error when fetching active interlock property type:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when fetching active interlock property type:\n%s (%d)' %(e.args[1], e.args[0]))
        
    def saveActiveInterlockPropType(self, name, unit=None, description=None):
        '''
        Save active interlock property type information with the given name, unit, and/or description.
        Each device involved in active interlock system has some properties like offset, AIHOL/AIVOL, AIHAL/AIVAL, safe current, etc.
        
        The property name with given unit is unique in the database. It allows a user to reuse a property type name, but to give it 
        a different unit.
        
        :param name: property type name.
        :type name: str
        
        :param unit: unit of given property type.
        :type unit: str
        
        :param description: description of given property type.
        :type description: str
        
        :returns:
            Python dictionary with structure::
            
                {'id': internal property type id}
            
        :raises: MySQLError, ValueError
        '''
        
        # Check name parameter
        _checkParameter('name', name)
        
        # Try to retrieve existing property type
        existingPropType = self.retrieveActiveInterlockPropType(name, unit=unit)
        
        if len(existingPropType):
            raise ValueError("Active interlock property type (%s) with unit (%s) already exists in the database!" % (name, unit));

        sql = '''
        insert into active_interlock_prop_type
        (name, unit, description, created_date)
        values (%s, %s, %s, now())
        '''
        try:
            cur = self.conn.cursor()
            cur.execute(sql, (name, unit, description))
            
            # Get last row id
            proptypeid = cur.lastrowid
            
            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return {'id': proptypeid}
                
        except MySQLError as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error when saving active interlock property type:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when saving active interlock property type:\n%s (%d)' %(e.args[1], e.args[0]))
            
    def isLogicUsed(self, logic):
        '''
        Retrieves the number of uses of the specified logic
        
        :param logic: name of the logic
        :type logic: str
        
        :return:
            Python dictionary with structure::
            
                {'num': usage count}
        '''
        
        # Check logic parameter
        _checkParameter('logic', logic)
        
        # Generate SQL
        vals = []
        sql = '''
        SELECT count(active_interlock_device_id) as num_used
        FROM active_interlock_device aid
        LEFT JOIN active_interlock_logic ail ON(aid.active_interlock_logic_id = ail.active_interlock_logic_id)
        WHERE
        '''
        
        # Append logic
        sqlVals = _checkWildcardAndAppend('ail.name', logic, sql, vals)
        
        try:
            # Execute SQL
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])
            res = cur.fetchone()
            resdict = {'num': res[0]}
            
            return resdict
            
        except MySQLdb.Error as e:
            self.logger.info('Error when fetching number of occaisons logic is used:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when fetching number of occaisons logic is used:\n%s (%d)' %(e.args[1], e.args[0]))
    
    def retrieveActiveInterlockLogic(self, name, shape=None, logic=None, status=None, ai_id=None):
        '''
        Retrieves logic information according to the given search constraints.
        The active interlock envelop name must be provided as a minimum input for this function.
        
        Wildcard matching is supported for name and shape with:
        
            - ``*`` to match multiple characters, 
            - ``?`` to match single characters.

        Wildcards are not supported for logic since * is a mathematical symbol.

        :param name: active interlock envelop name
        :type name: str
        
        :param shape: active interlock shape name in phase space.
        :type shape: str
        
        :param logic: active interlock logic.
        :type logic: str
        
        :param status: status of the logic
        :type status: int
        
        :param ai_id: active interlock ID
        :type ai_id: int
        
        :returns:
            
            A Python dictionary is returned with each field as a list which could be converted into a table. Its structure is::
            
                {'id':
                    {'label':          , # str, column's name
                     'id':             , # int, internal id of active interlock logic
                     'name':           , # str, name of active interlock envelop 
                     'shape':          , # str, allowed envelop shape in phase space
                     'logic':          , # str, logic expression
                     'code':           , # int, logic code for hardware convenience
                     'status':         , # int, satus of the logic
                     'created_by':     , # str, who created this entry
                     'created_date':   , # datetime, when this entry was created
                     'num':            , # int, usage count of this logic
                    }
                }
        
        :raises: MySQLError, ValueError
        '''
        
        # Check name paramater
        _checkParameter('name', name)
        
        # Generate SQL
        vals = []
        sql = '''
        select active_interlock_logic_id, name, shape, logic, logic_code, status, created_by, created_date
        from active_interlock_logic where
        '''
        
        # Append name
        sqlVals = _checkWildcardAndAppend('name', name, sql, vals)
        sql = sqlVals[0]
        vals = sqlVals[1]

        # Append shape
        if shape != None:
            sqlVals = _checkWildcardAndAppend('shape', shape, sql, vals, 'AND')
            sql = sqlVals[0]
            vals = sqlVals[1]
            
        # Append logic
        if logic != None:
            # wildmatch is supported for logic since the * is a math symbol.
            sql += ' AND logic = %s '
            vals.append(logic)
        
        # Append status
        if status != None:
            sqlVals = _checkWildcardAndAppend('status', status, sql, vals, 'AND')
            sql = sqlVals[0]
            vals = sqlVals[1]
            
        # Only logic user for specific active interlock
        if ai_id != None:
            sql += ' AND active_interlock_logic_id IN (SELECT DISTINCT active_interlock_logic_id FROM active_interlock_device WHERE active_interlock_id = %s) '
            vals.append(ai_id)
        
        try:
            # Execute SQL
            cur = self.conn.cursor()
            cur.execute(sql, vals)
            res = cur.fetchall()
            resdict = {}
            
            # Generate return dictionary
            for r in res:
                resdict[r[0]] = {
                    'id': r[0],
                    'name': r[1],
                    'shape': r[2],
                    'logic': r[3],
                    'code': r[4],
                    'status': r[5],
                    'created_by': r[6],
                    'created_date': r[7].strftime(self.returnDateFormat)
                }
                
                # Get and append usage
                usage = self.isLogicUsed(r[1])
                resdict[r[0]]['num'] = usage['num']

            return resdict
            
        except MySQLdb.Error as e:
            self.logger.info('Error when fetching active interlock logic:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when fetching active interlock logic:\n%s (%d)' %(e.args[1], e.args[0]))
    
    def saveActiveInterlockLogic(self, name, shape=None, logic=None, code=None, created_by=None):
        '''
        Saves logic information for the active interlock system.
        The time is automatically captured when the data is saved into the RDB.
        
        It checks whether the given envelop name with the given phase space shape and logic exists. If it does, then it raises a ValueError exception.
        
        :param name: active interlock envelop name
        :type name: str
        
        :param shape: active interlock shape name in phase space
        :type shape: str
        
        :param logic: active interlock logic expression
        :type logic: str
        
        :param code: logic algorithm encoding code for hardware convenience
        :type code: int

        :param created_by: user who first created this dataset
        :type created_by: str
            
        :returns:
            Python dictionary with structure::
            
                {'id': internal id of active interlock logic}
                
        :Raises: ValueError, Exception
        '''
        
        # here logic code should be configured in system configure file, and user configurable.
        # allowed logic code should be checked here.
        # It will be added in next implementation.
        
        # Check name parameter
        _checkParameter('name', name)
        
        existingLogic = self.retrieveActiveInterlockLogic(name, shape=shape, logic=logic)
        
        if len(existingLogic):
            raise ValueError("Active interlock logic (%s) already exists in the database!" % name);

        # Generate SQL statement
        sql = '''
        insert into active_interlock_logic
        (name, shape, logic, logic_code, created_by, status, created_date)
        values
        (%s, %s, %s, %s, %s, 2, now())
        '''

        try:
            # Execute SQL
            cur=self.conn.cursor()
            cur.execute(sql, (name, shape, logic, code, created_by))
            
            # Return last row id
            logicid = cur.lastrowid
            
            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return {'id': logicid}
                
        except Exception as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error when saving active interlock logic:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when saving active interlock logic:\n%s (%d)' %(e.args[1], e.args[0]))

    def updateActiveInterlockLogic(self, id, name=None, shape=None, logic=None, code=None, status=None):
        '''
        Saves logic information for active interlock system.
        The time is automatically captured when the data is saved into the RDB.
        
        It checks whether the given envelop name with the given phase space shape and logic exists. If it does, then it raises a ValueError exception.
        
        The current implementation assumes that an active interlock envelop applies to a particular shape, which is globally unique. 
        If the logic is changed, a new name should be defined.
        
        :param id: active interlock envelop ID
        :type id: int
        
        :param name: active interlock envelop name
        :type name: str
        
        :param shape: active interlock shape name in phase space
        :type shape: str
        
        :param logic: active interlock logic expression
        :type logic: str
        
        :param code: logic algorithm encoding code for hardware convenience
        :type code: int
            
        :returns: 
            True, if successful.
                
        :Raises: ValueError, Exception
        '''
        
        # Define query dict
        queryDict = {}
        whereDict = {}
    
        # Check id parameter
        _checkParameter('id', id, "prim")
        whereDict['active_interlock_logic_id'] = id
        
        # Set status
        if status != None:
            queryDict['status'] = status
            
        else:
            queryDict['status'] = 2
        
        # Set name parameter
        if name != None:
            queryDict['name'] = name
        
        # Set shape parameter
        if shape != None:
            queryDict['shape'] = shape
        
        # Set logic parameter
        if logic != None:
            queryDict['logic'] = logic
            
        # Set code parameter
        if code != None:
            queryDict['logic_code'] = code
            
        # Generate SQL
        sqlVals = _generateUpdateQuery('active_interlock_logic', queryDict, None, None, whereDict)
        
        try:
            # Update logic
            cur = self.conn.cursor()
            cur.execute(sqlVals[0], sqlVals[1])
            
            # Create transactions
            if self.transaction == None:
                self.conn.commit()
                
            return True
        
        except Exception as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()

            self.logger.info('Error when updating active interlock logic:\n%s (%d)' %(e.args[1], e.args[0]))
            raise MySQLError('Error when updating active interlock logic:\n%s (%d)' %(e.args[1], e.args[0]))

    def deleteActiveInterlockLogic(self, logic_id):
        '''
        Deletes active interlock logic by active interlock logic ID
        
        :param logic_id: active interlock logic ID
        :type logic_id: int
        
        :returns:
            True, if successful.
        
        :Raises:
            MySQLError
        '''

        # Check id
        _checkParameter('logic id', logic_id, "prim")
        
        # Delete logic
        sqlL = '''
        DELETE FROM active_interlock_logic
        WHERE active_interlock_logic_id = %s
        '''
        
        try:
            cur = self.conn.cursor()
            cur.execute(sqlL, logic_id)

            # Create transaction
            if self.transaction == None:
                self.conn.commit()
                
            return True
            
        except MySQLdb.Error as e:
            
            # Rollback changes
            if self.transaction == None:
                self.conn.rollback()
            
            self.logger.info('Error while deleting active interlock logic:\n%s (%d)' % (e.args[1], e.args[0]))
            raise MySQLError('Error while deleting active interlock logic:\n%s (%d)' % (e.args[1], e.args[0]))

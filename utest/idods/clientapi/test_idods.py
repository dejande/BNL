'''
Created on Feb 17, 2014

@author: dejan.dezman@cosylab.com
'''
import os
import sys

import unittest
import logging
import requests
import random

import inspect
from requests import HTTPError

from idods.rdbutils.preparerdb import *

libPath = os.path.abspath("../../../clientapi/")
sys.path.append(libPath)

from idodspy.idodsclient import IDODSClient


class Test(unittest.TestCase):

    __url = 'http://localhost:8000/id/device/'
    __jsonheader = {'content-type': 'application/json', 'accept': 'application/json'}

    def cleanTables(self):

        cleanDB()

    def setUp(self):
        self.cleanTables()
        self.client = IDODSClient(BaseURL=self.__url)

        try:
            requests_log = logging.getLogger("requests")
            requests_log.setLevel(logging.DEBUG)

        except:
            raise

    def tearDown(self):
        self.cleanTables()

    '''
    Try to save and update a vendor
    '''
    def testVendor(self):

        # Save new vendor
        self.client.saveVendor('test vendor')

        # Test retrieving vendor by its name
        result = self.client.retrieveVendor('test vendor')
        resultKeys = result.keys()

        self.assertEqual(result[resultKeys[0]]['name'], 'test vendor', 'Verdor retrieved')

        # Test retrieving vendor without a name
        self.assertRaises(HTTPError, self.client.retrieveVendor, None)

        # Update vendor
        self.client.updateVendor('test vendor', 'test vendor2', description='desc')

        # Test retrieving vendor by its name
        result = self.client.retrieveVendor('test vendor2')
        resultKeys = result.keys()
        resultObject = result[resultKeys[0]]

        # Test name
        self.assertEqual(resultObject['name'], 'test vendor2')

        # Test description
        self.assertEqual(resultObject['description'], 'desc')

    '''
    Test saving, retrieving and updating component type
    '''
    def testCmpntType(self):

        # Save component type property type
        self.client.saveComponentTypePropertyType('length', 'test description')

        # Save new component type
        cmpntid = self.client.saveComponentType('test cmpnt3', 'test description', props={'length': 4.354})

        # Retrieve component type
        result = self.client.retrieveComponentType('test cmpnt3')
        resultKeys = result.keys()
        resultObject = result[resultKeys[0]]

        # Check if returned name is the same as saved one
        self.assertEqual(resultObject['name'], 'test cmpnt3', 'We got back the right component type')

        # Check if property was successfully saved in the database
        self.assertTrue('length' in resultObject and resultObject['length'] == '4.354', "Component type property in the database")

        # Save new component type with the same name and same description, it should raise an error
        self.assertRaises(HTTPError, self.client.saveComponentType, 'test cmpnt3', 'test description')

        # Try to save new component type without a name
        self.assertRaises(HTTPError, self.client.saveComponentType, None)

        # Try updating
        self.assertTrue(self.client.updateComponentType('test cmpnt3', 'Magnet', description='desc', props={'length': 3}))

        # Retrieve component type
        result = self.client.retrieveComponentType('Magnet')
        resultKeys = result.keys()
        resultObject = result[resultKeys[0]]

        # Check if returned name is the same as saved one
        self.assertEqual(resultObject['name'], 'Magnet', 'We got back the right component type')

        # Check returned description
        self.assertEqual(resultObject['description'], 'desc')

        # Check returned length
        self.assertEqual(resultObject['length'], '3')

    '''
    Test saving, retrieving and updating component type property type
    '''
    def testCmpntTypePropType(self):

        # Save component type property type
        propertyType = self.client.saveComponentTypePropertyType('length', 'test description')

        # Retrieve component type property type
        retrievedPropertyType = self.client.retrieveComponentTypePropertyType('length')
        retrievedPropertyTypeKeys = retrievedPropertyType.keys()
        retrievedPropertyTypeObject = retrievedPropertyType[retrievedPropertyTypeKeys[0]]

        # Check if name was saved
        self.assertEqual(retrievedPropertyTypeObject['name'], 'length')

        # Check if description was saved
        self.assertEqual(retrievedPropertyTypeObject['description'], 'test description')

        # Try to update with a new name by old name
        self.assertTrue(self.client.updateComponentTypePropertyType('length', 'width'))

    '''
    Test saving, retrieving and updating inventory
    '''
    def testInventory(self):

        # Save new vendor
        self.client.saveVendor('test vendor')

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Try to save new inventory property template
        self.client.saveInventoryPropertyTemplate('Magnet', 'alpha')

        # Create inventory
        idObject = self.client.saveInventory('23524', name='name', cmpnt_type_name='Magnet', vendor_name='test vendor', alias='name2', props={'alpha': 42})

        # Update inventory
        self.assertTrue(self.client.updateInventory(idObject['id'], '23524', name='name2', cmpnt_type_name='Magnet', alias='name3', props={'alpha': 43}))

        # Get updated inventory
        inventory = self.client.retrieveInventory('23524', cmpnt_type_name='Magnet')
        inventoryKeys = inventory.keys()
        inventoryObject = inventory[inventoryKeys[0]]

        # Check if ids are the same
        self.assertEqual(inventoryObject['id'], idObject['id'], "Ids should stay the same!")

        # Check if alpha property value has changed
        self.assertEqual(inventoryObject['alpha'], '43', "Check if property has changed")

        # Check component type
        self.assertEqual(inventoryObject['cmpnt_type_name'], 'Magnet')

        # Check alias
        self.assertEqual(inventoryObject['alias'], 'name3')

        # Check vendor
        self.assertEqual(inventoryObject['vendor'], 'test vendor')

    '''
    Test saving, retrieving and updating inventory property template
    '''
    def testInventoryPropTmplt(self):

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Try to save new inventory property template
        idObject = self.client.saveInventoryPropertyTemplate('Magnet', 'alpha', 'desc', 'default', 'units')

        # Update template
        self.assertTrue(self.client.updateInventoryPropertyTemplate(idObject['id'], 'Magnet', 'beta'))

        # Retrieve updated template
        template = self.client.retrieveInventoryPropertyTemplate('beta')
        templateKeys = template.keys()
        templateObject = template[templateKeys[0]]

        # Check if ids are the same
        self.assertEqual(idObject['id'], templateObject['id'], "Ids should be the same")

        # Check if description stayed the same
        self.assertEqual(templateObject['description'], 'desc')

        # Check name
        self.assertEqual(templateObject['name'], 'beta')

    '''
    Test saving, retrieving and updating install
    '''
    def testInstall(self):

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Prepare install
        savedInstall = self.client.saveInstall('test parent', cmpnt_type_name='Magnet', description='desc', coordinatecenter=2.2)

        # Try to update
        self.assertTrue(self.client.updateInstall('test parent', 'test child', cmpnt_type_name='Magnet', description='desc2'))

        # Try to update by setting component type to None
        # self.assertRaises(HTTPError, self.client.updateInstall, savedInstall['id'], 'test child', cmpnt_type_name=None)

        # Retrieve successfully updated component type
        componentType = self.client.retrieveInstall('test child')
        componentTypeKeys = componentType.keys()
        componentTypeObject = componentType[componentTypeKeys[0]]

        # Check ids
        self.assertEqual(savedInstall['id'], componentTypeObject['id'])

        # Check description
        self.assertEqual(componentTypeObject['description'], 'desc2')

        # Check coordinate center
        self.assertEqual(componentTypeObject['coordinatecenter'], 2.2)

        # Check name
        self.assertEqual(componentTypeObject['name'], 'test child')

        # Check component type
        self.assertEqual(componentTypeObject['cmpnt_type_name'], 'Magnet')

    '''
    Test saving, retrieving and updating install rel
    '''
    def testInstallRel(self):

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Prepare install parent
        self.client.saveInstall('test parent', cmpnt_type_name='Magnet', description='desc', coordinatecenter=2.2)

        # Prepare install child
        self.client.saveInstall('test child', cmpnt_type_name='Magnet')

        # Prepare prop type
        self.client.saveInstallRelPropertyType('testprop')

        # Save rel
        self.client.saveInstallRel('test parent', 'test child', 'desc', 1, {'testprop': 'testvalue'})

        # Try to update
        self.assertTrue(self.client.updateInstallRel('test parent', 'test child', description='descupd', order=2, props={'testprop': 'value'}))

        # Retrieve rel
        retrievedRel = self.client.retrieveInstallRel(None, 'test parent', 'test child')
        retrievedRelKeys = retrievedRel.keys()
        retrievedRelObject = retrievedRel[retrievedRelKeys[0]]

        # Check description
        self.assertEqual(retrievedRelObject['description'], 'descupd')

        # Check order
        self.assertEqual(retrievedRelObject['order'], 2)

        # Check test property
        self.assertEqual(retrievedRelObject['testprop'], 'value')

        # Test saving another rel with same parent and child
        self.assertRaises(HTTPError, self.client.saveInstallRel, 'test parent', 'test child', None, None)

        # Test saving install rel with property that is not defined
        self.assertRaises(HTTPError, self.client.saveInstallRel, 'test child', 'test parent', None, None, {'testprop2': 'testvalue'})

    '''
    Test saving, retrieving and updating install rel property type
    '''
    def testInstallRelPropertyType(self):

        # Prepare prop type
        propType = self.client.saveInstallRelPropertyType('testprop')

        # Try to update
        self.assertTrue(self.client.updateInstallRelPropertyType('testprop', 'prop2', description='desc', unit='units'))

        # Retrieve updated property type
        updatedPropType = self.client.retrieveInstallRelPropertyType('prop2')
        updatedPropTypeKeys = updatedPropType.keys()
        updatedPropTypeObject = updatedPropType[updatedPropTypeKeys[0]]

        # Check ids
        self.assertEqual(propType['id'], updatedPropTypeObject['id'])

        # Check if units are still the same
        self.assertEqual(updatedPropTypeObject['unit'], 'units')

        # Check if description is still the same
        self.assertEqual(updatedPropTypeObject['description'], 'desc')

        # Check name
        self.assertEqual(updatedPropTypeObject['name'], 'prop2')

    '''
    Test saving, retrieving and updating inventory to install map
    '''
    def testInventoryToInstall(self):

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Try to save new inventory property template
        self.client.saveInventoryPropertyTemplate('Magnet', 'alpha')

        # Create inventory
        inv = self.client.saveInventory('1236423', name='name', vendor_name=None, cmpnt_type_name='Magnet', alias='name2', props={'alpha': 42})
        inv2 = self.client.saveInventory('4324', name='name2', vendor_name=None, cmpnt_type_name='Magnet', alias='name2')

        # Prepare install parent
        self.client.saveInstall('test parent', cmpnt_type_name='Magnet', description='desc', coordinatecenter=2.2)

        # Map install to inventory
        map = self.client.saveInventoryToInstall('test parent', inv['id'])

        # Retrieve saved map
        retrieveMap = self.client.retrieveInventoryToInstall(None, 'test parent', inv['id'])
        retrieveMapKeys = retrieveMap.keys()
        retrieveMapObject = retrieveMap[retrieveMapKeys[0]]

        # Check if saved and retrieved maps are equal
        self.assertEqual(map['id'], retrieveMapObject['id'])

        # Set install to a new inventory
        self.assertTrue(self.client.updateInventoryToInstall(map['id'], 'test parent', inv2['id']))

    '''
    Test saving, retrieving and updating data method
    '''
    def testUpdateDataMethod(self):
        # Save data method with name and description
        saveDataMethod = self.client.saveDataMethod('method', 'description')

        # Try updating by old name
        self.assertTrue(self.client.updateDataMethod('method', 'method2', description='new desc'))

        # Get updated data method
        updatedDataMethod = self.client.retrieveDataMethod('method2')
        updatedDataMethodKeys = updatedDataMethod.keys()
        updatedDataMethodObject = updatedDataMethod[updatedDataMethodKeys[0]]

        # Check ids
        self.assertEqual(saveDataMethod['id'], updatedDataMethodObject['id'])

        # Check new description
        self.assertEqual(updatedDataMethodObject['description'], 'new desc',)

        # Update by an id
        self.assertTrue(self.client.updateDataMethod('method', 'method', description='new desc2'))

        # Update should fail if there is no id or old name present
        self.assertRaises(HTTPError, self.client.updateDataMethod, None, 'method2')

    '''
    Test saving, retrieving and updating offline data
    '''
    def testOfflineData(self):

        # Prepare data method
        self.client.saveDataMethod('method', 'description')

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Prepare inventory
        inv = self.client.saveInventory('serial', vendor_name=None, name='name', cmpnt_type_name='Magnet', alias='name2')

        # Prepare install
        self.client.saveInstall('install', cmpnt_type_name='Magnet')

        # Connect install in inventory
        self.client.saveInventoryToInstall('install', inv['id'])

        # Create offline data
        savedOfflineData = self.client.saveOfflineData(inventory_id=inv['id'], method_name='method', status=1, data='../dataapi/download_128', data_file_name='datafile', gap=3.4, description='spec1234desc')

        # Update offline data
        self.assertTrue(self.client.updateOfflineData(savedOfflineData['id'], status=2, phase1=2.4, data='large2', phasemode='p', data_file_ts='2014-02-03'))

        # Retrieve updated offline data by id
        updatedData = self.client.retrieveOfflineData(offlineid=savedOfflineData['id'], with_data=True)
        updatedDataKeys = updatedData.keys()
        updatedDataObject = updatedData[updatedDataKeys[0]]

        # Check status
        self.assertEqual(updatedDataObject['status'], 2)

        # Check gap
        self.assertEqual(updatedDataObject['gap'], 3.4)

        # Check phase mode
        self.assertEqual(updatedDataObject['phasemode'], 'p')

        # Check raw data id
        self.assertNotEqual(updatedDataObject['data_id'], 0)

        # Check data
        self.assertNotEqual(updatedDataObject['data'], '')

        # Retrieve updated offline data by id
        retData = self.client.retrieveInstallOfflineData(install_name='install')
        retDataKeys = retData.keys()

        # There should be eno returned
        self.assertEqual(len(retDataKeys), 1)

        # Delete offline data
        self.assertTrue(self.client.deleteOfflineData(savedOfflineData['id']))

        # Try to retrieve deleted offline data
        retrievedData = self.client.retrieveOfflineData(offlineid=savedOfflineData['id'])
        retrievedDataKeys = retrievedData.keys()

        # There should be none returned
        self.assertEqual(len(retrievedDataKeys), 0)

    '''
    Test retrieving, saving and updating online data
    '''
    def testOnlineData(self):

        # Prepare component type
        self.client.saveComponentType('Magnet')

        # Prepare install parent
        self.client.saveInstall('test parent', cmpnt_type_name='Magnet', description='desc', coordinatecenter=2.2)

        # Save online data
        onlineid = self.client.saveOnlineData('test parent', username='username', description='desc1234', rawdata_path='../dataapi/download_128', feedforward_file_name='datafile', status=1)

        # Update online data
        self.assertTrue(self.client.updateOnlineData(onlineid['id'], username='username2', rawdata_path='../dataapi/download_128', feedforward_file_name='datafile123'))

        # Retrieve online data
        retrievedOnlineData = self.client.retrieveOnlineData(onlineid=onlineid['id'])
        retrievedOnlineDataKeys = retrievedOnlineData.keys()
        retrievedOnlineDataObject = retrievedOnlineData[retrievedOnlineDataKeys[0]]

        # Test URL
        self.assertTrue('datafile' in retrievedOnlineDataObject['feedforward_file_name'])

        # Test status
        self.assertEqual(1, retrievedOnlineDataObject['status'])

        # Save online data with feedforward table
        onlineid = self.client.saveOnlineData('test parent', username='username', description='desc1234', rawdata_path='../dataapi/download_128', feedforward_file_name='datafile', feedforward_data='some data', status=1)

        # Retrieve online data
        retrievedOnlineData = self.client.retrieveOnlineData(onlineid=onlineid['id'])
        retrievedOnlineDataKeys = retrievedOnlineData.keys()
        retrievedOnlineDataObject = retrievedOnlineData[retrievedOnlineDataKeys[0]]

        # Check data
        self.assertNotEqual(retrievedOnlineDataObject['feedforward_data'], '')

    def testUploadingLargeFile(self):

        # Upload a file
        uploadedFile = self.client.uploadFile('large', 'new_file')

        # Test file path
        self.assertNotEqual(uploadedFile['path'], '')

    def testRotCoilData(self):
        '''
        Test rot coil data
        '''
        cmpnt = self.client.saveComponentType('Magnet')
        inv = self.client.saveInventory('1341', vendor_name=None, name='name2', cmpnt_type_name='Magnet', alias='name2')
        rcd = self.client.saveRotCoilData(inv['id'], 'alias')
        self.assertNotEqual(rcd['id'], 0)

        # Retrieve rot coil data
        data = self.client.retrieveRotCoilData(inv['id'])

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 1)

        # Test update
        self.assertTrue(self.client.updateRotCoilData(rcd['id'], login_name='admin'))

        # Retrieve rot coil data
        data = self.client.retrieveRotCoilData(inv['id'])

        # # Test the number of items in the table
        self.assertEqual(len(data.keys()), 1)
        firstKey = data.keys()[0]

        self.assertEqual(data[firstKey]['inventory_id'], inv['id'])
        self.assertEqual(data[firstKey]['alias'], 'alias')

        # Test deleting with an error in function call
        self.assertRaises(self.client.deleteRotCoilData, None)

        # Test deleting
        self.assertTrue(self.client.deleteRotCoilData(inv['id'], data[firstKey]['id']))

    def testHallProbeData(self):
        '''
        Test hall probe data
        '''
        cmpnt = self.client.saveComponentType('Magnet')
        inv = self.client.saveInventory('12341', vendor_name=None, name='name2', cmpnt_type_name='Magnet', alias='name2')
        hpd = self.client.saveHallProbeData(inv['id'], 'sub device')
        self.assertNotEqual(hpd['id'], 0)

        # Retrieve hall probe data
        data = self.client.retrieveHallProbeData(inv['id'])

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 1)

        # Test update
        self.assertTrue(self.client.updateHallProbeData(hpd['id'], login_name='admin'))

        # # Retrieve rot coil data
        data = self.client.retrieveHallProbeData(inv['id'])

        # # Test the number of items in the table
        self.assertEqual(len(data.keys()), 1)
        firstKey = data.keys()[0]

        self.assertEqual(data[firstKey]['inventory_id'], inv['id'])
        self.assertEqual(data[firstKey]['sub_device'], 'sub device')

        # Test deleting with an error in function call
        self.assertRaises(self.client.deleteHallProbeData, None)

        # Test deleting
        self.assertTrue(self.client.deleteHallProbeData(inv['id'], data[firstKey]['id']))

    def testComponentTypeRotCoilData(self):
        '''
        Test component type rot coil data
        '''

        cmpnt = self.client.saveComponentType('Magnet')

        # Try retrieving without first saving it
        self.assertRaises(HTTPError, self.client.retrieveComponentTypeRotCoilData, 'Magnet')

        hpd = self.client.saveComponentTypeRotCoilData('Magnet', 'sub device', b2=2.4)
        hpd2 = self.client.saveComponentTypeRotCoilData('Magnet', 'sub device2', roll_angle=1)

        # Retrieve rot coil data
        data = self.client.retrieveComponentTypeRotCoilData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 2)

        firstKey = data.keys()[1]

        self.assertEqual(data[hpd['id']]['cmpnt_type_id'], cmpnt['id'])
        self.assertEqual(data[hpd['id']]['cmpnt_type_name'], 'Magnet')
        self.assertEqual(data[hpd['id']]['b2'], str(2.4))

        # Test update
        self.assertTrue(self.client.updateComponentTypeRotCoilData(hpd['id'], 'Magnet', b2=2.5))

        # Retrieve rot coil data
        data = self.client.retrieveComponentTypeRotCoilData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 2)

        firstKey = data.keys()[1]

        self.assertEqual(data[hpd['id']]['cmpnt_type_id'], cmpnt['id'])
        self.assertEqual(data[hpd['id']]['cmpnt_type_name'], 'Magnet')
        self.assertEqual(data[hpd['id']]['b2'], str(2.5))

        # Delete rot coil data
        self.assertTrue(self.client.deleteComponentTypeRotCoilData('Magnet', hpd['id']))

        # Retrieve rot coil data
        data = self.client.retrieveComponentTypeRotCoilData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 1)

        # Delete rot coil data
        self.assertTrue(self.client.deleteComponentTypeRotCoilData('Magnet', hpd2['id']))

        # Retrieve rot coil data
        data = self.client.retrieveComponentTypeRotCoilData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 0)

    def testComponentTypeHallProbeData(self):
        '''
        Test component type hall probe data
        '''

        cmpnt = self.client.saveComponentType('Magnet')

        # Try retrieving without first saving it
        self.assertRaises(HTTPError, self.client.retrieveComponentTypeHallProbeData, 'Magnet')

        hpd = self.client.saveComponentTypeHallProbeData('Magnet', 'sub device', up_dn2=2.4)
        hpd2 = self.client.saveComponentTypeHallProbeData('Magnet', 'sub device2', bx_t=1)

        # Retrieve hall probe data
        data = self.client.retrieveComponentTypeHallProbeData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 2)

        firstKey = data.keys()[1]

        self.assertEqual(data[hpd['id']]['cmpnt_type_id'], cmpnt['id'])
        self.assertEqual(data[hpd['id']]['cmpnt_type_name'], 'Magnet')
        self.assertEqual(data[hpd['id']]['up_dn2'], str(2.4))

        # Test update
        self.assertTrue(self.client.updateComponentTypeHallProbeData(hpd['id'], 'Magnet', up_dn2=2.5))

        # Retrieve hall probe data
        data = self.client.retrieveComponentTypeHallProbeData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 2)

        firstKey = data.keys()[1]

        self.assertEqual(data[hpd['id']]['cmpnt_type_id'], cmpnt['id'])
        self.assertEqual(data[hpd['id']]['cmpnt_type_name'], 'Magnet')
        self.assertEqual(data[hpd['id']]['up_dn2'], str(2.5))

        # Delete hall probe data
        self.assertTrue(self.client.deleteComponentTypeHallProbeData('Magnet', hpd['id']))

        # Retrieve hall probe data
        data = self.client.retrieveComponentTypeHallProbeData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 1)

        # Delete hall probe data
        self.assertTrue(self.client.deleteComponentTypeHallProbeData('Magnet', hpd2['id']))

        # Retrieve hall probe data
        data = self.client.retrieveComponentTypeHallProbeData('Magnet')

        # Test the number of items in the table
        self.assertEqual(len(data.keys()), 0)

    def testDevice(self):
        '''
        Test retrieving, saving and updating devices
        '''

        # Save a device
        deviceID = self.client.saveDevice(device_name="device_name", cmpnt_type_name="cmpnt_type_name", device_description="device_description", device_coordinatecenter=None, cmpnt_type_description="cmpnt_type_description", cmpnt_type_props=None)

        # Retrieve a device
        self.assertEqual(len(self.client.retrieveDevice("device_name", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 1)
        self.assertEqual(len(self.client.retrieveDevice("*", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 1)

        # Save another device
        deviceID = self.client.saveDevice(device_name="device_name2", cmpnt_type_name="cmpnt_type_name", device_description="device_description", device_coordinatecenter=None, cmpnt_type_description="cmpnt_type_description", cmpnt_type_props=None)

        # Retrieve a device
        self.assertEqual(len(self.client.retrieveDevice("device_name2", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 1)
        self.assertEqual(len(self.client.retrieveDevice("*", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 2)

        # Update a device
        if len(self.client.retrieveDevice("device_name_new", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()) == 0:
            self.assertTrue(self.client.updateDevice("device_name", "device_name_new", description=None, cmpnt_type_name=None, coordinatecenter=None))

        # Retrieve a device
        self.assertEqual(len(self.client.retrieveDevice("device_name", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 0)
        self.assertEqual(len(self.client.retrieveDevice("device_name_new", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 1)
        self.assertEqual(len(self.client.retrieveDevice("*", description=None, cmpnt_type_name=None, coordinatecenter=None).keys()), 2)

if __name__ == "__main__":
    unittest.main()
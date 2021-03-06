'''
This script is to read data related to magnet unit conversion for NSLS II injector system,
and save all data into IRMIS database.

Created on Jan 28, 2013

@author: shengb
'''
from __future__ import print_function
import os
import sys

import xlrd

try:
    import simplejson as json
except ImportError:
    import json

from pymuniconv import municonvdata

from devicelist import (dipoletype2draw, quadtype2draw, sexttype2draw, cortype2draw, hcortype2draw, vcortype2draw)
from pymuniconv.municonvprop import (proptmplt, proptmpltdesc, cmpnttypeproptype, cmpnttypeproptypedesc)
from rdbinfo import (host, user, pw, db)

draw2typedict = {}

def __readdata(xlname, sheetno=0, sheetname=None):
    '''Read data from Excel spreadsheet file using xlrd library.
    '''
    # the working spreadsheet will be close by open_workbook() method automatically when returning
    # unless using on_demand=True. If on_demand is turned True, the file is not closed, even if the workbook is collected.
    # Should be careful to call release_resources() before letting the workbook go away..
    wb = xlrd.open_workbook(xlname)
    sh = wb.sheet_by_index(sheetno)
    
    raw_data = []
    for rownum in range(sh.nrows):
        raw_data.append(sh.row_values(rownum))
    return raw_data

def filecrawler(root):
    '''
    search all data files under root directory.
    Assume the directory has structure like as below:
        /root
            |-- Hall_Maps
            |   |-- Latest_Data
            |   |   |-- BuckleyDataFromWGuo
            |   |   |   |-- ...
            |   |   |   `-- ...
            |   |   |-- ...
            |   |   `-- ...
            |   `-- Obsolete_Data
            |       |-- ...
            |       `-- ...
            `-- RotatingCoil
                |-- Latest_Data
                |   |-- ...
                |   `-- ...
                `-- Obsolete_Data
                    |-- ...
                    `-- ...

    '''
    for path, _, files in os.walk(root):
        for name in files:
            if 'Latest_Data' in path:
                yield (os.path.join(path, name))

def __savecmpnttype(ctptid, data, updatemap=True):
    '''
    '''
    for val in data:
        ctypeid = municonv.retrievecmpnttype(val[0], val[1])
        if len(ctypeid) == 0:
            ctypeid = municonv.savecmpnttype(val[0], val[1])
        else:
            ctypeid = ctypeid[0][0]
        ctypepropid = municonv.retrievecmpnttypeprop(ctypeid, ctptid)
        if len(ctypepropid) == 0:
            ctypepropid = municonv.savecmpnttypeprop(val[2], ctypeid, ctptid)
        else:
            municonv.updatecmpnttypeprop(val[2], ctypeid, ctptid)
            ctypepropid = ctypepropid[0][0]

        if updatemap:
            draw2typedict[val[2]] = [ctypeid, val[0], val[1]]
##    #####################################
##    #  get ref draw to type 
##    #####################################
##    
##    type2drawmapsql = '''
##    select cmpnt_type.cmpnt_type_id, cmpnt_type_name, cmpnt_type_prop_value 
##    from 
##    cmpnt_type, cmpnt_type_prop, cmpnt_type_prop_type 
##    where 
##    cmpnt_type.cmpnt_type_id = cmpnt_type_prop.cmpnt_type_id 
##    and cmpnt_type_prop.cmpnt_type_prop_type_id = cmpnt_type_prop_type.cmpnt_type_prop_type_id 
##    and cmpnt_type_prop_type_name = "Reference Drawing";
##    '''

def savecmpnttype():
    '''
    '''
    ctpt_id = municonv.retrievecmpnttypeproptype(cmpnttypeproptype, cmpnttypeproptypedesc)
    if len(ctpt_id) == 0:
        ctpt_id = municonv.savecmpnttypeproptype(cmpnttypeproptype, cmpnttypeproptypedesc)
    else:
        ctpt_id = ctpt_id[0][0]

    __savecmpnttype(ctpt_id, dipoletype2draw)
    __savecmpnttype(ctpt_id, quadtype2draw)
    __savecmpnttype(ctpt_id, sexttype2draw)
    __savecmpnttype(ctpt_id, cortype2draw)
    __savecmpnttype(ctpt_id, hcortype2draw, updatemap=False)
    __savecmpnttype(ctpt_id, vcortype2draw, updatemap=False)

def saveinstall(dfile):
    '''
    '''
    ctypelist = ['Quad A', 'Quad B', 'Quad C', 'Quad Cp', 'Quad D', 'Quad D2', 'Quad E', 'Quad E2', 'Quad F',
                 'Sext A', 'Sext B', 'Sext C', 'Corr A', 'Corr C', 'Corr D', 'Corr Fast']
    #ctypelist = ['Quad A', 'Quad B', 'Quad C', 'Quad Cp', 'Quad D', 'Quad D2', 'Quad E', 'Quad E2', 'Quad F',
    #             'Sext A', 'Sext B', 'Sext C', 'Corr D']
    # Corr D is a skew Quad
    #corrlist=['Corr A', 'Corr C']
    #fastcor=['Corr Fast']
    section = "Storage Ring"
    installeddev = __readdata(dfile)
    for data in installeddev[1:]:
        if data[7] != '' and data[4] in ctypelist:
            # link with install with inventory since serial # is available
            field_name = str(data[3])
            ctype = data[4]
            #refdraw = data[5]
            #desc = data[6]
            
            # special case: change the SN    from    |       to
            #              Provided by: Animesh Jain |   Chenghao Yu
            # SR-MG-QDW-9810-SN             0002     |      1002
            # SR-MG-QDW-9810-SN             0003     |      1003
            # SR-MG-QDW-9813-SN             0002     |      1002
            # SR-MG-QDW-9813-SN             0003     |      1003
            # SR-MG-QDW-9813-SN             0004     |      1004
            #
            # SR-MG-QDP-9810 == Quad D2
            # SR-MG-QDW-9813 == Quad E2
            serial = int(data[7])
#            print(ctype, serial)
#            if ctype in ["Quad D2", 'Quad E2'] and serial != 1:
#                serial += 1000
            #alias = data[8]
            invid = None
            invdata = municonv.retrieveinventory(str(serial), ctype)
            if len(invdata) == 1:
                invid = invdata[0][1]
            ctypedata = municonv.retrievecmpnttype(ctype)
            
            ctypeid = None
            if len(ctypedata) == 1:
                ctypeid = ctypedata[0][0]
            if ctypeid != None and invid != None:
                res = municonv.retrieveinstall(field_name, ctype, section)
                if len(res) == 0:
                    municonv.saveinstall(field_name, ctypeid, section, invid)
            else:
                raise ValueError("cannot find device [%s: %s] for type (%s) in inventory." %(field_name, serial, ctype))
        elif data[4] in ctypelist or data[4] in ['Dipole', 'Dipole G']:
            # save install only since serial # is not available
            field_name = str(data[3])
            ctype = data[4]
            ctypedata = municonv.retrievecmpnttype(ctype)
            ctypeid = None
            if len(ctypedata) == 1:
                ctypeid = ctypedata[0][0]
            if ctypeid != None:
                res = municonv.retrieveinstall(field_name, ctype, section)
                if len(res) == 0:
                    municonv.saveinstall(field_name, ctypeid, section)
    
def checksn(fname, serial):
    '''Compare the serial number with that in file name.
    If the does not match each other, use the one in file name.
    
    Subject to change if the rule is changed.
    '''
    fserial = int(fname.split("-")[2].split("_")[0])
    if serial != fserial:
        serial = fserial

    return serial

def saverotcoildata(files):
    '''
    '''

    for dfile in files:
        data = __readdata(dfile)
#        if data[0][1].strip() != refdraw:
#            print("%s,%s,%s,%s"%(data[0][1].strip(), data[1][1].strip(), data[2][1].strip(), str(int(data[3][1])).zfill(4)))
#            refdraw = data[0][1].strip()
#        elif data[2][1].strip() != vendor:
#            print("%s,%s,%s,%s"%(data[0][1].strip(), data[1][1].strip(), data[2][1].strip(), str(int(data[3][1])).zfill(4)))
#            vendor = data[2][1].strip()
        vendor = None
        serial = None
        ctype = None
        paramdict = {}
        resdict={}
        if data[3][0] == 'Serial Number' and data[3][1] != '':
            serial = int(data[3][1])
            paramdict['serialNumber'] = serial
        else:
            print ('No serial number for %s'%(dfile))
        serial = checksn(os.path.split(str(dfile))[1], serial)

        if data[0][0] == 'Magnet Type' and data[0][1] != '':
            ctype = data[0][1].strip()
            paramdict['referenceDraw'] = data[0][1].strip()
            ctype = draw2typedict[ctype[6:]]
            
            # special case: change the SN    from    |       to
            #              Provided by: Animesh Jain |   Chenghao Yu
            # SR-MG-QDW-9810-SN             0002     |      1002
            # SR-MG-QDW-9810-SN             0003     |      1003
            # SR-MG-QDW-9813-SN             0002     |      1002
            # SR-MG-QDW-9813-SN             0003     |      1003
            # SR-MG-QDW-9813-SN             0004     |      1004
            if data[0][1].strip() in ['SR-MG-QDP-9810', "SR-MG-QDW-9813"] and serial != 1:
                serial += 1000
        else:
            print ('No no reference drawing for %s'%(dfile))
        
        if data[1][0] == 'Alias' and data[1][1] != '':
            paramdict['aliasName'] = data[1][1].strip()
        else:
            print ('No alias for %s'%(dfile))
        if data[2][0] == 'Vendor ID' and data[2][1] != '':
            vendor = data[2][1].strip()
            paramdict['vendor'] = vendor
        else:
            print ('No vendor for %s'%(dfile))
#        if data[4][0] == 'Measureing_Coil_ID' and data[4][1] != '':
#            paramdict['coil_id'] = data[4][1]
#        else:
#            print ('No coil id for %s'%(dfile))
        if data[5][0] == 'Reference_Radius' and data[5][1] != '':
            # convert reference radius from mm to meter
            paramdict['referenceRadius'] = data[5][1]/1000.00
        else:
            print ('No reference radius for %s'%(dfile))        
        if data[8][0] == 'Conditioning Current' and data[8][1] != '':
            paramdict['conditionCurrent'] = data[8][1]
        
        ctypeid = ctype[0]
        ctypename = ctype[1]
        ctypedesc = ctype[2]
        
        res = municonv.retrievecmpnttype(ctypename, desc=ctypedesc, vendor=vendor)
        if len(res) == 0:
            res = municonv.savecmpnttype(ctypename, ctypedesc, vendor=vendor)
            #vendorid = res[1]
        else:
            res = res[0]
            #vendorid = res[4]
        if ctypeid != res[0]:
            raise ValueError ("component type id in IRMIS (%s) does not match that on the file (%s)."%(res[0], ctypeid))

        ####################################
        # save inventory property template
        # the key name for unit conversion is:
        #    "municonv"
        ####################################
        invproptmplt = municonv.retrieveinventoryproptmplt(proptmplt, ctypeid, desc=proptmpltdesc)
        if len(invproptmplt):
            invproptmpltid = invproptmplt[0][0]
        else:
            invproptmpltid = municonv.saveinventoryproptmplt(proptmplt, ctypeid, desc=proptmpltdesc)
        
        run1 = []
        run2 = []
        run3 = []
        cur1 = []
        cur2=[]
        cur3=[]
        bref1=[]
        bref2=[]
        bref3=[]
        direction1 = []
        direction2 = []
        direction3 = []
        transf1 = []
        transf2 = []
        transf3 = []
        dev1 = []
        dev2 = []
        dev3 = []
        for field in data[11:]:
            if str(field[3]).strip() == '' and str(field[4]).strip() == '' and str(field[5]).strip() == '':
                break
            elif str(field[6]).strip() != '':
                run1.append(field[1])
                cur1.append(field[3])
                direction1.append(field[6])
                bref1.append(field[13])
                transf1.append(field[10])
                dev1.append(field[2])
            elif str(field[7]).strip() != '':
                run2.append(field[1])
                cur2.append(field[4])
                direction2.append(field[7])
                bref2.append(field[13])
                transf2.append(field[10])
                dev2.append(field[2])
            elif str(field[8]).strip() != '':
                run3.append(field[1])
                cur3.append(field[5])
                direction3.append(field[8])
                bref3.append(field[13])
                transf3.append(field[10])
                dev3.append(field[2])
        
        defaultEnergy = 3.0
        if len(cur2) != 0 or len(cur3) != 0:
            if len(cur1) != 0:
                measurementDatadict = {'runNumber': run1,
                                    'current': cur1,
                                    'currentUnit': 'A',
                                    'direction': direction1,
                                    'field': bref1,
                                    'fieldUnit': 'T-m',
                                    'integralTransferFunction': transf1,
                                    'description': dev1,
                                    }
                measurementDatadict.update(paramdict)
                conversionsdict = {'i2b': {'algorithmId': 2,
                                           'auxInfo': 1,
                                           'function': 'polynomial',
                                           'initialUnit': 'A',
                                           'resultUnit': 'T-m'},
                                   'b2k': {}}
                resdict['complex:1'] = {'measurementData': measurementDatadict,
                                         'algorithms': conversionsdict,
                                         'description': 'Horizontal corrector component',
                                         'defaultEnergy': defaultEnergy}
            if len(cur2) != 0:
                measurementDatadict = {'runNumber': run2,
                                    'current': cur2,
                                    'currentUnit': 'A',
                                    'direction': direction2,
                                    'field': bref2,
                                    'fieldUnit': 'T-m',
                                    'integralTransferFunction': transf2,
                                    'description': dev2,
                                    }
                conversionsdict = {'i2b': {'algorithmId': 2,
                                           'auxInfo': 1,
                                           'function': 'polynomial',
                                           'initialUnit': 'A',
                                           'resultUnit': 'T-m'},
                                   'b2k': {}}
                measurementDatadict.update(paramdict)
                resdict['complex:2'] = {'measurementData': measurementDatadict,
                                        'algorithms': conversionsdict,
                                        'description': 'Vertical corrector component',
                                        'defaultEnergy': defaultEnergy}
            if len(cur3) != 0:
                measurementDatadict = {'runNumber': run3,
                                    'current': cur3,
                                    'currentUnit': 'A',
                                    'direction': direction3,
                                    'field': bref3,
                                    'fieldUnit': 'T-m',
                                    'integralTransferFunction': transf3,
                                    'description': dev3,
                                    }
                conversionsdict = {'i2b': {'algorithmId': 2,
                                           'auxInfo': 1,
                                           'function': 'polynomial',
                                           'initialUnit': 'A',
                                           'resultUnit': 'T-m'},
                                   'b2k': {}}
                measurementDatadict.update(paramdict)
                resdict['complex:3'] = {'measurementData': measurementDatadict,
                                        'algorithms': conversionsdict,
                                        'description': 'Skew quadrupole component',
                                        'defaultEnergy': defaultEnergy}
        
        else:
            measurementDatadict = {'runNumber': run1,
                                'current': cur1,
                                'currentUnit': 'A',
                                'direction': direction1,
                                'field': bref1,
                                'fieldUnit': 'T-m',
                                'integralTransferFunction': transf1,
                                'description': dev1}
            conversionsdict = {'i2b': {'algorithmId': 3,
                                       'auxInfo': 0,
                                       'function': 'interpolating',
                                       'initialUnit': 'A',
                                       'resultUnit': 'T-m'},
                              }

            if ctypename in ['Quad A', 'Quad B', 'Quad C', 'Quad Cp', 'Quad D', 'Quad D2', 'Quad E', 'Quad E2', 'Quad F']:
                try:
                    conversionsdict['b2k'] = {'algorithmId': 0,
                                              'auxInfo': 2,
                                              'function': "input/(%s*3.33567*energy)"%(paramdict['referenceRadius']),
                                              'initialUnit': 'T-m',
                                              'resultUnit': '1/m2'}
                except:
                    # do not add function for b2k since reference radius is not available.
                    pass
                description = "pure quadrupole component"
            elif ctypename in ['Sext A', 'Sext B', 'Sext C']:
                try:
                    conversionsdict['b2k'] = {'algorithmId': 0,
                                              'auxInfo': 3,
                                              'function': "2*input/(%s**2*3.33567*energy)"%(paramdict['referenceRadius']),
                                              'initialUnit': 'T-m',
                                              'resultUnit': '1/m3'}
                except:
                    # do not add function for b2k since reference radius is not available.
                    pass
                description = "pure sextupole component"
            measurementDatadict.update(paramdict)
            resdict['standard'] = {'measurementData': measurementDatadict,
                                   'algorithms': conversionsdict,
                                   'description': description,
                                   'defaultEnergy': defaultEnergy}

        jsondump = json.dumps(resdict)

        if ctypename == 'Corr A':
            # 156 mm corrector; has only one measurement data set
            # use serial # 3
            for sn  in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38,
                        39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
                        57, 58, 59, 60]:
                res = municonv.retrieveinventory(str(sn), ctypename, vendor)
                if len(res) == 0:
                    invid = municonv.saveinventory(str(sn), ctypename, vendor)
                else:
                    invid = res[0][1]
                try:
                    municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
                except:
                    municonv.updateinventoryprop(jsondump, invid, invproptmpltid)
        elif ctypename == 'Corr C':
            if serial == 13:
                # available candidate: 1, 13
                # use serial # 13
                for sn in [8, 13, 15, 16, 18, 26, 37, 58, 62, 70, 71, 75, 78, 90]:
                    res = municonv.retrieveinventory(str(sn), ctypename, vendor)
                    if len(res) == 0:
                        invid = municonv.saveinventory(str(sn), ctypename, vendor)
                    else:
                        invid = res[0][1]
                    try:
                        municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
                    except:
                        municonv.updateinventoryprop(jsondump, invid, invproptmpltid)
            elif serial == 31:
                # available candidate: 2, 3, 6, 12, 31
                #use serial # 31
                for sn in [10, 14, 20, 21, 22, 25, 29, 31, 32, 34, 41, 43, 44, 50, 
                           56, 57, 61, 64, 66, 68, 73, 77, 88, 91, 93, 98]:
                    res = municonv.retrieveinventory(str(sn), ctypename, vendor)
                    if len(res) == 0:
                        invid = municonv.saveinventory(str(sn), ctypename, vendor)
                    else:
                        invid = res[0][1]
                    try:
                        municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
                    except:
                        municonv.updateinventoryprop(jsondump, invid, invproptmpltid)
            elif serial == 4:
                # available candidate: 4
                #use serial # 4
                for sn in  [4, 5, 7, 11, 17, 19, 23, 24, 28, 30, 33, 35, 36, 39, 40, 48, 
                            53, 54, 55, 59, 60, 69, 76, 89, 92, 94, 95, 99, 100, 102]:
                    res = municonv.retrieveinventory(str(sn), ctypename, vendor)
                    if len(res) == 0:
                        invid = municonv.saveinventory(str(sn), ctypename, vendor)
                    else:
                        invid = res[0][1]
                    try:
                        municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
                    except:
                        municonv.updateinventoryprop(jsondump, invid, invproptmpltid)
            elif serial == 9:
                # available candidate: 
                #use serial # 9
                for sn in  [9, 27, 42, 45, 46, 49, 51, 52, 63, 65, 67, 72, 74, 96, 97, 101]:
                    res = municonv.retrieveinventory(str(sn), ctypename, vendor)
                    if len(res) == 0:
                        invid = municonv.saveinventory(str(sn), ctypename, vendor)
                    else:
                        invid = res[0][1]
                    try:
                        municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
                    except:
                        municonv.updateinventoryprop(jsondump, invid, invproptmpltid)
            else:
                res = municonv.retrieveinventory(str(serial), ctypename, vendor)
                if len(res) == 0:
                    invid = municonv.saveinventory(str(serial), ctypename, vendor)
                else:
                    invid = res[0][1]
                try:
                    municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
                except:
                    municonv.updateinventoryprop(jsondump, invid, invproptmpltid)
        else:
            res = municonv.retrieveinventory(str(serial), ctypename, vendor)
            if len(res) == 0:
                invid = municonv.saveinventory(str(serial), ctypename, vendor)
            else:
                invid = res[0][1]
            try:
                municonv.saveinventoryprop(jsondump, invid, invproptmpltid)
            except:
                municonv.updateinventoryprop(jsondump, invid, invproptmpltid)

def savehallprobedata(files):
    '''
    '''

def linkinventoryinstall():
    '''
    '''

def main(root):
    rotcoils = []
    hallmaps = []
    for f in filecrawler(root):
        if "LBT" not in f and "BST" not in f:
            ext = os.path.splitext(f)[-1].lower()
        
            # Now we can simply use == to check for equality, no need for wildcards.
            if ext in ['.xls', '.xlsx']:
                if 'RotatingCoil' in f:
                    rotcoils.append(f)
                elif 'Hall_Maps' in f:
                    hallmaps.append(f)

    #####################################
    # save storage magnet component types 
    # and the reference drawings
    #####################################
    savecmpnttype()
    
    #####################################
    # save data into inventory
    #####################################
    # save magnet data measured with rotating coil method
    saverotcoildata(rotcoils)
#    # save magnet data measured with hall probe method
    savehallprobedata(hallmaps)

    saveinstall("/".join((root, 'Alignment/SR-MG-INSTALL-SN-09-19.xls')))

if __name__ == '__main__':
    municonv = municonvdata()
    municonv.connectdb(host=host, user=user, pwd=pw, db=db)

    if len(sys.argv) > 1:
        rootpath = sys.argv[1]
    else:
        if sys.version_info[:2] > (3,0):
            rootpath = input ('Please specify the path to the data file directory:')
        else:
            rootpath = raw_input('Please specify the path to the data file directory:')
    main(rootpath)
    print('Finish saving magnet measurement data.')

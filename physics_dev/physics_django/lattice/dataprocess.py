'''
Created on May 9, 2013

@author: shengb
'''
from django.db import connection, transaction
try:
    from django.utils import simplejson as json
except ImportError:
    import json

import datetime

from pylattice.lattice import (lattice)
from pylattice.model import (model)

from pylattice import (runtracy, runelegant)

from utils.utils import _checkkeys

latinst = lattice(connection, transaction=transaction)
modelinst = model(connection, transaction=transaction)

def retrievelatticetype(params):
    '''
    The params is a dictionary with format: {'name': , 'format': }
    the name is supported lattice type name, and format is type format such as 'lat', 'ele', and/or 'txt'.
    '''
    _checkkeys(params.keys(), ['function','name', 'format'])
    
    names = params['name']
    if names == '':
        names = '*'
    formats = params['format']
    if formats == '':
        formats = '*'
    
    if not isinstance(names, list) and not isinstance(formats, list):  
        results = latinst.retrievelatticetype(names, formats)
        resdict = {}
        for res in results:
            resdict[res[0]] = {'name': res[1], 'format': res[2]}
        return resdict
    else:
        raise ValueError('No multiple searches for either name or format are implemented yet.')

def savelatticetype(params):
    '''
    The params is a dictionary with format: {'name': , 'format': }
    the name is supported lattice type name, and format is type format such as 'lat', 'ele', and/or 'txt'.
    '''
    _checkkeys(params.keys(), ['function','name', 'format'])
    if params['name'] == '':
        raise ValueError('lattice type name is empty.')

    try:
        result = latinst.savelatticetype(params['name'], params['format'])
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    
    return {'result': result}

def savelatticeinfo(params):
    '''
    parameters:
        name:        lattice name
        version:     version number
        branch:      branch name
        latticetype: a dictionary which consists of {'name': , 'format': }
                     it is a predefined structure: [{'name': 'plain', 'format': 'txt'},
                                                    {'name': 'tracy3',  'format': 'lat'},
                                                    {'name': 'tracy4',  'format': 'lat'},
                                                    {'name': 'elegant', 'format': 'lte'}]
        
        description: description for this lattice, allow user put any info here (< 255 characters)
        creator:     original creator
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'latticetype', 'description', 'creator'])

    name = params['name']
    if name == '':
        name = '*'
    version = params['version']
    if version == '':
        version = '*'
    branch=params['branch']
    if branch == '':
        branch = '*'
    latticetype=None
    if params.has_key('latticetype') and params['latticetype'] != '':
        latticetype = params['latticetype']
        latticetype = json.loads(latticetype)
        if not isinstance(latticetype, dict):
            raise TypeError("Lattice type data parameter format error.")
    description = None
    if params.has_key('description') and params['description'] != '':
        description = params['description']
    creator = None
    if params.has_key('creator') and params['creator'] != '':
        creator = params['creator']

    try:
        result = latinst.savelatticeinfo(name, version, branch, latticetype=latticetype, description=description, creator=creator)
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    
    return {"id": result}

def retrievelatticeinfo(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'description', 'creator'])

    name=params['name']
    if name == '':
        name = '*'
    if params.has_key('version') and params['version'] != '':
        version = params['version']
    else:
        version = None        
    if params.has_key('branch') and params['branch'] != '':
        branch = params['branch']
    else:
        branch = None

    if params.has_key('creator') and params['creator'] != '':
        creator = params['creator']
    else:
        creator=None
        
    if params.has_key('description') and params['description'] != '':
        description = params['description']
    else:
        description=None
        
    lattices = latinst.retrievelatticeinfo(name, version=version, branch=branch, description=description, creator=creator)
#    urls, lattices = latinst.retrievelatticeinfo(name, version=version, branch=branch, description=description, creator=creator)
#    for k, v in lattices.iteritems():
#        if urls[k] != None:
#            v['url'] = urls[k]
#            lattices[k] = v
    return lattices
    
def updatelatticeinfo(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'latticetype', 'description', 'creator'])

    name = params['name']
    version = params['version']
    branch=params['branch']
    latticetype=None
    if params.has_key('latticetype'):
        latticetype = params['latticetype']
        latticetype = json.loads(latticetype)
        if not isinstance(latticetype, dict):
            raise TypeError("Lattice type data parameter format error.")
    description = None
    if params.has_key('description'):
        description = params['description']
    creator = None
    if params.has_key('creator'):
        creator = params['creator']
    
    try:
        result = latinst.updatelatticeinfo(name, version, branch, latticetype=latticetype, description=description, creator=creator)
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    
    return {"result": result}
    
def savelattice(params):
    '''
    Save lattice data.
    parameters:
        name:        lattice name
        version:     version number
        branch:      branch name
        latticetype: a dictionary which consists of {'name': , 'format': }
                     it is a predefined structure: [{'name': 'plain', 'format': 'txt'},
                                                    {'name': 'tracy3',  'format': 'lat'},
                                                    {'name': 'tracy4',  'format': 'lat'},
                                                    {'name': 'elegant', 'format': 'lte'},
                                                    {'name': 'xal',     'format': 'xdxf'}]
        
        description: description for this lattice, allow user put any info here (< 255 characters)
        creator:     original creator
        lattice:     lattice data, a dictionary:
                     {'name': ,
                      'data': ,
                      'raw': ,
                      'map': {'name': 'value'},
                      'alignment': ,
                      'control': {'name': ,
                                  'data': }, # control info for a simulation run, ele file for elegant for example
                      'init_twiss':, # initial twiss condition
                     }
                     name: file name to be saved into disk, it is same with lattice name by default
                     data: lattice geometric and strength with predefined format
                     raw:  raw data that is same with data but in original lattice format
                     map:  name-value pair dictionary
                     alignment: mis-alignment information
        dosimulation: Flag to identify whether to perform a simulation. False by default.
        
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'latticetype', 'description', 'creator', 'lattice', 'dosimulation'])

    name=params['name']
    version=params['version']
    branch=params['branch']
    if params.has_key('latticetype'):
        latticetype = params['latticetype']
        latticetype = json.loads(latticetype)
        if not isinstance(latticetype, dict):
            raise TypeError("Lattice type data parameter format error.")
    else:
        latticetype=None
    if params.has_key('creator'):
        creator = params['creator']
    else:
        creator = None
        
    if params.has_key('description'):
        description = params['description']
    else:
        description = None
    if params.has_key('lattice'):
        latticedata = params['lattice']
        latticedata = json.loads(latticedata)
        if not isinstance(latticedata, dict):
            raise TypeError("Lattice type data parameter format error.")
    else:
        latticedata = None
    
    # check whether do simulation here or not.
    modeldata=None
    if params.has_key('dosimulation') and latticetype != None and latticedata!=None:
        if latticedata.has_key('data') and latticedata['data'] != None:
            flattenlat=False
        else:
            flattenlat=True
        if latticetype['name'].lower() in ['tracy3', 'tracy4']:
            flattenlatdict, modeldata = runtracy(latticedata, tracy=latticetype['name'].lower(), flattenlat=flattenlat)
            if flattenlat:
                latticedata['data'] = flattenlatdict
        elif latticetype['name'].lower() in ['elegant']:
            flattenlatdict, modeldata = runelegant(latticedata, flattenlat=flattenlat)

            if flattenlat:
                latticedata['data'] = flattenlatdict
    
    # save lattice
    try:
        result = latinst.savelattice(name, version, branch, creator=creator, description=description, 
                                     latticetype=latticetype, lattice=latticedata)
        
        # save simulation result if there is one
        if modeldata:
            modeldata['description'] = 'automatic simulation result performed by server on %s'%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %p"))
            modelname = 'default model for %s (branch %s, version %s)'%(name, branch, version)
            modeldata['creator'] = 'lattice/model service'
            modelinst.savemodel({modelname:modeldata}, name, version, branch)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise

    return {'id': result}

def updatelattice(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'latticetype', 'description', 'creator', 'lattice', 'dosimulation'])

    name=params['name']
    version=params['version']
    branch=params['branch']
    if params.has_key('latticetype'):
        latticetype = params['latticetype']
        latticetype = json.loads(latticetype)
        if not isinstance(latticetype, dict):
            raise TypeError("Lattice type data parameter format error.")
    else:
        latticetype=None
    if params.has_key('creator'):
        creator = params['creator']
    else:
        creator = None
        
    if params.has_key('description'):
        description = params['description']
    else:
        description = None
    if params.has_key('lattice'):
        latticedata = params['lattice']
        latticedata = json.loads(latticedata)
        if not isinstance(latticedata, dict):
            raise TypeError("Lattice type data parameter format error.")
    else:
        latticedata = None
    
    latticeids = latinst.retrievelattice(name, version, branch)
    if len(latticeids) != 1:
        raise RuntimeError("More than one lattice found when updating lattice for %s (branch %s, version %s)"
                           %(name, branch, version))
    else:
        latticeid = latticeids.keys()[0]
    
    # check whether element has been there
    # do not do simulation 
    res = latinst._checkelementbylatticeid(connection.cursor(), latticeid)
    modelname = 'default model for %s (branch %s, version %s)'%(name, branch, version)
    modelres = modelinst.retrievemodel(modelname=modelname)
    
    modeldata=None
    if len(modelres) == 0:
        # check whether do simulation here or not.
        if params.has_key('dosimulation') and latticetype != None and latticedata!=None:
            if latticedata.has_key('data') and latticedata['data'] !=None:
                flattenlat=False
            else:
                flattenlat=True
            if latticetype['name'].lower() in ['tracy3', 'tracy4']:
                flattenlatdict, modeldata = runtracy(latticedata, tracy=latticetype['name'].lower(), flattenlat=flattenlat)
                if flattenlat and res[0] == 0:
                    latticedata['data'] = flattenlatdict
            elif latticetype['name'].lower() in ['elegant']:
                flattenlatdict, modeldata = runelegant(latticedata, flattenlat=flattenlat)
                if flattenlat:
                    latticedata['data'] = flattenlatdict

    # update lattice
    try:
        result = latinst.updatelattice(name, version, branch, creator=creator, description=description, 
                                       latticetype=latticetype, lattice=latticedata)
        
        # save simulation result if there is one
        if modeldata:
            modeldata['description'] = 'automatic simulation result performed by server on %s'%(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %p"))
            modeldata['creator'] = 'lattice/model service'
            modelinst.savemodel({modelname:modeldata}, name, version, branch)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise

    return {'result': result}
    
def retrievelattice(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'latticetype', 'description', 'creator', 'withdata', 'rawdata'])

    name = params['name']
    version = params['version']
    branch=params['branch']
    if params.has_key('description'):
        description = params['description']
    else:
        description = None
    if params.has_key('creator'):
        creator = params['creator']
    else:
        creator = None
    
    if params.has_key('latticetype'):
        latticetype = params['latticetype']
        latticetype = json.loads(latticetype)
        if not isinstance(latticetype, dict):
            raise TypeError("Lattice type data parameter format error.")
    else:
        latticetype = None  
    if params.has_key('withdata'):
        withdata = bool(json.loads(params['withdata'].lower()))
    else:
        withdata = False  
    if params.has_key('rawdata'):
        rawdata = bool(json.loads(params['rawdata'].lower()))
    else:
        rawdata = False  
    
    result = latinst.retrievelattice(name, version, branch, description=description, creator=creator,
                                     latticetype=latticetype, withdata=withdata, rawdata=rawdata)
    
    return result

def savelatticestatus(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'status', 'creator'])

    name = params['name']
    version = params['version']
    branch=params['branch']
    status=params['status']
    creator=params['creator']
    
    try:
        result=latinst.savelatticestatus(name, version, branch, status=status, creator=creator)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    
    return {'result':result}
    
def retrievelatticestatus(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'version', 'branch', 'status', 'creator', 'description'])

    name = params['name']
    version = params['version']
    branch=params['branch']
    if params.has_key('status'):
        status=params['status']
        ignorestatus=False
    else:
        status='*'
        ignorestatus=True
    
    result=latinst.retrievelatticestatus(name, version, branch, status=status, ignorestatus=ignorestatus)
    latticestatus={}
    for res in result:
        tmpdict = {'name':   res[1],
                   'version':res[2],
                   'branch': res[3],
                   'status': res[8]}
        if res[4] != None:
            tmpdict['creator'] =      res[4],
        if res[5] != None:
            tmpdict['originalDate'] = res[5].isoformat(),
        if res[6] != None:
            tmpdict['updated'] =      res[6],
        if res[7] != None:
            tmpdict['lastModified'] = res[7].isoformat(),
        latticestatus[res[9]] = tmpdict
    return latticestatus
    
def savemodelcodeinfo(params):
    ''''''
    _checkkeys(params.keys(), ['function','name', 'algorithm'])

    if params.has_key('name'):
        name = params['name']
    else:
        name=None
    if params.has_key('algorithm'):
        algorithm = params['algorithm']
    else:
        algorithm=None
    if name==None and algorithm==None:
        raise ValueError("No sufficient information provided to retrieve a simulation info (simulation result and algorithm)")

    try:
        result = modelinst.savemodelcodeinfo(name, algorithm)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise

    return {'result': result}
    
def retrievemodelcodeinfo(params):
    '''
    '''
    _checkkeys(params.keys(), ['function','name', 'algorithm'])

    if params.has_key('name'):
        name = params['name']
    else:
        name=None
    if params.has_key('algorithm'):
        algorithm = params['algorithm']
    else:
        algorithm=None
    if name==None and algorithm==None:
        raise ValueError("No sufficient information provided to retrieve a simulation info (simulation result and algorithm)")
    
    result = modelinst.retrievemodelcodeinfo(name, algorithm)
    resdict = {}
    for res in result:
        resdict[res[0]] = {'name': res[1], 'algorithm': res[2]}
    
    return resdict

def savemodelstatus(params):
    ''''''
    _checkkeys(params.keys(), ['function','name', 'status', 'creator'])

    name = params['name']
    status = params['status']
    creator = params['creator']
    
    try:
        result=modelinst.savegoldenmodel(name, status=status, creator=creator)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    
    return {'result':result}
    
def retrievemodelstatus(params):
    ''''''
    _checkkeys(params.keys(), ['function','name', 'status'])

    name = params['name']
    if params.has_key('status'):
        status=params['status']
        ignorestatus=False
    else:
        status='*'
        ignorestatus=True

    results=modelinst.retrievegoldenmodel(name, status=status, ignorestatus=ignorestatus)
    result = {}
    for res in results:
        result[res[7]] = {'name': res[1],
                          'status': res[6],
                          'id': res[7]
                          }
        if res[2] !=None:
            result[res[7]]['creator'] = res[2]
        if res[3] != None:
            result[res[7]]['originalDate'] = res[3].isoformat()
        if res[4] !=None:
            result[res[7]]['updated'] = res[4]
        if res[5] != None:
            result[res[7]]['lastModified'] = res[5].isoformat()

    #return {'result': result}
    return result

def savemodel(params, defaultuser=None):
    '''
    Save a model.
    parameters:
        latticeid:      internal id of lattice this model belongs to
        latticename:    lattice name that this model belongs to
        latticeversion: the version of lattice
        latticebranch:  the branch of lattice
        
        model:          a dictionary which holds all data 
            {'model name':                            # model name
                           { # header information
                            'description': ,          # description of this model
                            'creator': ,              # name who create this model first time
                            'updated': ,              # name who modified last time
                            'tunex': ,                # horizontal tune
                            'tuney': ,                # vertical tune
                            'chromX0': ,             # linear horizontal chromaticity
                            'chromX1': ,             # non-linear horizontal chromaticity
                            'chromX2': ,             # high order non-linear horizontal chromaticity
                            'chromY0': ,             # linear vertical chromaticity
                            'chromY1': ,             # non-linear vertical chromaticity
                            'chromY2': ,             # high order non-linear vertical chromaticity
                            'finalEnergy': ,          # the final beam energy in GeV
                            'simulationCode': ,       # name of simulation code, Elegant and Tracy for example
                            'sumulationAlgorithm': ,  # algorithm used by simulation code, for example serial or parallel,
                                                      # and SI, or SI/PTC for Tracy code
                            'simulationControl': ,    # various control constrains such as initial condition, beam distribution, 
                                                      # and output controls
                            'simulationControlFile':  # file name that control the simulation conditions, like a .ele file for elegant
                            
                            # simulation data
                            'beamParameter':          # a dictionary consists of twiss, close orbit, transfer matrix and others
                           }
             ...
            }
    
    '''
    _checkkeys(params.keys(), ['function','latticeid', 'latticename', 'latticeversion', 'latticebranch','modelname', 'model'])

    if params.has_key('latticeid'):
        # ignore lattice name, version, and branch information
        latticeid=params['latticeid']
        latticename = None
        latticeversion = None
        latticebranch = None
    else:
        # no lattice provided. Have to use lattice name, version, and branch.
        latticeid=None
        latticename = params['latticename']
        latticeversion = params['latticeversion']
        latticebranch = params['latticebranch']
    
    if latticeid==None and (latticename==None or latticeversion==None or latticebranch==None):
        raise ValueError("Cannot identify lattice that this model belongs to")
    
    if not params.has_key('model') or params['model'] == None:
        raise ValueError ("Cannot find model information")
    
    models = params['model']
    models = json.loads(models)
    if not isinstance(models, dict):
        raise TypeError("Model data parameter format error.")

    if latticeid != None:
        nbv = latinst._retrievelatticeinfobyid(latticeid)
        if len(nbv) == 0:
            raise ValueError('Cannot find lattice with id=%s'%lattice)
        latticename = nbv[0]
        latticeversion = nbv[1]
        latticebranch = nbv[2]
    
    try:
        result = modelinst.savemodel(models, latticename, latticeversion, latticebranch, defaultuser=defaultuser)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    return {'result': result}
    
def updatemodel(params):
    ''''''
    _checkkeys(params.keys(), ['function','latticeid', 'latticename', 'latticeversion', 'latticebranch', 'modelname', 'model'])

    if params.has_key('latticeid'):
        # ignore lattice name, version, and branch information
        latticeid=params['latticeid']
        latticename = None
        latticeversion = None
        latticebranch = None
    else:
        # no lattice provided. Have to use lattice name, version, and branch.
        latticeid=None
        latticename = params['latticename']
        latticeversion = params['latticeversion']
        latticebranch = params['latticebranch']
    
    if latticeid==None and (latticename==None or latticeversion==None or latticebranch==None):
        raise ValueError("Cannot identify lattice that this model belongs to")
    
    if not params.has_key('model') or params['model'] == None:
        raise ValueError ("Cannot find model information")
    
    models = params['model']
    models = json.loads(models)
    if not isinstance(models, dict):
        raise TypeError("Model data parameter format error.")

    if latticeid != None:
        nbv = latinst._retrievelatticeinfobyid(latticeid)
        if len(nbv) == 0:
            raise ValueError('Cannot find lattice with id=%s'%lattice)
        latticename = nbv[0]
        latticeversion = nbv[1]
        latticebranch = nbv[2]
    
    try:
        result = modelinst.updatemodel(models, latticename, latticeversion, latticebranch)
        
        transaction.commit_unless_managed()
    except:
        transaction.rollback_unless_managed()
        raise
    return {'result': result}

def retrievemodel(params):
    '''
    Retrieve a model list that satisfies given constrains.
    parameters:
        name:    the name shows that which model this API will deal with
        id:      the id shows that which model this API will deal with
        
    return: a dictionary
            {'model name':                            # model name
                           {'id': ,                   # model id number
                            'latticeId': ,            # id of the lattice which given model belongs to
                            'description': ,          # description of this model
                            'creator': ,              # name who create this model first time
                            'originalDate': ,         # date when this model was created
                            'updated': ,              # name who modified last time
                            'lastModified': ,         # the date this model was modified last time
                            'tunex': ,                # horizontal tune
                            'tuney': ,                # vertical tune
                            'chromX0': ,             # linear horizontal chromaticity
                            'chromX1': ,             # non-linear horizontal chromaticity
                            'chromX2': ,             # high order non-linear horizontal chromaticity
                            'chromY0': ,             # linear vertical chromaticity
                            'chromY1': ,             # non-linear vertical chromaticity
                            'chromY2': ,             # high order non-linear vertical chromaticity
                            'finalEnergy': ,          # the final beam energy in GeV
                            'simulationCode': ,       # name of simulation code, Elegant and Tracy for example
                            'sumulationAlgorithm': ,  # algorithm used by simulation code, for example serial or parallel,
                                                      # and SI, or SI/PTC for Tracy code
                            'simulationControl': ,    # various control constrains such as initial condition, beam distribution, 
                                                      # and output controls
                            'simulationControlFile':  # file name that control the simulation conditions, like a .ele file for elegant
                           }
             ...
            }
    '''
    _checkkeys(params.keys(), ['function','name', 'id'])

    if params.has_key('name'):
        name = params['name']
    else:
        name=None
    if  params['name'] == '':
        name = '*'
    if params.has_key('id') and params['id'] != '':
        mid = params['id']
    else:
        mid=None
    
    result = modelinst.retrievemodel(name, mid)
    
    return result

def retrievemodellist(params):
    '''
    Retrieve all models info/list belong to a lattice
    parameters:
        latticename
        latticebranch
        latticeversion
        
    '''
    _checkkeys(params.keys(), ['function', 'latticename', 'latticeversion', 'latticebranch'])
    
    latticename = params['latticename']
    if latticename == '':
        latticename = '*'
    if params.has_key('latticebranch') and params['latticebranch'] != '':
        latticebranch = params['latticebranch']
    else:
        latticebranch=None
        
    if params.has_key('latticeversion') and params['latticeversion']:
        latticeversion = params['latticeversion']
    else:
        latticeversion=None

    result = modelinst.retrievemodellist(latticename, latticebranch=latticebranch, latticeversion=latticeversion)
    return result
    
def retrievetransfermatrix(params):
    '''
    name:  model name
    from:  starting position
    to:    end position
    '''
    _checkkeys(params.keys(), ['function', 'modelname', 'from', 'to'])

    return modelinst.retrievetransfermatrix(params)
    
def retrieveclosedorbit(params):
    '''
    name:  model name
    from:  starting position
    to:    end position
    ''' 
    _checkkeys(params.keys(), ['function', 'modelname', 'from', 'to'])

    return modelinst.retrieveclosedorbit(params)
    
def retrievetwiss(params):
    '''
    name:  model name
    from:  starting position
    to:    end position
    ''' 
    _checkkeys(params.keys(), ['function', 'modelname', 'from', 'to'])

    return modelinst.retrievetwiss(params)
    
def retrievebeamparameters(params):
    '''
    name:  model name
    from:  starting position
    to:    end position
    ''' 
    _checkkeys(params.keys(), ['function', 'modelname', 'from', 'to'])

    return modelinst.retrievebeamparameters(params)

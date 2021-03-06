Lattice/Model Web Service Reference Manual
==========================================

Introduction
--------------
The implementation of the Lattice/Model service that is described in this section is a REST web service within the Django framework.
As shown in Figure 2 in the :ref:`lattice_model_architecture` section, this service consists of 3 layers:
    
    1. The Client layer, which provides an interface to end user of service; 
    2. The Service layer, which 
		
		a. provides an interface to a client, response request from the client and send/receive data overnetwork thru http/REST interface to/from the 			client, and 
		b. interfaces with underneath rdb thru a data api; 
		
    3. The Relational database layer, which stores all data.

The current implementation uses 2 http methods, namely GET and POST. Once the server is running, the Lattice/Model service can be accessed via a URL, for example: ::

    http://localhost:8000/lattice

A JSON encoding/decoding is adopted to transfer data over the network. All data has to be encoded into a JSON string format before sending over the  network. For binary data, a BASE64 algorithm is supported to encode/decode the data to/from a string to enable data transfer with the JSON string. An example of a JSON header is: ::

    {'content-type':'application/json', 'accept':'application/json'}
    

The Client Layer
---------------------
The Client layer provides an interface to the end user in 2 formats: 

	1. an API library, which can be used by a client application, for example a Python script or a Matlab application; 
	2. a graphic user interface (GUI), which can be a graphic interface from a browser, or a CSS (Control System Studio) application.

Work on this implementation is in-progress, and more detailed documentation will follow shortly.

The Service Layer
---------------------
The Service layer responds to requests from the client, sends data back to or receives data from client through a REST/HTTP protocol, and saves data to and retrieves data from the underlying relational database through a data API. An online simulation can be carried out by request with proper configuration and currently it supports 2 simulation codes, tracy3 and elegant. Since the lattice grammar is the only difference between tracy3 and tracy4, support for tracy4 is under development, and can be done incorporated.

Service API
~~~~~~~~~~~~~
The GET and POST methods implemented for lattice and model are described here.

:NOTE: Since all raw data is transported as a JSON string, it is recommended that the data be decoded into a native format, e.g. a dictionary in Python, before it is used, or encoded into a JSON string before transport over the network.

A summary for the service API is listed below: 

==========================   =====================
   **GET**                          **POST**
--------------------------   ---------------------
  retrieveLatticeType          saveLatticeType
--------------------------   ---------------------
  retrieveLatticeInfo          saveLatticeInfo
  
                               updateLatticeInfo
--------------------------   ---------------------
  retrieveLattice              saveLattice
  
                               updateLattice
--------------------------   ---------------------
  retrieveLatticeStatus        saveLatticeStatus
--------------------------   ---------------------
  retrieveModelCodeInfo        saveModelCodeInfo
--------------------------   ---------------------
  retrieveModel                saveModel
  
                               updateModel
--------------------------   ---------------------
  retrieveModelList
--------------------------   ---------------------
  retrieveModelStatus          saveModelStatus
--------------------------   ---------------------
  retrieveTransferMatrix
--------------------------   ---------------------
  retrieveClosedOrbit
--------------------------   ---------------------
  retrieveTwiss
--------------------------   ---------------------
  retrieveBeamParameters
==========================   =====================


For the status of a lattice or model, no update method is provided since the status history is not recorded.
Each status is treated as new except the original information when the entry is first created.

GET Methods
^^^^^^^^^^^^^^^^^^^^^^

A GET method retrieves data from a service, and a GET command can be easily formalized into a URL.
Available commands for a GET operation are:

Rules for wildcard matching:

    - \* for multiple character matching;
    - ? for single character matching.

It raises an **HTTP/404** error if an invalid keyword is given.

    :NOTE: Since the data is saved as it is, and server does not do any manipulation, the client has take note of the data returned from the server and the convention that is used when the data is produced, especially the units of the returned data. For example, elegant uses :math:`\beta*\gamma` as beam energy output while in Tracy, phase advance is defined in the units of 2π, which means there is a factor of 2π difference when comparing with restults from other simulation code like elegant.

GET Methods - Lattice
^^^^^^^^^^^^^^^^^^^^^^

* **retrieveLatticeType**

    Retrieves the lattice type information according to the given lattice type ``name`` and ``format``. The purpose behind having the lattice type with its format is to capture the original lattice information, which will help when retrieving the original lattice, and converting a lattice to another format.
 
    **keywords** for searching: ::
    
        function: retrieveLatticeType
        name:     lattice type name
        format:   lattice type format  

    Both ``name`` and ``format`` are needed to search available lattice type, otherwise, it will return an **HTTP/404** error with a message that says "Parameters are missing for function retrieveLatticeType". Wildcards are supported for ``name`` and ``format``.
    
    :NOTE: The ``name`` with ``format`` is globally unique. A format could be empty/None, but a lattice type name has to be given. No duplicated entry is allowed for a given lattice name with a specific format. 
    
    **Result data structure**: ::
    
        {lattice type id: {
                           'name': , 
                           'format': 
                          }, 
         ...
        }
        or {} if no existing entry.

    A lattice type is site-specific. Typical lattice types could be, but are not limited to: ::   

    {'name': 'plain', 'format': 'txt'}
    {'name': 'tracy3',  'format': 'lat'}
    {'name': 'tracy4',  'format': 'lat'}
    {'name': 'elegant', 'format': 'lte'}


    An example command of a request sent to the server to get all available lattice types: ::
    
    /lattice/?function=retrieveLatticeType&name=*&format=*
    
    A returned result could be: ::
    
        {u'1': {u'format': u'lat', u'name': u'tracy3'},
         u'2': {u'format': u'lte', u'name': u'elegant'}
        }

* **retrieveLatticeInfo**
  
    Retrieves lattice header information. It returns lattice name, description, version, branch, creation information (by whom and when it was first created), and update information (by whom and when it was last modified/updated).

    **keywords** for searching: ::
    
        function:    retrieveLatticeInfo
        name:        lattice name
        version:     [optional] lattice version, which has a numeric format 
        branch:      [optional] lattice branch
        description: [optional] a short description
        creator:     [optional] who first created it
        

    The lattice ``name`` is needed to search available lattices, otherwise, it will return an **HTTP/404** error with a message to say "Parameters are missing for function retrieveLatticeInfo". Wildcards are supported for ``name``, ``branch``, ``description``, and ``creator``.
    
    :NOTE: The ``name`` for ``branch`` at ``version`` is globally unique. 
    
    **Result data structure**: ::
    
                {'id': {                             # identifier of this lattice
                        'lattice name': ,            # name of this lattice
                        'version': ,                 # version of this lattice
                        'branch': ,                  # branch this lattice belongs to
                        'description':  [optional],  # lattice description
                        'creator':      [optional],  # who first created this lattice
                        'originalDate': [optional],  # when this lattice was first created
                        'updated':      [optional],  # who last updated
                        'lastModified': [optional],  # when this lattice was last updated
                        'latticeType':  [optional],  # lattice type name
                        'latticeFormat':[optional],  # lattice type format
                        }
                 ...
                } 

    An example command to send a request to the server to get all available lattice headers: ::
    
    /lattice/?function=retrieveLatticeInfo&name=*&version=*&branch=*
    
    A returned result could be: ::
    
        {'1': {'branch': 'Design',
               'creator': 'NSLS II',
               'description': 'This is a design lattice released on Oct 3rd, 2012',
               'latticeFormat': 'lat',
               'latticeType': 'tracy3',
               'name': 'CD3-Oct3-12-30Cell-addID-par',
               'originalDate': '2013-06-20T13:51:02',
               'version': 20121003},
         '2': {'branch': 'Design',
               'creator': 'NSLS II',
               'description': 'This is a design lattice released on Apr 7th, 2010',
               'latticeFormat': 'lat',
               'latticeType': 'tracy3',
               'name': 'CD3-Apr07-10-30cell-par',
               'originalDate': '2013-06-20T13:51:05',
               'version': 20100407}}


.. _lattice_model_ref_retrieveLattice:
   
* **retrieveLattice**

    Retrieves lattice geometric layout with magnetic strength. It should be possible to generate a proper lattice deck from the retrieved data.
    All information needed to construct a desired lattice deck are provided here.

    **keywords** for searching: ::
    
        function:    retrieveLattice
        name:        lattice name
        version:     lattice version
        branch:      lattice branch
        description: [optional] lattice description
        latticetype: [optional] a name-value pair to identify the lattice type
                        {'name': , 'format': } 
        withdata:    [optional] flag to indicate whether to get real lattice data with header.
                     True  -- get the lattice geometric and strength
                     False -- default value, get lattice header description only.
        rawdata:     [optional] flag to indicate whether raw data should be returned. 
        
    The lattice ``name``, ``version``, and ``branch`` are needed to search available lattices, otherwise, it will return an **HTTP/404** error with a message to say "Parameters are missing for function retrieveLattice". Wildcards are supported for ``name``, ``branch``, ``description``, and ``creator``.
    
    :NOTE: The ``name`` for ``branch`` at ``version`` is globally unique. 

        
    **Result data structure**: ::

            {'id':  # identifier of this lattice
                    {'lattice name':              # lattice name
                     'version': ,                 # version of this lattice
                     'branch': ,                  # branch this lattice belongs to
                     'description':  [optional],  # lattice description
                     'creator':      [optional],  # who first created this lattice 
                     'originalDate': [optional],  # when this lattice was first created
                     'updated':      [optional],  # who last updated this lattice
                     'lastModified': [optional],  # when this lattice was last updated
                     'latticeType':  [optional],  # lattice type name
                     'latticeFormat':[optional],  # lattice type format
                     'lattice':      [optional],  # real lattice data
                     'rawlattice':   [optional],  # raw lattice data the server received
                     'map':          [optional]   # field map. A dictionary with name-value 
                                                  # pairs. Place for kick map for example.
                    } ,
                ...
             }

    Apart from the fields that are returned for **retrieveLatticeInfo**, this function returns up to 3 more fields when ``withdata``, and/or ``rawdata`` is set: **lattice**, **rawlattice**, **map**.

    **lattice**
    
    Returns a flattened lattice when the ``withdata`` keyword is set, which consists of the element geometric layout, type, and magnetic strength settings with associated helper information such as units, if applicable. The flattened lattice has the following structure: ::
    
        {
          'element index':  {'id': ,          # internal element id
                             'name': ,        # element name
                             'length': ,      # element length
                             'position': ,    # s position along beam trajectory
                             'type': ,        # element type
                             'typeprops': [], # collection of property names belonging 
                                              # to this element type in this particular 
                                              # lattice
                             'typeprop':      # value of each property with its unit 
                                              # if it has a different unit to the default
                            },
          ...
          'columns':             []   # full list of all properties for all elements 
                                      # in this particular lattice
          'typeunit': [optional] {},  # unit name-value pair for each type property 
                                      # if applicable
        }
    
    ``typeprop`` is a list like ``[value, unit]``. If the ``unit`` is different from the default, then it will appear here. In most cases, when the unit is the default, it could be omitted, which means ``typeprop`` has the structure ``[value]``.
    
    ``element index`` is the order that each element appears in this lattice. It starts from zero ('0'), which usually belongs to a hidden element, referring to a starting point, and does not appear in a lattice deck, for example "BEGIN" for ``tracy`` and "_BEG_" for ``elegant``. Its value is another map or a dictionary in Python, that its keys, in the original lattice, rely on when it is imported. Some common keys are as shown above: ``id``, ``name``, ``length``, ``position``, ``type`` and ``typeprops``.
    
    An example of a flattened lattice structure is: ::

        {
         '0': {'position':0.0,'length':0.0,'type':'MARK','name':'_BEG_', id':6903},
         '1': {'typeprops':['ON_PASS'], 'name': 'MA1', 'length': 0.0, 'ON_PASS': ['1'], 
               'position':0.0,'type': 'MALIGN','id': 6904},
         '2': {'position':0.0,'length':0.0,'type':'MARK','name':'MK4G1C30A','id':6905},
         '3': {'position':4.65,'length':4.65,'type':'DRIF','name':'DH0G1A','id':6906},
         ...
         '6': {'typeprops':['K2'],'name':'SH1G2C30A','K2':['31.83577810453853'],
               'length':0.2,'position':4.85,'type':'KSEXT','id':6909},
         ...
         '10': {'typeprops':['K1'],'name':'QH1G2C30A','K1':['-0.683259469066921'],
                'length':0.25,'position':5.275,'type':'KQUAD','id':6913},
         ...
         '37': {'typeprops':['ANGLE','E1','E2'],'ANGLE':['0.10472'],'name':'B1G3C30A',
                'type':'CSBEND','length':2.62,'position':10.95,'E1':['0.05236'],
                'id':6940,'E2':['0.05236']},
         ...
         '214': {'typeprops':['INPUT_FILE','N_KICKS','PERIODS','KREF','FIELD_FACTOR'],
                 'name':'DWKM','INPUT_FILE':['"W90v5_pole80mm_finemesh_7m.sdds"'],
                 'N_KICKS':['39'],'length':3.51,'PERIODS':['39'],
                 'KREF':['21.38006225118012'],'position':52.7972,
                 'FIELD_FACTOR':['0.707106781186548'],'type':'UKICKMAP','id':7117},
         ...
         3194': {'typeprops':['VOLT','PHASE','PHASE_REFERENCE','FREQ'],'name':'RF',
                 'VOLT':['2500000'],'length':0.0,'PHASE_REFERENCE':['9223372036854775807'],
                 'position':791.958,'FREQ':['499461995.8990133'],'type':'RFCA','id':10097,
                 'PHASE':['173.523251376']},
         ...
         'columns': ['ON_PASS','K2','K1','ANGLE','E1','E2','INPUT_FILE','N_KICKS','PERIODS',
                     'KREF','FIELD_FACTOR','VOLT','PHASE','PHASE_REFERENCE','FREQ','MODE',
                     'FILENAME'],
        }


    **rawlattice**
    
    Returns the original raw lattice when ``rawlattice`` is set as a name-value pair map, or a dictionary in Python, with the following structure: ::
        
        { 'name': '',
          'data': []
        }
    
    'name' is typically the lattice deck file name, and 'data' is a list which is read-in from a file with each data value on a separate line in the file.
    An original lattice deck could be created from the raw lattice data.
    
    **map**
    
    When either ``rawlattice`` and/or ``withdata`` is set, and the original lattice has an external map file, it is returned as a name-value pair map, or a dictionary in Python, with the following structure: ::
    
        { map_file_name_1: map_file_value_1,
          map_file_name_2: map_file_value_2,
          ...
        }
    
    Typically, the map file name is the original file name of the map file, and the map file value is read-in from a file.
    
    encoding/decoding map data
        A file could be a plain ASCII text file like most .txt files, or a binary file like a SDDS file. The data encoding/decoding algorithm supported by this service is:

        - ASCII data. If a map file is a plain text file, the data is read in directly as a list with each line as one value of the list since a list can be easily serialized into a JSON string.
        
        - Binary data. Since the data is transfered over network as JSON string, which doesn't support binary data natively, the binary data has to be encoded so that it can be placed into a string element in JSON. An algorithm, **Base64** as specified in RFC 3548, is used to encode/decode the binary data to/from a JSON string. The reasons for choosing Base64 are:

			1. it is a built-in module in Python which means the server has no dependency on a 3rd party library; 
			2. the ability to fit binary data into a strictly text-based and very limited format; 
			3. the overhead is minimal compared to the convenience of using JSON; 
			4. it is a simple, commonly used standard, and it is unlikely that something better could be found to be used with JSON; 
			5. encoded text strings can be safely used as parts of URLs, or included as part of an HTTP POST request.

    An example command of a request sent to server that returns the same result with as with retrieveLatticeInfo::
    
    /lattice/?function=retrieveLattice&name=*&version=*&branch=*
    
    To retrieve lattice data: ::
    
    /lattice/?function=retrieveLattice&name=*&version=*&branch=*&withdata=true
    
    To retrieve raw lattice data: ::
        
    /lattice/?function=retrieveLattice&name=*&version=*&branch=*&rawdata=true
    
    To retrieve lattice and raw data: ::
    
    /lattice/?function=retrieveLattice&name=*&version=*&branch=*&withdata=true&rawdata=true
    

* **retrieveLatticeStatus**

    Retrieves the status of a lattice, which is indicated by an integer. Each site could have its own convention for how to use the status integer. A typical use of the lattice status is to identify a golden lattice, and a reference definition could be as follows:
    
    +-----+-----------------------------------------------+
    | id  |   statement                                   |
    +=====+===============================================+
    |  0  |  current golden lattice                       |  
    +-----+-----------------------------------------------+
    |  1  |  alternative golden lattice                   |  
    +-----+-----------------------------------------------+
    |  2  |  lattice from live machine                    |  
    +-----+-----------------------------------------------+
    |  3  |  previous golden lattice                      |  
    +-----+-----------------------------------------------+

    **keywords** for searching: ::
    
        function:   retrieveLatticeStatus
        name:       lattice name
        version:    lattice version
        branch:     lattice branch
        status:     [optional]    lattice status

            
    If status is not specified, it gets all lattices having a status no matter what the status is.
        
    **Result data structure**: ::
    
            {'id':  # identifier of this lattice
                    {'lattice name':              # lattice name
                     'version': ,                 # version of this lattice
                     'branch': ,                  # branch this lattice belongs to
                     'status': ,                  # lattice description
                     'creator':      [optional],  # who first set the status
                     'originalDate': [optional],  # when this status was first set
                     'updated':      [optional],  # who last updated 
                     'lastModified': [optional],  # when it was last updated
                    } ,
                ...
             }

    An example command of a request sent to the server that gets all lattices which have a status: ::
    
    /lattice/?function=retrieveLatticeStatus&name=*&version=*&branch=*&status=*
    
GET Methods - Model
^^^^^^^^^^^^^^^^^^^^^^
As defined, a model is an output from either a simulation code, or from a measurement for a given lattice. In principle, model data could be re-produced within acceptable error tolerances when all initial parameters are in place.

* **retrieveModelCodeInfo**

    Retrieves the simulation code name and the algorithm name. 
	
    Since model data can be output from a simulation, it is necessary to capture some details about how the data was generated, e.g. what simulation code and algorithm were used. The code name could be the name of a particular simulation code, or whatever the name fits the site naming convention if the data is from a measurement. It is suggested to give a brief name for the algorithm, but this is not mandatory. 

    :NOTE: The code name with algorithm has to be unique, and an empty algorithm is treated as one value.
	
    **keywords** for searching: ::
    
        function:   retrieveModelCodeInfo
        name:       [optional] code name to generate a model
        algorithm:  [optional] algorithm to generate a model

    The client can search by either name, and/or algorithm. However, if both name and algorithm are not given, then the client raises an exception, and returns an **HTTP/404** error.

    **Result data structure**: ::
    
            {'id':  # model code internal id
                  {'name':         # simulation code name
                   'algorithm': ,  # algorithm, None if not specified.
                  } ,
                ...
             }

    An example command of a request sent to server to return all existing entries: ::
    
    /lattice/?function=retrieveModelCodeInfo&name=*&algorithm=*
    
    With this command, the client is able to check what name-algorithm combinations are already on the service, and is able to reuse an existing entry.

* **retrieveModelList**

    Retrieves model header information that satisfies the given constraints. 
    
    **keywords** for searching: ::
        
        function:       retrieveModelList
        latticename:    lattice name that this model belongs to
        latticeversion: the version of lattice
        latticebranch:  the branch of lattice
    
    **Result data structure**: ::    
    
        {'model name':                  # model name
            {'id': ,                    # internal model id number
             'latticeId': ,             # internal lattice id to identify
                                        # which lattice this particular model belongs to
             'description':, [optional] # description of this model
             'creator': ,    [optional] # who first created this model
             'originalDate':,[optional] # when this model was first created
             'updated': ,    [optional] # who last modified this model
             'lastModified':,[optional] # when this model was last modified
            }
            ...
        }

    An example command to get informations for all existing models for all lattices: ::
    
        /lattice/?function=retrieveModelList&latticename=*&latticeversion=*&latticebranch=*
    
    :NOTE: This command should be used with care since it might return a lot of information.
    
* **retrieveModel**

    Retrieves a model list that satisfies given constrains with global beam parameters.

    **keywords** for searching: ::
    
        function:    retrieveModelList
        name:        name of a model to be retrieved
        id:          id of a model to be retrieved
    
    Client can search and retrieve a model by either the name of a model, or its internal id. When an id is given, it retrieves that exact model which has the given id. 
    
    :NOTE: If both ID and name are given, it tries to match both. This is sometimes useful.
    
    **Result data structure**: ::    
    
        {'model name':                    # model name
                {'id': ,                  # model id 
                 'latticeId': ,           # id of the lattice to which the given model belongs
                 'description': ,         # description of this model
                 'creator': ,             # who first created this model 
                 'originalDate': ,        # when this model was first created
                 'updated': ,             # who last modified this model
                 'lastModified': ,        # when this model was last modified 
                 'tunex': ,               # horizontal tune
                 'tuney': ,               # vertical tune
                 'alphac': ,              # momentum compaction
                 'chromX0': ,             # linear horizontal chromaticity
                 'chromX1': ,             # non-linear horizontal chromaticity
                 'chromX2': ,             # high order non-linear horizontal chromaticity
                 'chromY0': ,             # linear vertical chromaticity
                 'chromY1': ,             # non-linear vertical chromaticity
                 'chromY2': ,             # high order non-linear vertical chromaticity
                 'finalEnergy': ,         # the final beam energy in GeV
                 'simulationCode': ,      # name of simulation code, 
                                          # Elegant and Tracy for example
                 'sumulationAlgorithm': , # algorithm used by simulation code, 
                                          # for example serial or parallel, 
                                          # or in case of tracy, SI, or SI/PTC
                 'simulationControl': ,   # various control constrains such as 
                                          # initial condition, beam distribution, 
                                          # and output controls
                 'simulationControlFile': # file name to control simulation conditions, 
                                          # like a .ele file for Elegant
                }
         ...
        }
                                
                               }
							   
    :NOTE: For data generated from ``Elegant``, ``finalEnergy`` is usually :math:`\beta*\gamma` unless the client has converted it before saving.
    
    An example command to get information for all existing models::
    
        /lattice/?function=retrieveModel&name=*
        
    :NOTE: This command should be used with care since it might return a lot of information.
    
    To retrieve information for a model with id=1: ::    
    
        /lattice/?function=retrieveModel&id=1
        
    To retrieve information for a model named ``whatever`` with id=1: ::    
    
        /lattice/?function=retrieveModel&id=1&name=whatever
        
    Wildcards are supported in the name matching; in this case, a model with a name that matches the pattern and with the given id will be returned by the server.
    
    
* **retrieveModelStatus**

    Retrieves the model status, if available. Like a lattice, a model can also have a status, which is indicated by an integer. 
    
    As for the lattice status, the model status definitiion can be customised by each site. A typical use of the model status is to identify a golden model, and a reference definition could be as follows:
    
    +-----+-----------------------------------------------+
    | id  |   statement                                   |
    +=====+===============================================+
    |  0  |  current golden model                         |  
    +-----+-----------------------------------------------+
    |  1  |  alternative golden model                     |  
    +-----+-----------------------------------------------+
    |  2  |  model from live machine                      |  
    +-----+-----------------------------------------------+
    |  3  |  previous golden model                        |  
    +-----+-----------------------------------------------+

    **keywords** for searching: ::
    
        function:  retrieveModelStatus
        name:      model name
        status:    id number of that status.

    If status is not specified, it retrieves all models with a status set, no matter what the status is.
        
    **Result data structure**: ::
        
        {'id':  # identifier of this lattice
            {'lattice name':              # lattice name
             'version': ,                 # version of this lattice
             'branch': ,                  # branch this lattice belongs to
             'status': ,                  # lattice description
             'creator':      [optional],  # who first set the status 
             'originalDate': [optional],  # when this status was first set 
             'updated':      [optional],  # who last updated the status
             'lastModified': [optional],  # when it was last updated
            },
            ...
        }
    
    
    An example to retrieve all models that have a status set: ::
        
        /lattice/?function=retrieveModelStatus&name=*&status=*
        
    
* **retrieveTransferMatrix**

    Retrieve transfer matrix from a given model, if one is available.
        
    **keywords** for searching: ::
    
        modelname:   the name of the model for which a transfer matrix is being requested 
        from:        floating-point number, s position of starting element, default 0
        to:          floating-point number, s position of ending element, 
                     default the max of element in a lattice

    **Result data structure**: ::
    
        {'model name':  # model name
            {
                'name':          [element name],
                'index':         [element index],
                'position':      [s position],
                'transferMatrix':[[transfer matrix],],
            }
            ...
        }
    
    It returns a map, or a dictionary in Python; results for each model are shown as one entry in this map, with a sub-map/sub-dictionary. The sub-map has 4 keys (described below), and the value of each key is a collection/list/array:
    
    - name: Element ``'name'`` appears in its lattice.
    - index: index'`` is a sequential number to identify element appeared in its lattice.
    - position: ``'position'`` is s position at the end of each element along beam direction, which is typically generated with a simulation code.
    - transferMatrix: ``'transferMatrix'`` is 6-dimensional beam linear transfer matrix from the starting point, which means the valued is propagated from s=0. The transfer matrix of each element is a sub-array of the transfer matrix with a structure like:
        [M00 M01 M01 M03 M04 M05 M06 M07 M08 .. M55]
        
        :NOTE: The value relies heavily on the simulation environment such as code, algorithm, etc.

    An example of a request sent to the server to get the transfer matrix from the model ``whateverthename``, for elements that start from s=12.3456 and end at s=34.5678: ::
        
        /lattice/?function=retrieveTransferMatrix&name=whateverthename&from=12.3456&to=34.5678
        
    If there are no elements in the given range, then the server returns an empty value.

* **retrieveClosedOrbit**

    Retrieve closed orbit distortion, if it is available, from a given model.
        
    **keywords** for searching: ::
    
        modelname:   the name of the model for which a closed orbit distorion is being requested
        from:        floating-point number, s position of starting element, default 0
        to:          floating-point number, s position of ending element, 
                     default the max of element in a lattice

    **Result data structure**: ::
    
        {'model name':  # model name
            {
                'name':     [element name],
                'index':    [element index],
                'position': [s position],
                'codx':     [codx],
                'cody':     [cody]
            }
            ...
        }
    
    It returns a map, or a dictionary in Python; results for each model are shown as a single entry in this map, with a sub-map/sub-dictionary. The sub-map has 5 keys (described below), and the value of each key is a collection/list/array:
    
    - name: Element ``'name'`` appears in its lattice.
    - index: ``'index'`` is a sequential number  to identify where the element appears in its lattice.
    - position: ``'position'`` is the s position at the end of each element along the beam direction, which is typically generated with a simulation code.
    - codx. ``'codx'`` is the horizontal closed orbit distortion.
    - cody. ``'cody'`` is the vertical closed orbit distortion.
    
    An example of a request it intendes to retrieve the closed orbit for model ``whateverthename``, whose element s position is (12.3456, 34.5678): ::
        
        /lattice/?function=retrieveClosedOrbit&name=whateverthename&from=12.3456&to=34.5678
        
    If there is no element in that range, the server returns an empty value.

* **retrieveTwiss**

    Retrieve Twiss parameters, if it is available, from a given model.
        
    **keywords** for searching: ::
    
        modelname:   the name of the model for which the Twiss parameters are being requested 
        from:        floating-point number, s position of start element, default is 0
        to:          floating-point number, s position of end element, 
                     default is the max of element in a lattice

    **Result data structure**: ::
    
        {'model name':  # model name
            {
                'name':     [element name],
                'index':    [element index],
                'position': [s position],
                'alphax':   [],
                'alphay':   [],
                'betax':    [],
                'betay':    [],
                'etax':     [],
                'etay':     [],
                'etapx':    [],
                'etapy':    [],
                'phasex':   [],
                'phasey':   [],
            }
            ...
        }
    
    It returns a map, or a dictionary in Python; results for each model are shown as a single entry in this map, with a sub-map/sub-dictionary. The sub-map has 4 keys (described below), and the value of each key is a collection/list/array:
    
    - name: Element ``'name'`` that appears in the lattice.
    - index: ``'index'`` is a sequential number to identify where the element appears in the lattice.
    - position: ``'position'`` is the s position at the end of each element along the beam direction, which is typically generated with a simulation code.
    - alphax: ``alphax`` is the horizontal :math:`\alpha` Twiss function
    - alphay: ``alphay`` is the vertical :math:`\alpha` Twiss function
    - betax: ``betax`` is the horizontal :math:`\beta` Twiss function
    - betay: ``betay`` is the vertical :math:`\beta` Twiss function
    - etax: ``etax`` is the horizontal dispersion
    - etay: ``etay`` is the vertical dispersion
    - etapx: ``etapx`` is slope of the horizontal dispersion
    - etapy: ``etapy`` is slope of the vertical dispersion
    - phasex: ``phasex`` is the horizontal phase advance
    - phasey: ``phasey`` is the vertical phase advance


    :NOTE: Be careful about the value, especially the unit of value. Usually, the value is stored as it is. It is suggested that client does not manipulate the value and uses code convention when it is stored. 

    An example of a command to request Twiss parameter for the model named ``whateverthename``, with element s position (12.3456, 34.5678): ::
        
        /lattice/?function=retrieveTwiss&name=whateverthename&from=12.3456&to=34.5678
        
    If there is no element in that range, the server will return an empty value.

* **retrieveBeamParameters**

    Retrieve all beam parameters of each element that satisfies the given constraints.
        
    **keywords** for searching: ::
    
        modelname:   the name of the model for which beam parameters are being requested 
        from:        floating-point number, s position of starting element, default is 0
        to:          floating-point number, s position of ending element, 
                     default is the max of element in a lattice

        {'model name':  # model name
            {
                'name':          [element name],
                'index':         [element index],
                'position':      [s position],
                'alphax':        [],
                'alphay':        [],
                'betax':         [],
                'betay':         [],
                'etax':          [],
                'etay':          [],
                'etapx':         [],
                'etapy':         [],
                'phasex':        [],
                'phasey':        [],
                'codx',          [],
                'cody',          [],
                'transferMatrix':[[transfer matrix],],
            }
            ...
        }
    
    The returned result is a collection of calling 3 APIs:``retrieveTransferMatrix``, ``retrieveClosedOrbit``, and ``retrieveTwiss``.    

    An example of a command to request all beam parameters from the model named ``whateverthename`` with element s position of (12.3456, 34.5678): ::        
        /lattice/?function=retrieveBeamParameters&name=whateverthename&from=12.3456&to=34.5678
        
    If there is no element in that range, the server returns an empty value.


POST Methods
^^^^^^^^^^^^^^^^^^^^^^

A POST method saves data into the service, and the APIs for post operations are listed in this section.

* **saveLatticeType**
    Saves lattice type information using the given lattice type name and format. The purpose behind saving the lattice type with its format is to capture the original lattice information, which will help when retrieving the original lattice, and converting a lattice to another format. If the lattice type with its format already exists, then the server returns an error.

    **keywords** to carry data:

    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::

        {'function': 'saveLatticeType',
         'name':     lattice type name,
         'format':   lattice type format
        }

    Lattice types are site-specific. Typical lattice types could be, but are not limited to: ::

        {'name': 'plain', 'format': 'txt'}
        {'name': 'tracy3',  'format': 'lat'}
        {'name': 'tracy4',  'format': 'lat'}
        {'name': 'elegant', 'format': 'lte'}

    If this operation completes successfully, then the server returns a map with the following structure: ::
        
        {'result': internal id}
    
    otherwise, it returns an error.

    A Python client example is shown below:
    
    .. code-block:: python
        :linenos:

        import httplib
        import urllib

        params = urllib.urlencode({'function': 'saveLatticeType', 
                                   'name': 'tracy3', 
                                   'format': 'lat'})
        headers = {'content-type':'application/json', 
                   'accept':'application/json'}
        conn = httplib.HTTPConnection('localhost', 8000)
        conn.request("POST", "/lattice/", params, headers)
        response = conn.getresponse()
        conn.close()

    In this case, if the lattice ``tracy3`` with a ``lat`` format does not yet exist on the server, then the client receives a result similar to: ::
    
        {"result": 9}
        
    If the lattice type and format already exist, then the server returns an error message: ::

        Lattice type (tracy3) with given format (lat) exists already.


* **saveLatticeInfo**

    Saves lattice description information. Lattice data, geometric layout and the strength setting are not included here. A lattice has a name, version, and branch, and those 3 make a lattice globally unique. A time stamp is added automatically by the underlying database, which is transparent to the client. If the lattice information already exists, then the server returns an error.

    **keywords** to transfer data:

    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::

        {'function':    'saveLatticeInfo',
         'name':        lattice name
         'version':     version number
         'branch':      branch name
         'latticetype': [optional] a dictionary which consists of {'name': , 'format': }
                         example lattice type is as described above.
         'description': [optional] description for this lattice, 
                        allow user to put any information here (< 255 characters)
         'creator':     [optional] original creator
         }

    If this operation completes successfully, the server returns the id of the new lattice as a map with the following structure: ::
    
        {'id': internal id}
    
    otherwise, the server returns an error.

    A Python client example is shown:
    
    .. code-block:: python
        :linenos:

        import httplib
        import urllib
        import json

        paramsdata = {'function': 'saveLatticeInfo', 
                      'name': 'lattice info demo',
                      'version': 20131001,
                      'branch': 'design',
                      'latticetype': json.dumps({'name': 'elegant', 'format': 'lte'}),
                      'description': 'demo example how to insert a lattice information',
                      'creator': 'Examiner'}
        params = urllib.urlencode(paramsdata)
        headers = {'content-type':'application/json', 
                   'accept':'application/json'}
        conn = httplib.HTTPConnection('localhost', 8000)
        conn.request("POST", "/lattice/", params, headers)
        response = conn.getresponse()
        conn.close()

    In this case, if the lattice does not yet exist, and the save operation is successful, the client receives a result similar to: ::
    
        {"id": 9}
        
    If the lattice already exists, then the server returns an error message similar to: ::

        lattice (name: lattice info demo, version: 20131001, branch: design) exists already.


* **updateLatticeInfo**

    Updates information for an existing lattice description. Once a lattice is saved, it cannot be deleted since it might be used by many other sources, it is possible to update it. If the lattice does not exist, the server returns an error.
    
    **keywords** to transfer data: 

    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::

        {'function':    'updateLatticeInfo',
         'name':        lattice name
         'version':     version number
         'branch':      branch name
         'latticetype': [optional] a dictionary which consists of {'name': , 'format': }
                        example lattice type is as described above.
         'description': [optional] description for this lattice, 
                        allow user put any info here (< 255 characters)
         'creator':     [optional] name who update this lattice head
         }

    If this operation completes successfully, the server returns the new lattice as a map: ::
    
        {'id': true}
    
    otherwise, the server returns an error.

    
    A Python client example is shown:
    
    .. code-block:: python
        :linenos:

        import httplib
        import urllib
        import json

        paramsdata = {'function': 'updateLatticeInfo', 
                      'name': 'lattice info demo',
                      'version': 20131001,
                      'branch': 'design',
                      'latticetype': json.dumps({'name': 'elegant', 'format': 'lte'}),
                      'description': 'demo example how to insert a lattice information',
                      'creator': 'Examiner'}
        params = urllib.urlencode(paramsdata)
        headers = {'content-type':'application/json', 
                   'accept':'application/json'}
        conn = httplib.HTTPConnection('localhost', 8000)
        conn.request("POST", "/lattice/", params, headers)
        response = conn.getresponse()
        conn.close()

    In this case, if the lattice exists and is successfully updated, then client receives a result similar to: ::
    
        {"result": true}

    If the lattice does not yet exist, the client receives an error similar to: ::

        Did not find lattice (name: lattice info demo, version: 20131001, branch: design).
    

* **saveLattice**

    Saves lattice data. It creates a new entry with the given lattice data, or returns an error if the lattice data already exists. 
    
    **keywords** to transfer data: 
    
    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::
    
        {'function':    'saveLattice',
         'name':        lattice name
         'version':     version number
         'branch':      branch name
         'latticetype': a dictionary which consists of {'name': , 'format': }
         'description': description for this lattice,
                            allow user put any info here (< 255 characters)
         'creator':     original creator
         'lattice':     lattice data, a dictionary:
                        {'name': ,
                         'data': ,
                         'raw': ,
                         'map': {'name': 'value'},
                         'alignment': ,
                         'control': {'name': ,
                                     'data': }, # control info for a simulation run, 
                                                # ele file for ``elegant`` for example
                         'init_Twiss':, # initial Twiss condition
                         }
                         name: file to be saved into, default is lattice name
                         data: lattice geometric and strength with predefined format
                         raw:  raw data, same with data but in original lattice format
                         map:  name-value pair dictionary
                         alignment: mis-alignment information
         'dosimulation': Flag to identify whether to perform a simulation. 
                         False by default.
         }
    
    The structure is similar to that for ``saveLatticeInfo`` except there are 2 additional keywords, ``lattice`` and ``dosimulation``. The data structure for these is: ::
    
        - lattice: Contains all lattice data, and transfers data  
                    from client to server. Its structure is described below.
        - dosimulation. A Flag to identify whether to perform a simulation. 
                    False by default, which means a simulation will not be carried out. 
    
    **lattice sub-structure**
    
    Real lattice information is included in lattice sub-structure. The keywords used by this structure are:
    
    - name: lattice file name to which the lattice raw data will be saved to on the server side.
    - data: lattice data from lattice file. The real data is in this structure, and each lattice format has a different requirement. Details are explained below.
    - raw: original lattice which might be transferred in a different format.
    - map: contains, for example, field map. A typical use of this is to transfer a kick map over the network. As described in the section :ref:`retrieveLattice <lattice_model_ref_retrieveLattice>` , plain text maps are read in as a list/array with each line in the file being one value of the array. For a binary map, the whole file has to be read in and encoded with the **Base64** algorithm.
    - control: data to perform simulation on the server side. Since there are many simulation codes having separate files, e.g. an .ele ``elegant`` file, this information is transferred here. ``name`` is the control file name, and ``data`` is the content of the control file. If a header is contained inside a lattice deck, e.g. tracy3/tracy4, its header information, excluding element layout, could also be saved here.
    - alignment: place to hold misalignment data. This is currently a place holder, and has not yet been implemented. An integration with real misalignment data from a survey could be contained here, and integrated on the server side.
    - init_Twiss: contains initial Twiss parameters, if applicable. This is currently a place holder, and has not yet been implemented.
    
    
    **data** sub-structure of lattice sub-structure
    
    The current implementation of the lattice service supports 3 different formats:
		1. plain text format with tab-separation, 
		2. ``tracy3``, and 
		3. ``elegant``. 
		
	To prevent the server from parsing many different lattice formats, the server only accepts lattices from the client with these 3 dedicated formats.

    **1. Tab-separated Plain Text Lattices**
    
    Suggested lattice types for this lattice file format: ``{'name': 'plain', 'format': 'txt'}``. 
    
    A plain text file is transported as an array, such that each line of the file corresponds to one value of the array. A header is needed and should have the following format: ::
    
             ElementName ElementType  L  s   K1    K2   Angle [dx dy dz pitch yaw roll map]
                                      m  m  1/m2  1/m3  rad   [m  m  m  rad   rad rad     ]
             ------------------------------------------------------------------------------
    
    The 1\ :sup:`st` line of the header contains the name for each column to identify what the property. The first 7 columns will most likely be common to all lattices, but the user is also able to add extra information like alignment errors and maps such as a kick map file name of an insertion device. It is recommended that the map appear as the last column. The 2\ :sup:`nd` line of the header contains unit information, if applicable, and the 3\ :sup:`rd` line is a divider between the header and the body. 
    
    The file also needs that the ``s`` position start from zero (0), and it is recommended to include the starting point, e.g., ``_BEG_`` in ``elegant`` or ``begin`` in ``tracy3/tracy4``.

    The misalignment could be a displacement along (:math:`\delta_x, \delta_y, \delta_x`) and/or a rotation around (:math:`\theta_x, \theta_y, \theta_z`, or pitch, yaw, roll) the ``x``, ``y``, and ``z`` axes.

    :NOTE: Currently, all properties of an element have to be on one line; multiple lines are not yet supported.

    **2. ``Tracy3``, and ``elegant`` Lattices**

    Suggested lattice types for these lattice file formats: ::
    
        ===========   ==========================================
          lattice         type
        -----------   ------------------------------------------
          tracy3        {'name': 'tracy3',  'format': 'lat'}
        -----------   ------------------------------------------
          tracy4        {'name': 'tracy4',  'format': 'lat'}
        -----------   ------------------------------------------
          elegant       {'name': 'elegant', 'format': 'lte'}
        ===========   ==========================================

    

    For a lattice used by a particular simulation code like ``tracy3``, ``tracy4``, or ``elegant``, it has its own grammar, and most likely differs significantly with each other. To avoid the problem of the server needing to parse each particular lattice format, a data structure is designed as below: ::
    
        {sequence #: { 'name':     ,
                       'length':   , 
                       'position': , 
                       'type':     , 
                       ...         [other properties such as K1, K2, or others]
                     }
        }
    
    For example, a ``tracy`` lattice could be transported as: ::
    
  		'data': {
		0: {'position': '0.00000', 'length': '0.0', 
		    'type': 'Marker', 'name': 'BEGIN'},
		1: {'position': '4.29379', 'length': '4.29379', 
		    'type': 'Drift', 'name': 'DH05G1C30A'},
		2: {'position': '4.31579', 'length': '0.022', 
		    'type': 'Drift', 'name': 'DFH2G1C30A'},
		3: {'position': '4.31579', 'type': 'Corrector,Horizontal', 
		    'name': 'FXH2G1C30A', 'Method': 'Meth'},
		4: {'position': '4.31579', 'type': 'Corrector,Vertical', 
		    'name': 'FYH2G1C30A', 'Method': 'Meth'},
		5: {'position': '4.33779', 'length': '0.022', 
		    'type': 'Drift', 'name': 'DFH2G1C30A'},
		6: {'position': '4.65000', 'length': '0.31221', 
		    'type': 'Drift', 'name': 'DH1G1A'},
		7: {'position': '4.65000', 'type': 'Marker', 'name': 'GEG1C30A'},
		8: {'position': '4.65000', 'type': 'Marker', 'name': 'GSG2C30A'},
		9: {'name': 'SH1G2C30A', 'K': '12.098850', 'N': 'Nsext', 
		    'length': '0.2', 
		    'position': '4.85000', 'type': 'Sextupole', 'Method': 'Meth'},
		10: {'position':'4.93500', 'length':'0.085', 'type':'Drift', 'name':'DH1AG2A'},
		11: {'position': '4.93500', 'type': 'Beam Position Monitor', 
		    'name': 'PH1G2C30A'},
		12: {'position': '5.01250', 'length': '0.0775', 'type': 'Drift', 
		    'name': 'DBPM01'},
		13: {'name': 'QH1G2C30A', 'K': '-0.633004', 'N': 'Nquad', 
		    'length': '0.275', 'position': '5.28750', 'type': 'Quadrupole', 
		    'Method': 'Meth'},
		14: {'position': '5.43250', 'length': '0.145', 'type': 'Drift', 
		    'name': 'DH2AG2A'},
		15: {'name': 'SQHHG2C30A', 'K': '0', 'N': 'Nquad', 'length': '0.1', 
		    'position': '5.53250', 'type': 'Quadrupole', 'Method': 'Meth'},
		16: {'position': '5.53250', 'type': 'Corrector,Horizontal', 
		    'name': 'CXH1G2C30A', 'Method': 'Meth'},
		17: {'position': '5.53250', 'type': 'Corrector,Vertical', 
		    'name': 'CYH1G2C30A', 'Method': 'Meth'},
		18: {'name': 'SQHHG2C30A', 'K': '0', 'N': 'Nquad', 'length': '0.1', 
		    'position': '5.63250', 'type': 'Quadrupole', 'Method': 'Meth'},
		....
		}
				
    **Online Simulation**

    Currently, the server supports simulation using ``tracy3`` or ``elegant``. If the lattice sent from a client is correctly formatted as one of these, then the client can set the ``dosimulation`` flag to be true to trigger the server to carry out a quick simulation, and to save the simulation results. However, if the lattice format is not one of ``tracy3`` or ``elegant``, and even if ``dosimulation`` is set to true, the server does not perform the simulation. Also the client is responsible for checking the lattice to ensure that a simulation can be executed successfully; the server does not do this check. Commands needed by the server are: ::
      
      ===========   =====================
         code           commands
      -----------   ---------------------
        tracy3          tracy3
      -----------   ---------------------
        elegant        elegant
                       sddsprocess
                       sddsxref
                       sddsconvert
                       sddsprintout
      ===========   =====================
    
    
    :NOTE: These commands have to be accessible by the server. If they are not in the searchable PATH, some environment variables, ``TRACY3_CMD`` for ``tracy3`` and ``ELEGANT_CMD`` for ``elegant``, respectively, have to be set. 

    If the simulation completes successfully, then the simulation results are saved automatically together with the associated lattice. The data is saved in 2 parts: (a) global beam parameters like final beam energy, and (b) beam parameters for each element. Data from different simulation codes are slightly different and the detailed data for ``tracy3`` and ``elegant`` are described:
    
    For ``tracy``, the global parameters for a ring are: ::
    
        'tunex': horizontal tune
        'tuney':  vertical tune
        'chromX0': horizontal linear chromaticity
        'chromY0': vertical linear chromaticity
        'finalEnergy': beam energy in GeV
        'alphac': momentum compaction factor
        'simulationCode':  which is ``tracy3``
        'simulationAlgorithm': ,  which is ``SI``

    For a linear machine, only the ``finalEnergy`` is saved as a global parameter.
    
    Parameters for each element are: ::
        
        'alphax': ,
        'alphay': ,
        'betax': ,
        'betay': ,
        'etax': ,
        'etay': ,
        'etapx': ,
        'etapy': ,
        'phasex': ,
        'phasey': ,
        'codx': ,
        'cody': ,
        'transferMatrix': which is a linear matrix ordered M00, M01, M02, ..., M55
        's': ,
        'energy': energy at each element
    
    For elegant, global parameters for a ring are: ::
    
        'tunex': , horizontal tune
        'tuney': , vertical tune
        'chromX0': , horizontal linear chromaticity
        'chromX1': , non-linear horizontal chromaticity
        'chromX2': , high order non-linear horizontal chromaticity
        'chromY0': , vertical linear chromaticity
        'chromY1': , non-linear vertical chromaticity
        'chromY2': , high order non-linear vertical chromaticity
        'finalEnergy': beam energy in GeV, this value is recorded as beta*gamma
        'alphac': , momentum compaction factor
        'simulationCode': , which is ``elegant``
        'simulationAlgorithm': ,  which is ``matrix``

    Parameters for each element are: ::
        
        'alphax': ,
        'alphay': ,
        'betax': ,
        'betay': ,
        'etax': ,
        'etay': ,
        'etapx': ,
        'etapy': ,
        'phasex': ,
        'phasey': ,
        'codx': ,
        'cody': ,
        'transferMatrix': which is a linear matrix ordered M00, M01, M02, ..., M55
        's': ,
        'energy': energy at each element, this value is recorded as beta*gamma
    
    If a lattice exists, and the save operation is successful, the client receives a result similar to: ::
    
        {"result": true}

    If a lattice does not exist, the client receives an error as: ::

        Did not find lattice (name: lattice info demo, version: 20131001, branch: design).

* **updateLattice**

    Updates lattice data. This function is similar to ``saveLattice``, but updates lattice data for an existing lattice. The data structure is the same as for ``saveLattice``.
    If lattice data does not exist, the server returns an error, otherwise, if lattice is there and is updated successfully, the client receives a result similar to: ::
    
        {"result": true}

    As with ``saveLattice``, the user can request the server to perform a simulation with this function. 

* **saveLatticeStatus**

    Saves lattice status. Each lattice could be assigned a status, which is an integer with a site-specific convention. The status captures details about who assigned a status for a specific lattice, and when. Also who updated the status, and when.
    
    **keywords** to transfer data: 
    
    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::
    
        {'function':    'saveLatticeStatus',
         'name':        lattice name
         'version':     version number
         'branch':      branch name
         'creator':     original creator
         'status':      who commands this function
        }
    
    How to utilize the ``status`` is entirely up to each site, and could vary differently. A suggested convention could be as below: ::


        0: current golden lattice [by default]
        1: current live lattice
        2: alternative golden lattice
        3: previous golden lattice, but not any more
        
        (The number is customisable and can be changed or extended.)
    
    If the command is successful, then the server returns: ::
        
        {'result': true}
    
    otherwise, an exception is raised.
    
    :NOTE: The status is not captured in this version, therefore, there is no difference between the ``save*`` and ``update*`` commands.  All are treated as saving a new status.

* **saveModelCodeInfo**

    Saves information required to carry out a simulation for a model. In this service, a model is defined as an output from either simulation, or measurement. To help with understanding each particular model, its environment, particularly the name of the simulation code and a brief description for the algorithm used, is captured.

    **keywords** to transfer data: 
    
    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::
    
        {'function':    'saveModelCodeInfo',
         'name':        simulation code name
         'algorithm':   algorithm used to generate the beam parameters
        }

    Examples of algorithms are (the user can define his own): ::

      ===========   =====================
        name           algorithm
      -----------   ---------------------
        tracy3          SI
      -----------   ---------------------
        tracy3          PTC
      -----------   ---------------------
        tracy4          SI
      -----------   ---------------------
        tracy4          PTC
      -----------   ---------------------
        elegant         serial
      -----------   ---------------------
        elegant         parallel
      ===========   =====================    
    
    One exception here is to deal with model data from measurement, which could be determined by each site, for example using ``measurement`` as the name.

    If this command is successful, then the following structure is returned: ::
        
        {'result': true}
    
    otherwise, an exception is raised.

* **saveModelStatus**
    
    Saves model status. Similar to the equivalent command for the lattice, each model could be assigned a status, which is an integer with a  site-specific convention. The status captures details about who assigned a status for a specific model , and when. Also who updated the status, and when.
    
    **keywords** to transfer data: 
    
    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::
    
        {'function':    'saveModelStatus',
         'name':        model name
         'status':      who commands this function
        }
    
    How to utilize the ``status`` is entirely up to each site, and could vary differently. A suggested convention could be as below: ::

        0: current golden model [by default]
        1: alternative golden model
        2: previous golden model, but not any more
        
        (The number is customisable and can be changed or extended.)
    
    If the command is successful, then the server returns: ::
        
        {'result': true}
    
    otherwise, an exception is raised.
    
    :NOTE: The status is not captured in this version, therefore, there is no difference between the ``save*`` and ``update*`` commands.  All are treated as saving a new status.
    
* **saveModel**
    
    Saves a model result for a given lattice. It requires that a lattice exists.

    **keywords** to transfer data:

    The data is transferred to the server using a map, or a dictionary in Python, with the following format: ::
    
        {'function':      'saveModel',
         'latticename':   lattice name that this model belongs to
         'latticeversion: the version of lattice
         'latticebranch:  the branch of lattice
         'model':         a dictionary which holds all data 
        }        
    
	Details of the data contained in the model sub-structure are described below.
	
    **model** sub-structure: ::
    
        {'model name':               # model name
           { # header information
            'description': ,         # description of this model
            'creator': ,             # who requested this function
            'tunex': ,               # horizontal tune
            'tuney': ,               # vertical tune
            'alphac':                # momentum compaction factor
            'chromX0': ,             # linear horizontal chromaticity
            'chromX1': ,             # non-linear horizontal chromaticity
            'chromX2': ,             # high order non-linear horizontal chromaticity
            'chromY0': ,             # linear vertical chromaticity
            'chromY1': ,             # non-linear vertical chromaticity
            'chromY2': ,             # high order non-linear vertical chromaticity
            'finalEnergy': ,         # the final beam energy in GeV
            'simulationCode': ,      # name of simulation code, Elegant and Tracy for example
            'sumulationAlgorithm': , # algorithm used by simulation code, for example serial 
                                     # or parallel for elegant, and SI or PTC for Tracy 
            'simulationControl': ,   # various control constrains such as initial conditions, 
                                     # beam distribution, and output controls
            'simulationControlFile': # file name that control the simulation conditions, 
                                     # like a .ele file for elegant simulation data
            'beamParameter':         # a map/dictionary consists of Twiss, close orbit, 
                                     # transfer matrix and others
           }
           ...
        }
    
    This sub-structure allows a client to transfer multiple results to the server at the same time. All these values apply to the entire model, except for the ``beamParameter`` structure, which applies to each element.
    
    The ``simulationControl`` is read in from a file as a list with each line of the file as one value of the list; the file name is contained in ``simulationControlFile``.
    
    **beamParameter** Sub-structure
    
    Beam parameters at each element is contained in the ``beamParameter`` sub-structure as follows: ::
    
        { element_order: #element_order starts with 0.
            { 'name': ,     # element name
              'position': , # element position
              'alphax': ,
              'alphay': ,
              'betax': ,
              'betay': ,
              'etax': ,
              'etay': ,
              'etapx': ,
              'etapy': ,
              'phasex': ,
              'phasey': ,
              'codx': ,
              'cody': ,
              'transferMatrix': ,
              'indexSliceCheck': ,
              'energy': ,
              'particleSpecies': ,
              'particleMass': ,
              'particleCharge': ,
              'beamChargeDensity': ,
              'beamCurrent': ,
              'x': ,
              'xp': ,
              'y': ,
              'yp': ,
              'z': ,
              'zp': ,
              'emittancex': ,
              'emittancey': ,
              'emittancexz':  
            }
         }

    Most values appear here as primitive data such as double, or string, except for the transferMatrix which is a 2-D array with a structure as follows:
    
    **transferMatrix** sub-structure: ::
    
        [[M00, M01, M02, ..., M05], [M10, M11, ..., M15], ..., [M50, M51, ..., M55]]
        
    :NOTE: 
        - In principle, the server is capable of capturing  any type of transfer matrix, however, the current implementation supports a linear transfer matrix only.
        - The element layout/sequence contained in this structure has to correspond to the one in lattice.
    
    If this command completes successfully, then it returns the ids of the new model with a structure as follows: ::
        
        {'result': [ids]}
    
    otherwise, an exception is raised.
    
* **updateModel**

    Updates an existing model. If model already exists, then it is suggested that ``updateModel`` be used instead of ``saveModel``. The data structure for ``updateModel`` is the same as that for ``saveModel``.

    If the command is successful, then the server returns: ::
        
        {'result': true}
    
    otherwise, an exception is raised.
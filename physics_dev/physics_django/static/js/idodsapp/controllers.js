/*
 * Controllers for insertion device online data service module
 *
 * @author: Dejan Dežman <dejan.dezman@cosylab.com>
 * @created: Feb 26, 2014
 */

app.controller('searchCtrl', function($scope) {
	setUpSearchForm();
});

app.controller('indexCtrl', function($scope, $location, $anchorScroll) {

	$scope.top = function() {
		//l($location.hash());
		var id = $location.hash();

		// If no Log entry is selected, go to the top
		if(id === "" || id === "top") {
			$location.hash("top");
			$anchorScroll();

		// Scroll to the device
		} else {
			$location.hash("");
			var element = $('input[value=' + id + ']');

			$('html, body').animate({
				scrollTop: element.parent().offset().top
			}, 100);
		}
	};
});

/*
 * Main controller when we load the main page
 */
app.controller('mainCtrl', function($scope, $window, $modal, $routeParams, navigationFactory){
	$scope.version = version;
	$scope.style = {};
	$scope.style.middle_class = "container-scroll-middle";
	$scope.style.right_class = "container-scroll-last-one";
	$scope.currentNav = {};
	setUpLoginForm();
	$scope.nav = navigationFactory.nav;

	$scope.$on('handleBroadcast', function() {
		$scope.currentNav = navigationFactory.view;
	});

	$scope.changeEntity = function(entityName) {
		$('#view_dropdown').dropdown('toggle');
		var newLocation = createRouteUrl(undefined, entityName, []);
		$window.location = newLocation;
	};

	// Show add form in the right pane
	$scope.addItem = function() {
		l($scope.currentNav.name);
		var location = createRouteUrl($routeParams, $scope.currentNav.name, entityParameters[$scope.currentNav.name]) + "/id/new/action/save";
		$window.location = location;
	};

	$scope.session = {};
	$scope.authenticated = {};
	$scope.authenticated.error = false;

	$scope.login = function() {

		$.ajax({
			url: serviceurlraw + "user/login/",
			method: "POST",
			data: "username=" + $scope.session.username + "&password=" + $scope.session.password
		}).success(function(data, status, headers, config) {
			$scope.authenticated.error = false;
			$scope.$apply();
			$window.location.reload();

		}).error(function(data, status, headers, config) {
			$scope.authenticated.error = true;
			$scope.$apply();
		});
	};

	$scope.logout = function() {

		$.ajax({
			url: serviceurlraw + "user/logout/",
			method: "POST"
		}).success(function(data, status, headers, config) {
			$window.location.reload();

		}).error(function(data, status, headers, config) {

		});
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchVendorCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[0];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "vendor", ["name", "description"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		$window.location = newLocation;
	};

	// Vendor search button click
	$scope.searchForItem = function(search) {
		// var newDisplayString = generateSearchQuery(search);
		// l(newDisplayString);
		// search.display = newDisplayString[0];
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "vendor", ["name", "description"]) + "/list";
		$window.location = newLocation;
	};
});

/*
 * List vendor in the middle pane
 */
app.controller('listVendorCtrl', function($scope, $routeParams, $http, $window, Vendor, vendorFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	var previousItem;
	$scope.vendors = [];

	vendorFactory.retrieveVendors($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new Vendor(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.vendors.push(newItem);
		});
		$scope.vendors.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "vendor", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, "vendor", ["name", "description"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showVendorCtrl', function($scope, $routeParams, $http, $window, Vendor, vendorFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new Vendor();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;

	// Get vendor from the factory
	// Get inventory from the factory if updating
	if($routeParams.action != "save") {
		vendorFactory.retrieveVendor($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "vendor", ["name", "description"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var vendor = new Vendor(newItem);
		l(vendor);
		var result = vendorFactory.checkVendor(vendor);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			delete $scope.error;
			var promise;
			l($scope.element);

			if(action === "update") {
				promise = vendorFactory.updateVendor($scope.element);

			} else if(action == "save") {
				promise = vendorFactory.saveVendor($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Vendor successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchCmpntTypeCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[1];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "cmpnt_type", ["name", "description"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "cmpnt_type", ["name", "description"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listCmpntTypeCtrl', function($scope, $routeParams, $http, $window, CmpntTypeInfo, CmpntType, cmpntTypeFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = CmpntTypeInfo;
	var previousItem;
	$scope.types = [];

	cmpntTypeFactory.retrieveCompntTypes($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new CmpntType(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.types.push(newItem);
		});
		$scope.types.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, "cmpnt_type", ["name", "description"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showCmpntTypeCtrl', function($scope, $routeParams, $http, $window, CmpntTypeInfo, CmpntType, CmpntTypeType, cmpntTypeFactory, cmpntTypeTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new CmpntType();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = CmpntTypeInfo;

	$scope.types = [];
	$scope.new.prop_keys = [];

	// Retrieve all Componet type property types
	cmpntTypeTypeFactory.retrieveCompntTypeTypes({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.types.push(item.name);
		});
	});

	// Append new property
	$scope.appendProperty = function() {

		if($routeParams.action === "save"){
			$scope.new.prop_keys.push({'name': '', 'value': ''});

		} else {
			$scope.element.prop_keys.push({'name': '', 'value': ''});
		}
		l($scope.props);
	};

	// Property name dropdown has changed
	$scope.changePropertyName = function() {
		l($scope.props);
	};

	// Get component type from the factory
	if($routeParams.action != "save") {
		cmpntTypeFactory.retrieveCmpntType($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type", ["name", "description"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new CmpntType(newItem);
		l(item);
		var result = cmpntTypeFactory.checkCmpntType(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {

				$.each($scope.element.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.element.props = JSON.stringify(propsObject);

				promise = cmpntTypeFactory.updateCmpntType($scope.element);

			} else if(action == "save") {

				$.each($scope.new.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.new.props = JSON.stringify(propsObject);
				promise = cmpntTypeFactory.saveCmpntType($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Component type successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchCmpntTypeTypeCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[2];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "cmpnt_type_type", ["name", "description"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "cmpnt_type_type", ["name", "description"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listCmpntTypeTypeCtrl', function($scope, $routeParams, $http, $window, CmpntTypeType, CmpntTypeTypeInfo, cmpntTypeTypeFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = CmpntTypeTypeInfo;
	var previousItem;
	$scope.types = [];

	cmpntTypeTypeFactory.retrieveCompntTypeTypes($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new CmpntTypeType(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.types.push(newItem);
		});
		$scope.types.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type_type", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, "cmpnt_type_type", ["name", "description"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showCmpntTypeTypeCtrl', function($scope, $routeParams, $http, $window, CmpntTypeType, CmpntTypeTypeInfo, cmpntTypeTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new CmpntTypeType();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = CmpntTypeTypeInfo;

	// Get component type from the factory
	if($routeParams.action != "save") {
		cmpntTypeTypeFactory.retrieveCmpntTypeType($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type_type", ["name", "description"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	// Save item into database
	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new CmpntTypeType(newItem);
		l(item);
		var result = cmpntTypeTypeFactory.checkCmpntTypeType(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = cmpntTypeTypeFactory.updateCmpntTypeType($scope.element);

			} else if(action == "save") {
				promise = cmpntTypeTypeFactory.saveCmpntTypeType($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Component type property type successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInventoryCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.device[1];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory", entityParameters.inventory) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory", entityParameters.inventory) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listInventoryCtrl', function($scope, $routeParams, $http, $window, InventoryInfo, Inventory, inventoryFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = InventoryInfo;
	var previousItem;
	$scope.items = [];

	inventoryFactory.retrieveItems($routeParams).then(function(result) {

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new Inventory(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "inventory", entityParameters.inventory) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;
		$routeParams.serial_no = item.serial_no;
		$routeParams.cmpnt_type_name = item.cmpnt_type_name;
		$routeParams.vendor_name = item.vendor_name;

		var location = createRouteUrl($routeParams, "inventory", entityParameters.inventory) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInventoryCtrl', function($scope, $routeParams, $http, $window, InventoryInfo, CmpntType, Inventory, cmpntTypeFactory, offlineDataFactory, OfflineData, inventoryTypeFactory, inventoryFactory, vendorFactory, EntityError, RotCoilData, rotCoilDataFactory, HallProbeData, hallProbeDataFactory){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new Inventory();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InventoryInfo;
	$scope.deviceCatagoryList = deviceCatagoryList;
	$scope.measurementDataLocationList = measurementDataLocationList;

	$scope.types = [];
	$scope.props = [];
	$scope.vendors = [];
	$scope.new.prop_keys = [];
	$scope.offlinedata = [];
	$scope.statusMap = statusArrMap;
	$scope.measurementDataData = {};

	$scope.measurementData = {
		'location': measurementDataLocationList,
		'rot_coil_data': new RotCoilData(),
		'hall_probe_data': new HallProbeData()
	};

	// Retrieve all Component types
	cmpntTypeFactory.retrieveCompntTypes({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.types.push(item.name);
		});
	});

	// Retrieve all Inventory property templates
	inventoryTypeFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.props.push(item.name);
		});
	});

	// Retrieve all vendors
	vendorFactory.retrieveVendors({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.vendors.push(item.name);
		});
	});

	$scope.toggleTableRows = function(el, type, index) {
		l(el);
		toggleTableRows(el.target, type + index);
	};

	// Append new property
	$scope.appendProperty = function() {

		if($routeParams.action === "save"){
			$scope.new.prop_keys.push({'name': '', 'value': ''});

		} else {
			$scope.element.prop_keys.push({'name': '', 'value': ''});
		}
	};

	// Property name dropdown has changed
	$scope.changePropertyName = function() {
		l($scope.props);
	};

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		inventoryFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.inventory_id = result.id;
			l($scope.element);

			if ($routeParams.action == "retrieve") {

				// Get offline data
				offlineDataFactory.retrieveItems({'inventory_name': result.name}).then(function(result) {
					$.each(result, function(i, item){
						$scope.offlinedata.push(new OfflineData(item));
					});

					l($scope.offlinedata);
				});

				if(result.__device_category__ && result.__device_category__ === 'magnet' && result.__measurement_data_settings__) {
					var measDataPromise;

					if(result.__measurement_data_settings__.source === 'rot_coil_data') {
						measDataPromise = rotCoilDataFactory.retrieveItems({'inventory_name': result.name});

					} else {
						measDataPromise = hallProbeDataFactory.retrieveItems({'inventory_name': result.name});
					}

					measDataPromise.then(function(measurement) {

						$.each(measurement, function(id, meas) {

							$.each(meas, function(key, value) {

								if($scope.measurementDataData[key]) {
									$scope.measurementDataData[key].push(value);

								} else {
									$scope.measurementDataData[key] = [value];
								}
							});
						});
					});
				}
			}
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "inventory", entityParameters.inventory) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.updateMeasurementData = function() {
		var newWindowUrl = serviceurlraw + "id/measurement/#/" + "inventory_name/" + $routeParams.name + "/" + "view/readwrite";

		$window.open(newWindowUrl);
	};

	$scope.expandToVectorView = function() {
		var newWindowUrl = serviceurlraw + "id/measurement/#/" + "inventory_name/" + $routeParams.name + "/" + "view/readonly";

		$window.open(newWindowUrl);
	};

	$scope.cleanMeasurementDataSettingsColumns = function(item) {
		item.columns = {};

		l(item.source);

		var columnList = $scope.measurementData[item.source].retrieve;

		$.each(columnList, function(i, column) {

			if(column === 'inventory_name' || column === 'sub_device') {
				item.columns[column] = {'display_name': '', 'displayed': true};

			} else {
				item.columns[column] = {'display_name': '', 'displayed': false};
			}
		});
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		l(newItem);
		var item = new Inventory(newItem);
		var result = inventoryFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				$scope.element.prop_keys.push({'name': '__device_category__', 'value': $scope.element.__device_category__});
				$scope.element.prop_keys.push({'name': '__measurement_data_settings__', 'value': $scope.element.__measurement_data_settings__});

				$.each($scope.element.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.element.props = JSON.stringify(propsObject);

				promise = inventoryFactory.updateItem($scope.element);

			} else if(action == "save") {
				$scope.new.prop_keys.push({'name': '__device_category__', 'value': $scope.new.__device_category__});
				$scope.new.prop_keys.push({'name': '__measurement_data_settings__', 'value': $scope.new.__measurement_data_settings__});

				$.each($scope.new.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.new.props = JSON.stringify(propsObject);

				promise = inventoryFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Inventory successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInventoryTypeCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[3];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory_type", ["name"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory_type", ["name"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listInventoryTypeCtrl', function($scope, $routeParams, $http, $window, InventoryTypeInfo, InventoryType, inventoryTypeFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = InventoryTypeInfo;
	var previousItem;
	$scope.items = [];

	inventoryTypeFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new InventoryType(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "inventory_type", ["name"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;

		var location = createRouteUrl($routeParams, "inventory_type", ["name"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInventoryTypeCtrl', function($scope, $routeParams, $http, $window, InventoryTypeInfo, InventoryType, inventoryTypeFactory, cmpntTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new InventoryType();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InventoryTypeInfo;

	$scope.types = [];

	// Retrieve all Component types
	cmpntTypeFactory.retrieveCompntTypes({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.types.push(item.name);
		});
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		inventoryTypeFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.tmplt_id = result.id;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "inventory_type", ["name"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new InventoryType(newItem);
		var result = inventoryTypeFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = inventoryTypeFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = inventoryTypeFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Inventory property template successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInstallCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.device[0];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	$scope.changeMaster = function(type) {
		l(type);
		l($scope.group);
	};

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install", entityParameters.install) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install", entityParameters.install) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listInstallCtrl', function($scope, $routeParams, $http, $window, InstallInfo, Install, installFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = InstallInfo;
	var previousItem;
	$scope.items = [];

	installFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new Install(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "install", entityParameters.install) + "/id/new/action/save";
		$window.location = location;
	};

	// Show add form in the right pane
	$scope.addInsertionDevice = function() {
		var location = createRouteUrl($routeParams, "install", entityParameters.install) + "/saveid";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}
		l(item);

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;
		$routeParams.description = item.description;
		$routeParams.cmpnt_type = item.cmpnt_type;
		$routeParams.coordinatecenter = item.coordinatecenter;

		var location = createRouteUrl($routeParams, "install", entityParameters.install) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInstallCtrl', function($scope, $routeParams, $http, $window, installRelPropFactory, InstallRel, installRelFactory, InstallRelProp, InstallInfo, Install, InventoryToInstall, installFactory, inventoryToInstallFactory, onlineDataFactory, inventoryFactory, Inventory, OnlineData, offlineDataFactory, OfflineData, cmpntTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new Install();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InstallInfo;

	$scope.types = [];
	$scope.inventories = [];
	$scope.inventory_id = undefined;
	$scope.onlinedata = [];
	$scope.offlinedata = [];
	$scope.statusMap = statusArrMap;
	$scope.nodeTypeList = nodeTypeList;

	// Retrieve all Component types
	cmpntTypeFactory.retrieveCompntTypes({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.types.push(item.name);
		});
	});

	$scope.loadInventories = function() {

		// Retrieve all inventories
		inventoryFactory.retrieveItems({"not_installed": true}).then(function(result) {
			$.each(result, function(i, item){
				$scope.inventories.push(item);
			});
		});
	};

	// If updating, first retrieve an inventory that belongs to current install, then the others
	if ($routeParams.action == "update") {
		installFactory.retrieveItem($routeParams).then(function(inst_result) {

			// Setting inventoryToInstall
			var i2i = new InventoryToInstall({
				"inventory_to_install": undefined,
				"install_name": inst_result.name,
				"inventory_id": undefined
			});

			// Making a promise
			var i2iPromise = inventoryToInstallFactory.retrieveItems(i2i);

			i2iPromise.then(function(data) {

				// If results are not empty
				if (!isArrayEmpty(data)) {
					inventoryFactory.retrieveItems({"name": data[Object.keys(data)[0]].inventory_name}).then(function(inv) {
						
						var thisInv = inv[Object.keys(inv)[0]];
						$scope.element.inventory = thisInv;
						$scope.inventories.push(thisInv);
					});
				}
			});
		});
		$scope.loadInventories();

	// Retrieve all available inventories, that can be installed
	} else {
		$scope.loadInventories();
	}

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		installFactory.retrieveItem($routeParams).then(function(inst_result) {
			$scope.element = inst_result;
			$scope.element.old_name = inst_result.name;
			l("InstallFactory retrieve: ");
			l(inst_result);

			if ($routeParams.action == "update") {

				// If a device does not have a node_type set, make it a Real type
				// This is necessary due to old devices that do not have __node_type_ set yet
				if ($scope.element.__node_type__ == "") {

					$scope.element.__node_type__ = $scope.nodeTypeList[2].name;
				}
			}

			if ($routeParams.action == "retrieve") {
				$scope.map = {};

				inventoryToInstallFactory.retrieveItems({'install_name': $scope.element.name, 'inventory_id': '*'}).then(function(result) {
					var keys = Object.keys(result);

					if(keys.length > 0) {
						$scope.map = result[keys[0]];

						// Get offline data
						inventoryFactory.retrieveItems({'inventory_id': $scope.map.inventory_id}).then(function(result) {
							l(result);
							var keys = Object.keys(result);
							$scope.inventory = new Inventory(result[keys[0]]);
						});

						// Get offline data
						offlineDataFactory.retrieveItems({'inventory_id': $scope.map.inventory_id}).then(function(result) {

							$.each(result, function(i, item){
								$scope.offlinedata.push(new OfflineData(item));
							});
						});
					}
				});
			}

			// Get online data
			onlineDataFactory.retrieveItems({'install_name': inst_result.name}).then(function(result) {
				$.each(result, function(i, item){
					$scope.onlinedata.push(new OnlineData(item));
				});
			});
		});
	}

	$scope.changeNodeType = function(currentValue, obj) {

		if (currentValue == 'real') {
			obj.cmpnt_type_name = "";

		} else {
			obj.cmpnt_type_name = "__virtual_device__";
			obj.__beamline__ = "";
			obj.__project__ = "";
			obj.inventory = "";
		}
	};

	$scope.changeNodeTypeInventory = function(currentValue, obj) {

		if (obj.inventory != undefined) {
			obj.cmpnt_type_name = obj.inventory.cmpnt_type_name;
			obj.__node_type__ = $scope.nodeTypeList[2].name;
		}
	};

	$scope.checkInventoryValidity = function(obj) {

		if (obj.inventory != undefined && obj.cmpnt_type_name != obj.inventory.cmpnt_type_name) {
			obj.inventory = undefined;
		}
	};

	$scope.toggleTableRows = function(el, type, index) {
		toggleTableRows(el.target, type + index);
	};

	$scope.goToMap = function(inv, install, id) {
		var newLocation = createRouteUrl({'inventory_id': inv, 'install_name': install, 'search': new Date().getTime()}, "inventory_to_install", entityParameters.inventory_to_install) + "/id/" + id + "/action/retrieve";
		$window.location = newLocation;
	};

	$scope.goToInventory = function(id) {

		var location = createRouteUrl({'vendor_name': '*', 'serial_no': '*', 'cmpnt_type_name': '*', 'search': new Date().getTime()}, "inventory", entityParameters.inventory) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};

	$scope.goToOnlineData = function(name, id) {
		var search = {};
		search.search = new Date().getTime();
		search.install_name = name;

		var location = createRouteUrl(search, "online_data", entityParameters.online_data) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};

	$scope.goToOfflineData = function(name, id) {
		var search = {};
		search.search = new Date().getTime();
		search.inventory_name = name;

		var location = createRouteUrl(search, "offline_data", entityParameters.offline_data) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "install", entityParameters.install) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	// Save or update installRel
	$scope.saveOrUpdateInstallRel = function(element) {

		// Setting installRel
		var installRel = new InstallRel({
			"parent_install": element.name,
			"child_install": element.name,
			"expected_property": JSON.stringify({"__virtual_rel__": "true"})
		});

		// Retrieving installRel
		var installRelPromise = installRelFactory.retrieveItems(installRel);

		// Retrieving installRel, so we can save a new installRelProp if it yet doesn't exist
		installRelPromise.then(function(data) {
			l("Retrieved InstallRel: ");
			l(data);

			// Setting installRel
			installRel = new InstallRel({
				"parent_install": element.name,
				"child_install": element.name,
				"description": "virtual_description",
				"props": JSON.stringify({"__virtual_rel__": "true", "__node_type__": element.__node_type__, "__beamline__": element.__beamline__, "__project__": element.__project__})
			});

			// If this install does not have an installRel yet, save it
			if (isArrayEmpty(data)) {

				// Saving a new InstallRel
				var newInstallRelPromise = installRelFactory.saveItem(installRel);
				

			// Otherwise update it
			} else {

				// Updating a new InstallRel
				var newInstallRelPromise = installRelFactory.updateItem(installRel);
			}	

			newInstallRelPromise.then(function(newInstallRel) {

				l("Saved/Updated installRel: ");
				l(newInstallRel);
			});
		});
	}

	// Save or update InventoryToInstall
	$scope.saveOrUpdateInventoryToInstall = function(element) {

		// Setting InventoryToInstall
		var i2i = new InventoryToInstall({
			"inventory_to_install": undefined,
			"install_name": element.name,
			"inventory_id": undefined//$scope.inventories[element.inventory].id
		});

		// Making a promise
		var i2iPromise = inventoryToInstallFactory.retrieveItems(i2i);

		// Retrieving InventoryToInstall, so we can save/update a InventoryToInstall
		i2iPromise.then(function(data) {
			l("Retrieved InventoryToInstall: ");
			l(data);

			// If InventoryToInstall does not exist for this inventory, save it
			if (isArrayEmpty(data)) {

				// If inventory selected, save it, otherwise do nothing
				if (element.inventory != undefined) {

					// Prepare new i2i
					var newi2i = new InventoryToInstall({
						"inventory_to_install": undefined,
						"install_name": element.name,
						"inventory_id": element.inventory.id
					});

					// Saving a new InventoryToInstall
					$scope.saveInventoryToInstall(inventoryToInstallFactory.saveItem(newi2i));
				}

			// Otherwise delete old one and/or save a new one
			} else {

				//  If we have a selected inventory, first delete old one and install a new one
				if (element.inventory != undefined) {

					// If chosen inventory is different than the current saved one
					if (element.inventory != data[Object.keys(data)[0]].inventory_id) {

						// First delete old i2i
						inventoryToInstallFactory.deleteItem({"inventory_to_install_id": Object.keys(data)[0]}).then(function(resDeleted){
							l("Deleted InventoryToInstall: ");
							l(resDeleted);

							// Prepare new i2i
							var newi2i = new InventoryToInstall({
								"inventory_to_install": undefined,
								"install_name": element.name,
								"inventory_id": element.inventory.id
							});

							// Save new i2i
							$scope.saveInventoryToInstall(inventoryToInstallFactory.saveItem(newi2i));
						});
					}
				} else {
					
					// Delete current i2i
					inventoryToInstallFactory.deleteItem({"inventory_to_install_id": Object.keys(data)[0]}).then(function(resDeleted){
						l("Deleted InventoryToInstall: ");
						l(resDeleted);
					});
				}
			}
		});
	}

	$scope.formatInventory = function(inv) {
		return inv.id + " ( " + inv.cmpnt_type_name + ", " + inv.vendor + " )";
	};

	$scope.saveInventoryToInstall = function(promise) {
		promise.then(function(newInventoryToInstall) {
				l("Saved/Updated InventoryToInstall: ");
				l(newInventoryToInstall);

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
	};

	$scope.deleteInventoryToInstall = function(promise) {
		promise.then(function(newInventoryToInstall) {
			l("Deleted InventoryToInstall: ");
			l(resDeleted);
		});
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new Install(newItem);
		var result = installFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = installFactory.updateItem($scope.element);

			} else if(action === "save") {
				promise = installFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Install item successfully saved!";
				l(data);

				// Performs only on update action
				if (action === 'update') {
					$scope.saveOrUpdateInstallRel($scope.element);
					$scope.saveOrUpdateInventoryToInstall($scope.element);

				// Performs only on save action
				} else if(action === "save") {
					$scope.saveOrUpdateInstallRel($scope.new);
					$scope.saveOrUpdateInventoryToInstall($scope.new);
				}

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInsertionDeviceCtrl', function($scope, $routeParams, $http, $window, InsertionDeviceInfo, InsertionDevice, InventoryToInstall, installFactory, inventoryToInstallFactory, onlineDataFactory, inventoryFactory, Inventory, OnlineData, offlineDataFactory, OfflineData, cmpntTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new InsertionDevice();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InsertionDeviceInfo;

	$scope.types = [];
	$scope.onlinedata = [];
	$scope.offlinedata = [];
	$scope.statusMap = statusArrMap;

	// Retrieve all Component types
	cmpntTypeFactory.retrieveCompntTypes({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.types.push(item.name);
		});
	});

	// Get inventory from the factory if updating
	// if($routeParams.action != "save") {

	// 	installFactory.retrieveItem($routeParams).then(function(inst_result) {
	// 		$scope.element = inst_result;
	// 		$scope.element.old_name = inst_result.name;

	// 		if ($routeParams.action == "retrieve") {
	// 			$scope.map = {};

	// 			inventoryToInstallFactory.retrieveItems({'install_name': $scope.element.name, 'inv_name': '*'}).then(function(result) {
	// 				var keys = Object.keys(result);

	// 				if(keys.length > 0) {
	// 					$scope.map = result[keys[0]];

	// 					// Get offline data
	// 					inventoryFactory.retrieveItems({'name': $scope.map.inventoryname}).then(function(result) {
	// 						l(result);
	// 						var keys = Object.keys(result);
	// 						$scope.inventory = new Inventory(result[keys[0]]);
	// 					});

	// 					// Get offline data
	// 					offlineDataFactory.retrieveItems({'inventory_name': $scope.map.inventoryname}).then(function(result) {

	// 						$.each(result, function(i, item){
	// 							$scope.offlinedata.push(new OfflineData(item));
	// 						});
	// 					});
	// 				}
	// 			});
	// 		}

	// 		// Get online data
	// 		onlineDataFactory.retrieveItems({'install_name': inst_result.name}).then(function(result) {
	// 			$.each(result, function(i, item){
	// 				$scope.onlinedata.push(new OnlineData(item));
	// 			});
	// 		});
	// 	});
	// }

	$scope.toggleTableRows = function(el, type, index) {
		l(el);
		toggleTableRows(el.target, type + index);
	};

	$scope.goToMap = function(inv, install, id) {
		var newLocation = createRouteUrl({'inv_name': inv, 'install_name': install, 'search': new Date().getTime()}, "inventory_to_install", ["inv_name", "install_name"]) + "/id/" + id + "/action/retrieve";
		$window.location = newLocation;
	};

	$scope.goToInventory = function(id) {

		var location = createRouteUrl({'name': '*', 'search': new Date().getTime()}, "inventory", ["name"]) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};

	$scope.goToOnlineData = function(name, id) {
		var search = {};
		search.search = new Date().getTime();
		search.install_name = name;

		var location = createRouteUrl(search, "online_data", ["install_name", "description", "date", "status"]) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};

	$scope.goToOfflineData = function(name, id) {
		var search = {};
		search.search = new Date().getTime();
		search.inventory_name = name;

		var location = createRouteUrl(search, "offline_data", ["inventory_name", "description", "date", "gap", "phase1", "phase2", "phase3", "phase4", "phasemode", "polarmode", "status", "method_name"]) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "install", ["name", "cmpnt_type", "description", "coordinatecenter"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new Install(newItem);
		var result = installFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = installFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = installFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Install item successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInventoryToInstallCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[4];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory_to_install", entityParameters.inventory_to_install) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory_to_install", entityParameters.inventory_to_install) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listInventoryToInstallCtrl', function($scope, $routeParams, $http, $window, InventoryToInstallInfo, InventoryToInstall, inventoryToInstallFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = InventoryToInstallInfo;
	var previousItem;
	$scope.items = [];

	inventoryToInstallFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new InventoryToInstall(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "inventory_to_install", entityParameters.inventory_to_install) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.inventory_id = item.inventory_id;
		$routeParams.install_name = item.install_name;

		var location = createRouteUrl($routeParams, "inventory_to_install", entityParameters.inventory_to_install) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInventoryToInstallCtrl', function($scope, $modal, $routeParams, $http, $window, InventoryToInstallInfo, InventoryToInstall, inventoryToInstallFactory, installFactory, inventoryFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new InventoryToInstall();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InventoryToInstallInfo;

	$scope.inv = [];
	$scope.inst = [];

	// Retrieve all Inventory items
	inventoryFactory.retrieveItems({'serial_no': '*', 'cmpnt_type_name': '*', 'vendor_name': '*'}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inv.push(item.id);
		});
	});

	// Retrieve all Install items
	installFactory.retrieveItems({'name': '*'}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inst.push(item.name);
		});
	});

	// Get inventory to install from the factory if updating
	if($routeParams.action != "save") {

		inventoryToInstallFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "inventory_to_install", entityParameters.inventory_to_install) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.deleteItem = function(localI2iId) {
		var modalInstance = $modal.open({
			templateUrl: 'modal/delete_inventory_to_install.html',
			controller: 'deleteInventoryToInstallCtrl',
			resolve: {
				i2iId: function() {
					return localI2iId;
				}
			}
		});
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new InventoryToInstall(newItem);
		l(item);
		var result = inventoryToInstallFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = inventoryToInstallFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = inventoryToInstallFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Inventory to install map item successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Delete inventory to install rel
 */
app.controller('deleteInventoryToInstallCtrl', function($scope, $routeParams, $modalInstance, inventoryToInstallFactory, $window, i2iId) {
	$scope.alert = {};
	$scope.showYesButton = true;
	$scope.showCancelButton = true;
	$scope.showFinishButton = false;
	var types = [];
	$scope.message = "Device will be uninstalled and all its Online data will be deleted. Are you sure you want to continue?";

	$scope.closeAlert = function() {
		$scope.alert.show = false;
	};

	$scope.ok = function() {
		$scope.alert.show = false;

		inventoryToInstallFactory.deleteItem({'inventory_to_install_id': i2iId}).then(function(data) {
			$scope.alert.show = true;
			$scope.alert.success = true;
			$scope.alert.title = "Success!";
			$scope.alert.body = "Device successfully uninstalled!";
			$scope.showYesButton = false;
			$scope.showCancelButton = false;
			$scope.showFinishButton = true;

		}, function(error) {
			$scope.alert.show = true;
			$scope.alert.success = false;
			$scope.alert.title = "Error!";
			$scope.alert.body = error;
		});
	};

	$scope.cancel = function() {
		$modalInstance.dismiss('cancel');
	};

	$scope.finish = function() {
		$routeParams.search = new Date().getTime();
		$routeParams.inv_name = "*";
		$routeParams.install_name = "*";
		var newLocation = createRouteUrl($routeParams, "inventory_to_install", entityParameters.inventory_to_install) + "/list";
		$window.location = newLocation;
		$modalInstance.dismiss('cancel');
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInstallRelCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[5];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install_rel", ["description", "parent_install"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {

		// Set description if is not set
		if (search.description === undefined || search.description === "") {
			search.description = "*";
		}

		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install_rel", ["description", "parent_install"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.showTree = function(search) {
		search.description = "";
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install_rel", ["description", "parent_install"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listInstallRelCtrl', function($scope, $routeParams, $http, $window, $sce, InstallRelInfo, InstallRel, installRelFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = InstallRelInfo;
	var previousItem;
	$scope.items = [];
	$scope.breadcrumbs = [];
	$scope.currentItem = $routeParams.parent_install;

	$scope.tree = {};
	$scope.treeRaw = {};
	$scope.showTree = false;
	$scope.currentNode = "/";

	if ($routeParams.description === undefined) {
		$scope.showTree = true;

		var installName = $routeParams.parent_install;

		if(installName === undefined) {
			installName = "root";
		}

		installRelFactory.retrieveTree({'install_name': 'root'}).then(function(result) {

			$scope.breadcrumbs.push($scope.currentNode);
			l($scope.breadcrumbs);
			$scope.treeRaw = result;

			$scope.tree = drawDataTree("", result, result[$scope.currentNode], 0);
		});

	} else {

		installRelFactory.retrieveItems($routeParams).then(function(result) {

			$.each(result, function(i, item){

				// Build customized object
				var newItem = new InstallRel(item);

				// Alternate background colors
				if(i%2 === 0) {
					newItem.color = "bg_dark";

				} else {
					newItem.color = "bg_light";
				}

				$scope.items.push(newItem);
			});
			$scope.items.reverse();
		});
	}

	// Show add form in the right pane
	$scope.addItem = function(parent) {

		if (parent !== undefined) {
			$routeParams.parent_install = parent;
		}

		l(parent);

		var location = createRouteUrl($routeParams, "install_rel", ["description", "parent_install"]) + "/id/new/action/save";
		l(location);
		$window.location = location;
	};

	$scope.showDetailsRaw = function(itemName) {
		$scope.showDetails($scope.treeRaw[itemName].obj);
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;
		l(item);

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;

		var location = createRouteUrl($routeParams, "install_rel", ["description", "parent_install"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};

	$scope.walkThroughTree = function(parent) {
		var parentNodeName = parent;
		$scope.breadcrumbs = [];

		while($scope.treeRaw[parentNodeName].parent !== undefined) {
			$scope.breadcrumbs.push($scope.treeRaw[parentNodeName].name);
			parentNodeName = $scope.treeRaw[parentNodeName].parent;
		}
		$scope.breadcrumbs.push("/");

		// Reverse array
		$scope.breadcrumbs = $scope.breadcrumbs.reverse();

		$scope.currentNode = parent;
		$scope.tree = drawDataTree("", $scope.treeRaw, $scope.treeRaw[$scope.currentNode], 0);
	};

	// Show details when user selects item from a list
	$scope.showTreeNodeDetails = function(id) {

		var location = createRouteUrl($routeParams, "install_rel", ["description", "parent_install"]) + "/id/" + id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInstallRelCtrl', function($scope, $modal, $routeParams, $http, $window, InstallRelInfo, InstallRel, installRelFactory, installRelTypeFactory, EntityError, installFactory){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new InstallRel();
	$scope.new.prop_keys = [];
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InstallRelInfo;
	$scope.installs = [];
	$scope.parentDisabled = false;

	$scope.types = [];
	$scope.props = [];

	// Get install
	installFactory.retrieveItems({'name': '*'}).then(function(result) {
		$.each(result, function(i, item){

			$scope.installs.push(item.name);
		});

		l($scope.isntalls);
	});

	installRelTypeFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item) {
			$scope.props.push(item.name);
		});
	});

	// Append new property
	$scope.appendProperty = function() {

		if($routeParams.action === "save"){
			$scope.new.prop_keys.push({'name': '', 'value': ''});

		} else {
			$scope.element.prop_keys.push({'name': '', 'value': ''});
		}
	};

	// Property name dropdown has changed
	$scope.changePropertyName = function() {
		l($scope.props);
	};

	// Get install rel type from the factory if updating
	if($routeParams.action != "save") {

		installRelFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.child_install = result.childname;
			$scope.element.parent_install = result.parentname;
			l($scope.element);
		});

	} else {
		$scope.new.parent_install = $routeParams.parent_install;
		$scope.new.parentname = $routeParams.parent_install;
	}

	// Disable parent if parent is set in url
	if ($routeParams.parent_install !== undefined && $routeParams.parent_install !== "") {
		$scope.parentDisabled = true;
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "install_rel", ["description", "parent_install"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.deleteItem = function(localParent, localChild) {
		var modalInstance = $modal.open({
			templateUrl: 'modal/delete_install_rel.html',
			controller: 'deleteInstallRelCtrl',
			resolve: {
				parent: function() {
					return localParent;
				},
				child: function() {
					return localChild;
				}
			}
		});
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new InstallRel(newItem);
		var result = installRelFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {

				$.each($scope.element.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.element.props = JSON.stringify(propsObject);

				promise = installRelFactory.updateItem($scope.element);

			} else if(action == "save") {

				$.each($scope.new.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.new.props = JSON.stringify(propsObject);

				promise = installRelFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Install rel type successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Delete install rel
 */
app.controller('deleteInstallRelCtrl', function($scope, $routeParams, $modalInstance, installRelFactory, $window, parent, child) {
	$scope.alert = {};
	$scope.showYesButton = true;
	$scope.showCancelButton = true;
	$scope.showFinishButton = false;
	var types = [];
	$scope.message = "This relationship and all its children will be deleted. Are you sure you want to continue?";

	$scope.closeAlert = function() {
		$scope.alert.show = false;
	};

	$scope.ok = function() {
		$scope.alert.show = false;

		installRelFactory.deleteItem({'parent_install': parent, 'child_install': child}).then(function(data) {
			$scope.alert.show = true;
			$scope.alert.success = true;
			$scope.alert.title = "Success!";
			$scope.alert.body = "Install rel successfully deleted!";
			$scope.showYesButton = false;
			$scope.showCancelButton = false;
			$scope.showFinishButton = true;

		}, function(error) {
			$scope.alert.show = true;
			$scope.alert.success = false;
			$scope.alert.title = "Error!";
			$scope.alert.body = error;
		});
	};

	$scope.cancel = function() {
		$modalInstance.dismiss('cancel');
	};

	$scope.finish = function() {
		$routeParams.search = new Date().getTime();
		$routeParams.description = "*";
		$routeParams.parent_install = "";
		var newLocation = createRouteUrl($routeParams, "install_rel", ["description", "parent_install"]) + "/list";
		$window.location = newLocation;
		$modalInstance.dismiss('cancel');
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInstallRelTypeCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[6];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install_rel_type", ["name"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install_rel_type", ["name"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listInstallRelTypeCtrl', function($scope, $routeParams, $http, $window, InstallRelTypeInfo, InstallRelType, installRelTypeFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = InstallRelTypeInfo;
	var previousItem;
	$scope.items = [];

	installRelTypeFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new InstallRelType(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "install_rel_type", ["name"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;

		var location = createRouteUrl($routeParams, "install_rel_type", ["name"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInstallRelTypeCtrl', function($scope, $routeParams, $http, $window, InstallRelTypeInfo, InstallRelType, installRelTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new InstallRelType();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InstallRelTypeInfo;

	// Get install rel type from the factory if updating
	if($routeParams.action != "save") {

		installRelTypeFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "install_rel_type", ["name"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new InstallRelType(newItem);
		var result = installRelTypeFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = installRelTypeFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = installRelTypeFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Install rel type successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchDataMethodCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[7];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "data_method", ["name", "description"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "data_method", ["name", "description"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listDataMethodCtrl', function($scope, $routeParams, $http, $window, DataMethodInfo, DataMethod, dataMethodFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = DataMethodInfo;
	var previousItem;
	$scope.items = [];

	dataMethodFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new DataMethod(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.name = item.name;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showDataMethodCtrl', function($scope, $routeParams, $http, $window, DataMethodInfo, DataMethod, dataMethodFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new DataMethod();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = DataMethodInfo;

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		dataMethodFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new DataMethod(newItem);
		var result = dataMethodFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = dataMethodFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = dataMethodFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Data method item successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchOfflineDataCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.statusArr2 = statusArr;
	$scope.statusArr2.push({name:"", value:"-"});

	$scope.search.type = dataTypes.others[8];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "offline_data", entityParameters.offline_data) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();

		if(search.date_from && search.date_to) {search.date='["' + search.date_from + '","' + search.date_to + '"]';} else {search.date = undefined;}
		if(search.gap_from && search.gap_to) {search.gap="[" + search.gap_from + "," + search.gap_to + "]";} else {search.gap = undefined;}
		if(search.phase1_from && search.phase1_to) {search.phase1="[" + search.phase1_from + "," + search.phase1_to + "]";} else {search.phase1 = undefined;}
		if(search.phase2_from && search.phase2_to) {search.phase2="[" + search.phase2_from + "," + search.phase2_to + "]";} else {search.phase2 = undefined;}
		if(search.phase3_from && search.phase3_to) {search.phase3="[" + search.phase3_from + "," + search.phase3_to + "]";} else {search.phase3 = undefined;}
		if(search.phase4_from && search.phase4_to) {search.phase4="[" + search.phase4_from + "," + search.phase4_to + "]";} else {search.phase4 = undefined;}
		if(search.phasemode_from && search.phasemode_to) {search.phasemode="[" + search.phasemode_from + "," + search.phasemode_to + "]";} else {search.phasemode = undefined;}
		if(search.polarmode_from && search.polarmode_to) {search.polarmode="[" + search.polarmode_from + "," + search.polarmode_to + "]";} else {search.polarmode = undefined;}

		var newLocation = createRouteUrl(search, "offline_data", entityParameters.offline_data) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listOfflineDataCtrl', function($scope, $routeParams, $http, $window, OfflineDataInfo, OfflineData, offlineDataFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = OfflineDataInfo;
	var previousItem;
	$scope.items = [];

	offlineDataFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new OfflineData(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "offline_data", entityParameters.offline_data) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.inventory_id = item.inventory_id;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, "offline_data", entityParameters.offline_data) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showOfflineDataCtrl', function($scope, $modal, $routeParams, $http, $window, OfflineDataInfo, OfflineData, Inventory, offlineDataFactory, inventoryFactory, dataMethodFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new OfflineData();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = OfflineDataInfo;
	$scope.uploadFileName = "";
	$scope.statusArr = statusArr;
	uploadData = undefined;

	$scope.inventories = [];
	$scope.inventoriesMap = {};
	$scope.methods = [];

	// Retrieve all Inventories
	inventoryFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inventories.push(item.id);
			$scope.inventoriesMap[item.id] = new Inventory(item);
		});

		if($routeParams.action == "retrieve") {
			$scope.inventory = $scope.inventoriesMap[$routeParams.inventory_id];
		}
	});

	// Retrieve all Component types
	dataMethodFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.methods.push(item.name);
		});
	});

	$scope.options = {
		url: serviceurl + "/saverawdata/",
		maxFileSize: 5000000,
		acceptFileTypes: /(\.|\/)(gif|jpe?g|png|txt)$/i
	};

	$scope.$on('fileuploadadd', function(e, data) {
		var id = data.fileInput.context.id;
		$scope.uploadFileName = data.files[0].name;

		uploadData = data;
		if ($scope.error != undefined) {
			delete $scope.error.data_id;
		}
	});

	$scope.$on('fileuploaddone', function(e, data) {
		l(data.jqXHR.responseText);
		var response = data.jqXHR.responseText;
		l(e);

		if($scope.action === "update") {
			$scope.element.data_id = JSON.parse(response).id;

		} else if($scope.action == "save") {
			$scope.new.data_id = JSON.parse(response).id;
		}

		saveData($scope, offlineDataFactory);
	});

	$scope.$on('fileuploadfail', function(e, data) {
		l(data);
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		offlineDataFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.offline_data_id = result.id;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "offline_data", entityParameters.offline_data) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	// Delete offline data
	$scope.deleteItem = function(localOfflineId) {
		var modalInstance = $modal.open({
			templateUrl: 'modal/delete_data.html',
			controller: 'deleteOfflineDataCtrl',
			resolve: {
				offlineId: function() {
					return localOfflineId;
				},
				url: function() {
					return "offline_data";
				}
			}
		});
	};

	$scope.saveItem = function(action) {

		if (uploadData === undefined && action === "save") {
			$scope.error.data_id = "Raw data field is mandatory!";

		} else if (uploadData === undefined && action !== "save") {
			saveData($scope, offlineDataFactory);

		} else {
			uploadData.submit();
		}
	};

	$scope.downloadScript = function(element) {
		download(element.script_name, element.script, true);
	};

	$scope.downloadRawData = function(element) {
		// Retrieve raw file
		offlineDataFactory.retrieveRawFile(element.data_id).then(function(result) {
			l(result);
			download(element.data_file_name, result[element.data_id].data, result[element.data_id].is_ascii);
		});
	};
});

/*
 * Delete offline data
 */
app.controller('deleteOfflineDataCtrl', function($scope, $routeParams, $modalInstance, offlineDataFactory, $window, offlineId, url) {
	$scope.alert = {};
	$scope.showYesButton = true;
	$scope.showCancelButton = true;
	$scope.showFinishButton = false;
	var types = [];
	$scope.title = "Delete offline data";
	$scope.message = "Offline data will be deleted. Are you sure you want to continue?";

	$scope.closeAlert = function() {
		$scope.alert.show = false;
	};

	$scope.ok = function() {
		$scope.alert.show = false;

		offlineDataFactory.deleteItem({'offline_data_id': offlineId}).then(function(data) {
			$scope.alert.show = true;
			$scope.alert.success = true;
			$scope.alert.title = "Success!";
			$scope.alert.body = "Offline data successfully deleted!";
			$scope.showYesButton = false;
			$scope.showCancelButton = false;
			$scope.showFinishButton = true;

		}, function(error) {
			$scope.alert.show = true;
			$scope.alert.success = false;
			$scope.alert.title = "Error!";
			$scope.alert.body = error;
		});
	};

	$scope.cancel = function() {
		$modalInstance.dismiss('cancel');
	};

	$scope.finish = function() {
		$routeParams.search = new Date().getTime();
		$routeParams.description = "*";
		$routeParams.parent_install = "";
		var newLocation = createRouteUrl($routeParams, url, entityParameters.offline_data) + "/list";
		$window.location = newLocation;
		$modalInstance.dismiss('cancel');
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchOfflineDataInstallCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.statusArr2 = statusArr;
	$scope.statusArr2.push({name:"", value:"-"});

	$scope.search.type = dataTypes.others[9];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "offline_data_install", entityParameters.offline_data_install) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();

		if(search.date_from && search.date_to) {search.date='["' + search.date_from + '","' + search.date_to + '"]';} else {search.date = undefined;}
		if(search.gap_from && search.gap_to) {search.gap="[" + search.gap_from + "," + search.gap_to + "]";} else {search.gap = undefined;}
		if(search.phase1_from && search.phase1_to) {search.phase1="[" + search.phase1_from + "," + search.phase1_to + "]";} else {search.phase1 = undefined;}
		if(search.phase2_from && search.phase2_to) {search.phase2="[" + search.phase2_from + "," + search.phase2_to + "]";} else {search.phase2 = undefined;}
		if(search.phase3_from && search.phase3_to) {search.phase3="[" + search.phase3_from + "," + search.phase3_to + "]";} else {search.phase3 = undefined;}
		if(search.phase4_from && search.phase4_to) {search.phase4="[" + search.phase4_from + "," + search.phase4_to + "]";} else {search.phase4 = undefined;}
		if(search.phasemode_from && search.phasemode_to) {search.phasemode="[" + search.phasemode_from + "," + search.phasemode_to + "]";} else {search.phasemode = undefined;}
		if(search.polarmode_from && search.polarmode_to) {search.polarmode="[" + search.polarmode_from + "," + search.polarmode_to + "]";} else {search.polarmode = undefined;}

		var newLocation = createRouteUrl(search, "offline_data_install", entityParameters.offline_data_install) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listOfflineDataInstallCtrl', function($scope, $routeParams, $http, $window, $location, OfflineDataInstallInfo, OfflineDataInstall, offlineDataInstallFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = OfflineDataInstallInfo;
	var previousItem;
	$scope.items = [];

	var pathParts = $location.path().split('/');
	var type = pathParts[1];

	// Append second part of the path
	if (type === "beamline" || type === "installation") {
		type += "/" + pathParts[2];
	}

	offlineDataInstallFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new OfflineDataInstall(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, type, entityParameters.offline_data_install) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.install_name = item.install_name;
		$routeParams.inventory_id = item.inventory_id;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, type, entityParameters.offline_data_install) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showOfflineDataInstallCtrl', function($scope, $modal, $routeParams, $location, $http, $window, OfflineDataInstallInfo, OfflineDataInstall, offlineDataInstallFactory, Inventory, offlineDataFactory, inventoryFactory, dataMethodFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new OfflineDataInstall();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = OfflineDataInstallInfo;
	$scope.uploadFileName = "";
	$scope.statusArr = statusArr;
	$scope.inventory = {};
	uploadData = undefined;

	$scope.inventories = [];
	$scope.inventoriesMap = {};
	$scope.methods = [];

	var pathParts = $location.path().split('/');
	var type = pathParts[1];

	// Append second part of the path
	if (type === "beamline" || type === "installation") {
		type += "/" + pathParts[2];
	}

	// Retrieve all Inventories
	inventoryFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inventories.push(item.id);
			$scope.inventoriesMap[item.id] = new Inventory(item);
		});

		if($routeParams.action == "retrieve") {
			$scope.inventory = $scope.inventoriesMap[$routeParams.inventory_id];
		}
	});

	// Retrieve all Component types
	dataMethodFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.methods.push(item.name);
		});
	});

	$scope.options = {
		url: serviceurl + "/saverawdata/",
		maxFileSize: 5000000,
		acceptFileTypes: /(\.|\/)(gif|jpe?g|png|txt)$/i
	};

	$scope.$on('fileuploadadd', function(e, data) {
		var id = data.fileInput.context.id;
		$scope.uploadFileName = data.files[0].name;

		uploadData = data;
		if ($scope.error != undefined) {
			delete $scope.error.data_id;
		}
	});

	$scope.$on('fileuploaddone', function(e, data) {
		l(data.jqXHR.responseText);
		var response = data.jqXHR.responseText;
		l(e);

		if($scope.action === "update") {
			$scope.element.data_id = JSON.parse(response).id;

		} else if($scope.action == "save") {
			$scope.new.data_id = JSON.parse(response).id;
		}

		saveData($scope, offlineDataFactory);
	});

	$scope.$on('fileuploadfail', function(e, data) {
		l(data);
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		offlineDataInstallFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.offline_data_id = result.id;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, type, entityParameters.offline_data_install) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	// Delete offline data
	$scope.deleteItem = function(localOfflineId) {
		var modalInstance = $modal.open({
			templateUrl: 'modal/delete_data.html',
			controller: 'deleteOfflineDataInstallCtrl',
			resolve: {
				offlineId: function() {
					return localOfflineId;
				},
				url: function() {
					return type;
				}
			}
		});
	};

	$scope.saveItem = function(action) {

		if (uploadData === undefined && action === "save") {
			$scope.error.data_id = "Raw data field is mandatory!";

		} else if (uploadData === undefined && action !== "save") {
			saveData($scope, offlineDataFactory);

		} else {
			uploadData.submit();
		}
	};

	$scope.downloadScript = function(element) {
		download(element.script_name, element.script, true);
	};

	$scope.downloadRawData = function(element) {
		// Retrieve raw file
		offlineDataFactory.retrieveRawFile(element.data_id).then(function(result) {
			l(result);
			download(element.data_file_name, result[element.data_id].data, result[element.data_id].is_ascii);
		});
	};
});

/*
 * Delete offline data
 */
app.controller('deleteOfflineDataInstallCtrl', function($scope, $routeParams, $modalInstance, offlineDataFactory, $window, offlineId, url) {
	$scope.alert = {};
	$scope.showYesButton = true;
	$scope.showCancelButton = true;
	$scope.showFinishButton = false;
	var types = [];
	$scope.title = "Delete offline data";
	$scope.message = "Offline data will be deleted. Are you sure you want to continue?";

	$scope.closeAlert = function() {
		$scope.alert.show = false;
	};

	$scope.ok = function() {
		$scope.alert.show = false;

		offlineDataFactory.deleteItem({'offline_data_id': offlineId}).then(function(data) {
			$scope.alert.show = true;
			$scope.alert.success = true;
			$scope.alert.title = "Success!";
			$scope.alert.body = "Offline data successfully deleted!";
			$scope.showYesButton = false;
			$scope.showCancelButton = false;
			$scope.showFinishButton = true;

		}, function(error) {
			$scope.alert.show = true;
			$scope.alert.success = false;
			$scope.alert.title = "Error!";
			$scope.alert.body = error;
		});
	};

	$scope.cancel = function() {
		$modalInstance.dismiss('cancel');
	};

	$scope.finish = function() {
		$routeParams.search = new Date().getTime();
		$routeParams.description = "*";
		$routeParams.parent_install = "";
		var newLocation = createRouteUrl($routeParams, url, entityParameters.offline_data_install) + "/list";
		$window.location = newLocation;
		$modalInstance.dismiss('cancel');
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchOnlineDataCtrl', function($scope, $window, $routeParams, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.statusArr2 = statusArr;
	$scope.statusArr2.push({name:"", value:"-"});

	$scope.search.type = dataTypes.others[10];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "online_data", ["install_name", "description", "date", "status"]) + "/list";
		$window.location = newLocation;
	}

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		if(search.date_from && search.date_to) {search.date='["' + search.date_from + '","' + search.date_to + '"]';} else {search.date = undefined;}

		var newLocation = createRouteUrl(search, "online_data", ["install_name", "description", "date", "status"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listOnlineDataCtrl', function($scope, $location, $routeParams, $http, $window, OnlineDataInfo, OnlineData, onlineDataFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = OnlineDataInfo;
	var previousItem;
	$scope.items = [];

	var pathParts = $location.path().split('/');
	var type = pathParts[1];

	// Append second part of the path
	if (type === "beamline" || type === "installation") {
		type += "/" + pathParts[2];
	}

	onlineDataFactory.retrieveItems($routeParams).then(function(result) {

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new OnlineData(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, type, ["install_name", "description", "date", "status"]) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.install_name = item.install_name;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, type, ["install_name", "description", "date", "status"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showOnlineDataCtrl', function($scope, $modal, $routeParams, $http, $window, $location, OnlineDataInfo, Install, OnlineData, onlineDataFactory, EntityError, installFactory, offlineDataFactory){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new OnlineData();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = OnlineDataInfo;
	$scope.uploadFileName = "";
	$scope.statusArr = statusArr;

	$scope.installs = [];
	$scope.installMap = {};
	$scope.uploadData = undefined;
	$scope.files = [];
	$scope.uploadDoneCounter = 0;

	var pathParts = $location.path().split('/');
	var type = pathParts[1];

	// Append second part of the path
	if (type === "beamline" || type === "installation") {
		type += "/" + pathParts[2];
	}

	// Retrieve all Installs
	installFactory.retrieveItems({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.installs.push(item.name);
			$scope.installMap[item.name] = new Install(item);
		});

		if ($routeParams.action == "retrieve") {
			$scope.install = $scope.installMap[$routeParams.install_name];
		}
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		onlineDataFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.online_data_id = result.id;
		});
	}

	// Append new file to the array of uploaded files
	$scope.appendFile = function(file) {
		var fileOnThisSpotAlreadyExists = false;

		if($scope.files.length === 0) {
			$scope.files.push(file);

		} else {

			$.each($scope.files, function(i, existingFile) {

				// Replace file
				if(file.fileId === existingFile.fileId) {
					$scope.files[i] = file;
					fileOnThisSpotAlreadyExists = true;
				}
			});

			// Append file
			if(!fileOnThisSpotAlreadyExists) {
				$scope.files.push(file);
			}
		}

	};

	$scope.options = {
		url: serviceurl + "/saveonlinedata/",
		maxFileSize: 5000000,
		acceptFileTypes: /(\.|\/)(gif|jpe?g|png|txt)$/i
	};

	$scope.$on('fileuploadadd', function(e, data) {
		var id = data.fileInput.context.id;
		l(id);
		l(data);

		if($scope.uploadData === undefined) {
			$scope.uploadData = {};
		}

		if($scope.action === "update") {
			data.url = serviceurl + "/updateonlinedata/";
		}

		if(id === "rawFile") {
			$scope.uploadFileName = data.files[0].name;
			data.fileId = "rawFile";
			data.files[0].fileId = "rawFile";
			$scope.uploadData.rawFile = data;

			if($scope.action === "update") {
				$scope.element.feedforward_file_name = $scope.uploadFileName;

			} else if($scope.action == "save") {
				$scope.new.feedforward_file_name = $scope.uploadFileName;
			}

		} else {
			$scope.uploadFileName2 = data.files[0].name;
			data.fileId = "rawFile2";
			data.files[0].fileId = "rawFile2";
			$scope.uploadData.rawFile2 = data;
		}

		l($scope.uploadData);
	});

	$scope.$on('fileuploaddone', function(e, data) {
		l(data.jqXHR.responseText);
		var response = data.jqXHR.responseText;
		l(e);
		l(data);

		$scope.alert.show = true;
		$scope.alert.success = true;
		$scope.alert.title = "Success!";
		$scope.alert.body = "Data successfully saved!";
	});

	$scope.$on('fileuploadfail', function(e, data) {
		l(data);
		$scope.alert.show = true;
		$scope.alert.success = false;
		$scope.alert.title = "Error!";
		$scope.alert.body = data;
	});

	$scope.download = function(url) {
		$window.location.href = serviceurlraw + url;
	};

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, type, ["install_name", "description", "date", "status"]) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.deleteItem = function(localOnlineId) {
		var modalInstance = $modal.open({
			templateUrl: 'modal/delete_data.html',
			controller: 'deleteOnlineDataCtrl',
			resolve: {
				onlineId: function() {
					return localOnlineId;
				},
				url: function() {
					return type;
				}
			}
		});
	};

	$scope.saveItem = function(action) {

		if($scope.action === "update") {
			result = onlineDataFactory.checkItem($scope.element);

		} else if($scope.action == "save") {
			l($scope.new);
			result = onlineDataFactory.checkItem($scope.new);
			l(result);
		}

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {

			if ($scope.uploadData === undefined && action === "save") {
				l("save");
				l($scope.items);
				saveData($scope, onlineDataFactory);

			} else if ($scope.uploadData === undefined && action !== "save") {
				l("asd");
				l($scope.items);
				saveData($scope, onlineDataFactory);

			} else {

				$.each($scope.uploadData, function(fileId, file) {
					file.submit();
				});
			}
		}
	};

	$scope.downloadRawData = function(element) {
		l(element);
		download(element.feedforward_file_name, element.feedforward_data, false);
	};
});

/*
 * Delete online data
 */
app.controller('deleteOnlineDataCtrl', function($scope, $routeParams, $modalInstance, onlineDataFactory, $window, onlineId, url) {
	$scope.alert = {};
	$scope.showYesButton = true;
	$scope.showCancelButton = true;
	$scope.showFinishButton = false;
	var types = [];
	$scope.title = "Delete online data";
	$scope.message = "Online data will be deleted. Are you sure you want to continue?";

	$scope.closeAlert = function() {
		$scope.alert.show = false;
	};

	$scope.ok = function() {
		$scope.alert.show = false;

		onlineDataFactory.deleteItem({'online_data_id': onlineId}).then(function(data) {
			$scope.alert.show = true;
			$scope.alert.success = true;
			$scope.alert.title = "Success!";
			$scope.alert.body = "Online data successfully deleted!";
			$scope.showYesButton = false;
			$scope.showCancelButton = false;
			$scope.showFinishButton = true;

		}, function(error) {
			$scope.alert.show = true;
			$scope.alert.success = false;
			$scope.alert.title = "Error!";
			$scope.alert.body = error;
		});
	};

	$scope.cancel = function() {
		$modalInstance.dismiss('cancel');
	};

	$scope.finish = function() {
		$routeParams.search = new Date().getTime();
		$routeParams.description = "*";
		$routeParams.parent_install = "";
		var newLocation = createRouteUrl($routeParams, url, ["install_name", "description", "date", "status"]) + "/list";
		$window.location = newLocation;
		$modalInstance.dismiss('cancel');
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchBeamlineCtrl', function($scope, $location, $window, $routeParams, installRelFactory, navigationFactory){
	$scope.style.middle_class = "container-scroll-middle";

	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.display = "online_data";

	$scope.search.type = dataTypes.hierarchy[0];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	var pathParts = $location.path().split('/');

	if (pathParts.length > 2) {
		$scope.display = pathParts[2];
	}

	installRelFactory.retrieveTree({'install_name': 'Beamline project'}).then(function(result) {

		l(result);
		$scope.tree = drawDataTree2("", result, 0);
	});

	$scope.listData = function(install_name) {
		l(install_name);
		$scope.searchForItem({'install_name': install_name});
	};

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		search.description = "*";

		var params = [];

		if ($scope.display === "offline_data") {
			params = ["install_name", "inventory_name", "description", "date", "gap", "phase1", "phase2", "phase3", "phase4", "phasemode", "polarmode", "status", "method_name"];

		} else if ($scope.display === "online_data") {
			params = ["install_name", "description", "date", "status"];
		}

		var newLocation = createRouteUrl(search, "beamline/" + $scope.display, params) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInstallationCtrl', function($scope, $location, $window, $routeParams, installRelFactory, navigationFactory){
	$scope.style.middle_class = "container-scroll-middle";

	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.display = "online_data";

	$scope.search.type = dataTypes.hierarchy[1];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	navigationFactory.setView($scope.search.type);

	var pathParts = $location.path().split('/');

	if (pathParts.length > 2) {
		$scope.display = pathParts[2];
	}

	installRelFactory.retrieveTree({'install_name': 'Device geometric layout'}).then(function(result) {

		l(result);
		$scope.tree = drawDataTree2("", result, 0);
	});

	$scope.listData = function(install_name) {
		l(install_name);
		$scope.searchForItem({'install_name': install_name});
	};

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		search.description = "*";

		var params = [];

		if ($scope.display === "offline_data") {
			params = ["install_name", "inventory_name", "description", "date", "gap", "phase1", "phase2", "phase3", "phase4", "phasemode", "polarmode", "status", "method_name"];

		} else if ($scope.display === "online_data") {
			params = ["install_name", "description", "date", "status"];
		}

		var newLocation = createRouteUrl(search, "installation/" + $scope.display, params) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchRotCoilDataCtrl', function($scope, $window, $routeParams, inventoryFactory, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[11];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	$scope.inv = [];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "rot_coil_data", entityParameters.rot_coil_data) + "/list";
		$window.location = newLocation;
	}

	// Retrieve all Inventory items
	inventoryFactory.retrieveItems({'cmpnt_type_name': '*', 'serial_no': '*', 'vendor_name': '*'}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inv.push(item.id);
		});
	});

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "rot_coil_data", entityParameters.rot_coil_data) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listRotCoilDataCtrl', function($scope, $routeParams, $http, $window, inventoryFactory, RotCoilDataInfo, RotCoilData, rotCoilDataFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = RotCoilDataInfo;
	var previousItem;
	$scope.items = [];
	$scope.invMap = {};

	rotCoilDataFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new RotCoilData(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "rot_coil_data", entityParameters.rot_coil_data) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.inventory_id = item.inventory_id;

		var location = createRouteUrl($routeParams, "rot_coil_data", entityParameters.rot_coil_data) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showRotCoilDataCtrl', function($scope, $routeParams, $http, $window, RotCoilDataInfo, RotCoilData, rotCoilDataFactory, inventoryFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new RotCoilData();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = RotCoilDataInfo;

	$scope.inv = [];

	// Retrieve all Inventory items
	inventoryFactory.retrieveItems({'cmpnt_type_name': '*', 'serial_no': '*', 'vendor_name': '*'}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inv.push(item.id);
		});
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		rotCoilDataFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.rot_coil_data_id = result.id;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "rot_coil_data", entityParameters.rot_coil_data) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new RotCoilData(newItem);
		var result = rotCoilDataFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = rotCoilDataFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = rotCoilDataFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Rot coil data item successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchHallProbeDataCtrl', function($scope, $window, $routeParams, inventoryFactory, navigationFactory){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.masterTypes = masterTypes;
	$scope.search.type = dataTypes.others[12];
	$scope.mapTypes = mapMasterTypesToDataTypes;
	$scope.group = mapMasterTypesToDataTypes[$scope.search.type.name];
	$scope.inv = [];
	navigationFactory.setView($scope.search.type);

	// Redirect to list
	if(!$routeParams.search) {
		var search = {};
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "hall_probe_data", entityParameters.hall_probe_data) + "/list";
		$window.location = newLocation;
	}

	// Retrieve all Inventory items
	inventoryFactory.retrieveItems({'cmpnt_type_name': '*', 'serial_no': '*', 'vendor_name': '*'}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inv.push(item.id);
		});
	});

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "hall_probe_data", entityParameters.hall_probe_data) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listHallProbeDataCtrl', function($scope, $routeParams, $http, $window, inventoryFactory, HallProbeDataInfo, HallProbeData, hallProbeDataFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = HallProbeDataInfo;
	var previousItem;
	$scope.items = [];
	$scope.invMap = {};

	hallProbeDataFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

		$.each(result, function(i, item){

			// Build customized object
			var newItem = new HallProbeData(item);

			// Alternate background colors
			if(i%2 === 0) {
				newItem.color = "bg_dark";

			} else {
				newItem.color = "bg_light";
			}

			$scope.items.push(newItem);
		});
		$scope.items.reverse();
	});

	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "hall_probe_data", entityParameters.hall_probe_data) + "/id/new/action/save";
		$window.location = location;
	};

	// Show details when user selects item from a list
	$scope.showDetails = function(item) {
		$scope.id = undefined;

		// Clear click style from previously selected element
		if(previousItem !== undefined) {
			previousItem.click = "";
		}

		previousItem = item;
		item.click = "item_click";
		item.search = $routeParams.search;
		$routeParams.click = "item_click";
		$routeParams.inventory_id = item.inventory_id;

		var location = createRouteUrl($routeParams, "hall_probe_data", entityParameters.hall_probe_data) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showHallProbeDataCtrl', function($scope, $routeParams, $http, $window, HallProbeDataInfo, HallProbeData, hallProbeDataFactory, inventoryFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new HallProbeData();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = HallProbeDataInfo;

	$scope.inv = [];

	// Retrieve all Inventory items
	inventoryFactory.retrieveItems({'cmpnt_type_name': '*', 'serial_no': '*', 'vendor_name': '*'}).then(function(result) {

		$.each(result, function(i, item){
			$scope.inv.push(item.id);
		});
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {

		hallProbeDataFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.hall_probe_id = result.id;
			l($scope.element);
		});
	}

	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "hall_probe_data", entityParameters.hall_probe_data) + "/id/" + $routeParams.id + "/action/update";
		$window.location = location;
	};

	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
		var item = new HallProbeData(newItem);
		var result = hallProbeDataFactory.checkItem(item);
		l(result);

		if(result !== true) {
			$scope.error = result.errorDict;

		} else {
			var propsObject = {};

			delete $scope.error;
			var promise;

			if(action === "update") {
				promise = hallProbeDataFactory.updateItem($scope.element);

			} else if(action == "save") {
				promise = hallProbeDataFactory.saveItem($scope.new);
			}

			promise.then(function(data) {
				$scope.alert.show = true;
				$scope.alert.success = true;
				$scope.alert.title = "Success!";
				$scope.alert.body = "Hall probe data item successfully saved!";

			}, function(error) {
				$scope.alert.show = true;
				$scope.alert.success = false;
				$scope.alert.title = "Error!";
				$scope.alert.body = error;
			});
		}
	};
});
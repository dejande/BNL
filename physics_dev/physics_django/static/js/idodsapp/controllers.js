/*
 * Controllers for insertion device online data service module
 *
 * @author: Dejan Dežman <dejan.dezman@cosylab.com>
 * @created: Feb 26, 2014
 */

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
app.controller('mainCtrl', function($scope, $modal){
	$scope.version = version;
	$scope.style = {};
	$scope.style.middle_class = "container-scroll-middle";
	$scope.style.right_class = "container-scroll-last-one";
	setUpLoginForm();

	$scope.session = {};
	$scope.authenticated = {};
	$scope.authenticated.error = false;

	$scope.login = function() {
		l($scope.loginData);

		$.ajax({
			url: serviceurl + "user/login/",
			method: "POST",
			data: "username=" + $scope.session.username + "&password=" + $scope.session.password
		}).success(function(data, status, headers, config) {
			$scope.authenticated.error = false;
			$scope.$apply();
			location.reload();

		}).error(function(data, status, headers, config) {
			$scope.authenticated.error = true;
			$scope.$apply();
		});
	};

	$scope.logout = function() {

		$.ajax({
			url: serviceurl + "user/logout/",
			method: "POST"
		}).success(function(data, status, headers, config) {
			l(data);
			location.reload();

		}).error(function(data, status, headers, config) {

		});
	};

	$scope.uploadLattice = function() {
		var modalInstance = $modal.open({
			templateUrl: 'modal/save_lattice.html',
			controller: 'uploadLatticeModalCtrl'
		});
	};

	$scope.uploadModel = function() {
		var modalInstance = $modal.open({
			templateUrl: 'modal/save_model.html',
			controller: 'uploadModelModalCtrl'
		});
	};
});

/*
 * Controller for the left/search pane
 */
app.controller('searchVendorCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[0];

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		$window.location = newLocation;
	};

	// Vendor search button click
	$scope.searchForItem = function(search) {
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

	$scope.vendors = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "vendor", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	}

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
	vendorFactory.retrieveVendor($routeParams).then(function(result) {
		$scope.element = result;
		$scope.element.old_name = result.name;
	});
	
	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "vendor", ["name", "description"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchCmpntTypeCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[1];

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

	$scope.types = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	}

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
	}

	// Property name dropdown has changed
	$scope.changePropertyName = function() {
		l($scope.props);
	}
	
	// Get component type from the factory
	cmpntTypeFactory.retrieveCmpntType($routeParams).then(function(result) {
		$scope.element = result;
		$scope.element.old_name = result.name;
		l($scope.element);
	});
	
	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type", ["name", "description"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchCmpntTypeTypeCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[2];

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, ["name", "cmpnt_type_type", "description"]) + "/list";
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

	$scope.types = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type_type", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	}

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
	cmpntTypeTypeFactory.retrieveCmpntTypeType($routeParams).then(function(result) {
		$scope.element = result;
		$scope.element.old_name = result.name;
	});
	
	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "cmpnt_type_type", ["name", "description"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInventoryCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[3];

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "inventory", ["name"]) + "/list";
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

	$scope.items = [];
	var previousItem = undefined;

	inventoryFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "inventory", ["name"]) + "/id/new/action/save";
		$window.location = location;
	}

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

		var location = createRouteUrl($routeParams, "inventory", ["name"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInventoryCtrl', function($scope, $routeParams, $http, $window, InventoryInfo, CmpntType, Inventory, cmpntTypeFactory, inventoryTypeFactory, inventoryFactory, vendorFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new Inventory();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InventoryInfo;

	$scope.types = [];
	$scope.props = [];
	$scope.vendors = [];
	$scope.new.prop_keys = [];

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
	
	// Append new property
	$scope.appendProperty = function() {

		if($routeParams.action === "save"){
			$scope.new.prop_keys.push({'name': '', 'value': ''});
		
		} else {
			$scope.element.prop_keys.push({'name': '', 'value': ''});
		}
	}

	// Property name dropdown has changed
	$scope.changePropertyName = function() {
		l($scope.props);
	}
	
	// Get inventory from the factory if updating
	if($routeParams.action != "save") {
		
		inventoryFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
			l($scope.element);
		});
	}
	
	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "inventory", ["name"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
	$scope.saveItem = function(newItem, action) {
		$scope.alert.show = false;
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

				$.each($scope.element.prop_keys, function(i, prop) {
					propsObject[prop.name] = prop.value;
				});

				$scope.element.props = JSON.stringify(propsObject);

				promise = inventoryFactory.updateItem($scope.element);

			} else if(action == "save") {

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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInventoryTypeCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[4];

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

	$scope.items = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "inventory_type", ["name"]) + "/id/new/action/save";
		$window.location = location;
	}

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
		var location = createRouteUrl($routeParams, "inventory_type", ["name"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInstallCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[5];

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "install", ["name", "cmpnt_type", "description", "coordinatecenter"]) + "/list";
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

	$scope.items = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "install", ["name", "cmpnt_type", "description", "coordinatecenter"]) + "/id/new/action/save";
		$window.location = location;
	}

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
		$routeParams.cmpnt_type = item.cmpnt_type;
		$routeParams.coordinatecenter = item.coordinatecenter;

		var location = createRouteUrl($routeParams, "install", ["name", "cmpnt_type", "description", "coordinatecenter"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showInstallCtrl', function($scope, $routeParams, $http, $window, InstallInfo, Install, installFactory, cmpntTypeFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new Install();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = InstallInfo;

	$scope.types = [];

	// Retrieve all Component types
	cmpntTypeFactory.retrieveCompntTypes({}).then(function(result) {

		$.each(result, function(i, item){
			$scope.types.push(item.name);
		});
	});

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {
		
		installFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.old_name = result.name;
			l($scope.element);
		});
	}
	
	// Show update form in the right pane
	$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "install", ["name", "cmpnt_type", "description", "coordinatecenter"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchInstallRelTypeCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[4];

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

	$scope.items = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "install_rel_type", ["name"]) + "/id/new/action/save";
		$window.location = location;
	}

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
		var location = createRouteUrl($routeParams, "install_rel_type", ["name"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchDataMethodCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[6];

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

	$scope.items = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/new/action/save";
		$window.location = location;
	}

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
		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}
	
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
	}
});

/*
 * Controller for the left/search pane
 */
app.controller('searchOfflineDataCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[7];

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "offline_data", ["inventory_name", "description"]) + "/list";
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

	$scope.items = [];
	var previousItem = undefined;

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "offline_data", ["inventory_name", "description"]) + "/id/new/action/save";
		$window.location = location;
	}

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
		$routeParams.inventory_name = item.inventory_name;
		$routeParams.description = item.description;

		var location = createRouteUrl($routeParams, "offline_data", ["inventory_name", "description"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showOfflineDataCtrl', function($scope, $routeParams, $http, $window, OfflineDataInfo, OfflineData, offlineDataFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new OfflineData();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = OfflineDataInfo;

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {
		
		offlineDataFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.offline_data_id = result.id;
			l($scope.element);
		});
	}
	
	// Show update form in the right pane
	/*$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}*/
	
	/*$scope.saveItem = function(newItem, action) {
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
	}*/
});

/*
 * Controller for the left/search pane
 */
app.controller('searchOnlineDataCtrl', function($scope, $window, $routeParams){
	$scope.search = {};
	$scope.dataTypes = dataTypes;
	$scope.search.type = dataTypes[8];

	// Change entity
	$scope.changeEntity = function() {
		var newLocation = createRouteUrl(undefined, $scope.search.type.name, []);
		l(newLocation);
		$window.location = newLocation;
	};

	// Item search button click
	$scope.searchForItem = function(search) {
		search.search = new Date().getTime();
		var newLocation = createRouteUrl(search, "online_data", ["install_name", "description"]) + "/list";
		l(newLocation);
		$window.location = newLocation;
	};
});

/*
 * List items in the middle pane
 */
app.controller('listOnlineDataCtrl', function($scope, $routeParams, $http, $window, OnlineDataInfo, OnlineData, onlineDataFactory) {
	// Remove image from the middle pane if there is something to show
	$scope.style.middle_class = "container-scroll-middle-no-img";

	$scope.id = $routeParams.id;
	$scope.info = OnlineDataInfo;

	$scope.items = [];
	var previousItem = undefined;

	onlineDataFactory.retrieveItems($routeParams).then(function(result) {

		l(result);

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
	});
	
	// Show add form in the right pane
	$scope.addItem = function() {
		var location = createRouteUrl($routeParams, "online_data", ["install_name", "description"]) + "/id/new/action/save";
		$window.location = location;
	}

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

		var location = createRouteUrl($routeParams, "online_data", ["install_name", "description"]) + "/id/" + item.id + "/action/retrieve";
		$window.location = location;
	};
});

/*
 * Show details in the right pane
 */
app.controller('showOnlineDataCtrl', function($scope, $routeParams, $http, $window, OnlineDataInfo, OnlineData, onlineDataFactory, EntityError){
	// Remove image from the middle pane if there is something to show
	$scope.style.right_class = "container-scroll-last-one-no-img";
	$scope.action = $routeParams.action;
	$scope.new = new OnlineData();
	$scope.error = {};
	$scope.alert = {};
	$scope.alert.show = false;
	$scope.info = OnlineDataInfo;

	// Get inventory from the factory if updating
	if($routeParams.action != "save") {
		
		onlineDataFactory.retrieveItem($routeParams).then(function(result) {
			$scope.element = result;
			$scope.element.online_data_id = result.id;
			l($scope.element);
		});
	}
	
	// Show update form in the right pane
	/*$scope.updateItem = function() {
		var location = createRouteUrl($routeParams, "data_method", ["name", "description"]) + "/id/" + $routeParams["id"] + "/action/update";
		$window.location = location;
	}*/
	
	/*$scope.saveItem = function(newItem, action) {
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
	}*/
});

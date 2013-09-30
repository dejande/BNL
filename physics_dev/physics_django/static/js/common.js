/*
 * Functions common to complete application
 *
 * @author: Dejan Dežman <dejan.dezman@cosylab.com>
 */

$(document).ready(function(){

	// Write data from cookie back to object and remove cookie
	if($.cookie(filtersCookieName) !== undefined) {
		selectedElements = $.parseJSON($.cookie(filtersCookieName));
	}

	// Read data from settings cookie and set it to converterSettings object
	if($.cookie(settingsCookieName) !== undefined) {
		converterSettings = $.parseJSON($.cookie(settingsCookieName));
	}

	// Create new comparator
	jQuery.expr[':'].Contains = function(a, i, m) {
		return (a.textContent || a.innerText || "").toUpperCase().indexOf(m[3].toUpperCase()) >= 0;
	};
});

/**
 * Write logs to Chrome or Firefox console
 * @param input input string
 */
function l(input) {

	if(writeLogs === true) {
		console.log(input);
	}
}

/**
 * Trim spaces from the start and the end of the string
 * @param {type} str input string
 * @returns {unresolved} string without spaces in the start and at the end of string
 */
function trim(str) {
	str = str.replace(/^\s+/, '');
	for (var i = str.length - 1; i >= 0; i--) {
		if (/\S/.test(str.charAt(i))) {
			str = str.substring(0, i + 1);
			break;
		}
	}
	return str;
}

/**
 * Check if elements is present in the current DOM or not
 * @returns {Boolean}
 */
jQuery.fn.doesExist = function(){
	return jQuery(this).length > 0;
};

/**
 * Save filter data into a cookie
 * @param {type} dataToBeSaved object to be saved into a cookie
 */
function saveFilterData(dataToBeSaved) {
	l("save filters data");
	l(dataToBeSaved);
	$.cookie(filtersCookieName, JSON.stringify(dataToBeSaved));
}

/**
 * Save settings data to a cookie
 * @param {type} dataToBeSaved data to be saved into a cookie
 */
function saveOlogSettingsData(dataToBeSaved) {
	$.cookie(settingsCookieName, JSON.stringify(dataToBeSaved));
}

/**
 * Create query for listing devices
 * @param {type} search search or $routeParams object
 * @param {boolean} returnUrl return url or query
 * @returns {String} return url or query string
 */
function createDeviceListQuery(search, returnUrl) {
	var query = "";
	var url = "#";

	// Add type
	query += search.type + '/?';
	url += "/type/" + search.type;

	// Only include system attribute if we are looking through installed devices
	if(search.type === "install") {

		// Add system part
		if(search.system !== undefined) {
			query += "system=" + search.system + '&';
			url += "/system/" + search.system;

		} else {
				query += "system=*&";
				url += "/system/";
		}
	}

	// Only include name attribute if we are looking through installed devices
	if(search.type === "install") {

		// Add name part
		if(search.name !== undefined) {
			query += "name=" + search.name + '&';
			url += "/name/" + search.name;

		} else {

				query += "name=*&";
				url += "/name/";
		}
	}

	// Add component type part
	if(search.cmpnt_type !== undefined) {
		query += "cmpnt_type=" + search.cmpnt_type + '&';
		url += "/cmpnt_type/" + search.cmpnt_type;

	} else {
		query += "cmpnt_type=*&";
		url += "/cmpnt_type/";
	}

	// Add serial number part
	if(search.serialno !== undefined) {
		query += "serialno=" + search.serialno;
		url += "/serialno/" + search.serialno;

	} else {
		query += "serialno=*";
		url += "/serialno/";
	}

	// Return URL or query
	if(returnUrl) {
		return url;

	} else {
		return query;
	}
}

/*
 * Create modal window on top of the web app
 * Example of use: createModal($modal, $scope);
 */
function createModal(modal, scope) {
	var modalInstance = modal.open({
		template: '\n\
		<div class="modal-header">\n\
			<h3>Im a modal!</h3>\n\
		</div>\n\
		<div class="modal-body">\n\
		body\n\
		</div>\n\
		<div class="modal-footer">\n\
			<button class="btn btn-primary" ng-click="ok()">OK</button>\n\
			<button class="btn btn-warning" ng-click="cancel()">Cancel</button>\n\
		</div>\n\
		',
		controller: "modalCtrl"
	});

	modalInstance.result.then(function(selectedItem) {
		scope.selected = selectedItem;
	}, function() {
		l("modal dismissed");
	});
}

/*
 * Retun first X characters from the string.
 * @param {type} string input string
 * @param {type} count how many characters do we want to return
 * @returns {String} First X words
 */
function returnFirstXCharacters(string, count){

	if(string.length > count) {
		return string.substring(0, count) + " ...";

	} else {
		return string;
	}
}
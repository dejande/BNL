/*
 * Helper functions for Unit Conversion client
 *
 * @author: Dejan Dežman <dejan.dezman@cosylab.com>
 */

// Global plot variable
var plot = undefined;

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

/**
 * Create plot from the two vectors from measurement data table
 * @param {type} data measurement data object
 * @param {type} x_axis measurement data object property that should be put on the x axis
 * @param {type} y_axis measurement data object property that should be put on the y axis
 * @param {type} newSeries array of conversion result points that should be put on the plot together with measurement data
 */
function drawPlot(data, x_axis, y_axis, newSeries){

	// Plot options object
	var options = {
		series: [{label: "Measurement data"}, {label: "Conversion results", showLine:false}],
		seriesColors: ["#c5b47f", "#953579"],
		axesDefaults: {
			labelRenderer: $.jqplot.CanvasAxisLabelRenderer
		},
		legend: {show: true},
		axes: {
			xaxis: {
				label: x_axis,
				pad: 0,
				tickOptions:{formatString:'$%.4f'}
			},
			yaxis: {
				label: y_axis,
				tickOptions:{formatString:'$%.4f'}
			}
		},
		highlighter: {
			show: true,
			sizeAdjust: 7.5
		},
		cursor: {
			show: true,
			zoom: true,
			showTooltip:	false
		}
	};

	// Prepared series from measuremetn data series
	var preparedSeries = prepareSeries(data, x_axis, y_axis);
	var series = [];

	// Add prepared series
	if(preparedSeries.length !== 0) {
		series.push(preparedSeries);
	}

	// Ad series of conversion points
	if(newSeries.length !== 0) {
		series.push(newSeries);
	}

	// Destroy previous plot if exists
	if(plot !== undefined) {
		plot.destroy();
		$('#plot').html("");
	}

	// Only draw plot if something is in series
	if(series.length !== 0) {
		plot = $.jqplot ('plot', series, options);

		$('#zoom').unbind('click');
		$('#zoom').click(function() {
			plot.resetZoom();
		});
	}
}

/**
 * Represent jason data as a tree with <ul> and <li> elements.
 * @param {type} html html code to start with
 * @param {type} data json data object
 * @returns {String} html with tree content
 */
function drawDataTree(html, data){
	//l(data);

	if(data === undefined) {
		return "";

	} else {
		html += "<ul>";

		for(var prop in data) {
			html += "<li>";
			html += "<b>" + prop + "</b>";

			// Find object
			if($.type(data[prop]) === 'object') {
				html = drawDataTree(html, data[prop]);

			} else {
				html += ': ' + data[prop];
			}
			html += "</li>";
		}
		html += "</ul>";
	}

	return html;
}

/**
 * Prepare series for plotting
 * @param {type} data measurement data object
 * @param {type} x_axis measurement data object property used to plot data on x axis
 * @param {type} y_axis measurement data object property used to plot data on y axis
 * @returns {Array} array of points
 */
function prepareSeries(data, x_axis, y_axis) {
	var series = [];

	// Check if data is udefined
	if(data === undefined) {
		return series;
	}

	// Set default data on axes
	var x_data = data.current;
	var y_data = data.field;

	// Set a new vector on x axis
	if(x_axis !== undefined) {
		x_data = data[x_axis];
	}

	// Set a new vector on y axis
	if(y_axis !== undefined) {
		y_data = data[y_axis];
	}

	// If there is data available for plotting, rearange it to create array of points
	if(x_data !== undefined && y_data !== undefined) {

		for(var i=0; i<x_data.length; i++){
			series.push([x_data[i], y_data[i]]);
		}
	}

	return series;
}
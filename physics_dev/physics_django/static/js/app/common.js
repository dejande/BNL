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

/*
 * Prepare form for login. Form is a part on a dropdown so some mesures should
 * be taken to change the dropdown functionality.
 */
function setUpLoginForm() {
	// Setup drop down menu
	$('.dropdown-toggle').dropdown();

	// Fix input element click problem
	$('.dropdown-menu').click(function(e) {
		e.stopPropagation();
	});

	$('#user_login_dropdown').click(function(){
		$('.user_dropdown_menu').ready(function(){
			$('#user_username').focus();
		});
	});
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
 * Function returns "-" if input parsed to float is lower than 0 or "+" if parsed float is greater of equal to 0
 * @param  {type} str input float number parsed as string
 * @return "+" or "-" string
 */
function returnSign(str) {
	var floatNumber = parseFloat(str);

	if(floatNumber < 0) {
		return "";

	} else {
		return "+";
	}
}

/**
 * Parse function string and determine algorithm type and all parameters
 * @param  {type} str function string
 * @return {type} Obj object with algorithm type and all parameters
 */
function parseAlgFunction(algFunction) {
	var returnObj = {};

	var tryMeasurementData = algFunction.split(",");
	var tryPlinom = algFunction.split("input");

	if(tryMeasurementData.length == 2) {
		returnObj.alg_type = "3";
		returnObj.current = $.trim(tryMeasurementData[0]);
		returnObj.field = $.trim(tryMeasurementData[1]);

	} else if(tryPlinom.length == 2) {
		returnObj.alg_type = "1";
		returnObj.a1 = $.trim(tryPlinom[0].replace("*", "").replace("+", ""));
		returnObj.a0 = $.trim(tryPlinom[1].replace("+", ""));

	} else if (tryPlinom.length == 3) {
		returnObj.alg_type = "2";
		returnObj.a2 = $.trim(tryPlinom[0].replace("*", "").replace("+", ""));
		returnObj.a1 = $.trim(tryPlinom[1].replace("*", "").replace("^2", "").replace("+", ""));
		returnObj.a0 = $.trim(tryPlinom[2].replace("+", ""));
	}

	return returnObj;
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

		} else if(search.inst !== undefined) {
			query += "name=" + search.inst + '&';
			url += "/name/";

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
 * @param {type} scope $scope object
 */
function drawPlot(data, x_axis, y_axis, newSeries, scope){

	var seriesData = {};
	scope.plot.numberOfDirections = 0;
	var container = $(".placeholder");
	var resizeContainer = $(".resize_container");

	if(scope.plot.direction === undefined) {
		scope.plot.direction = {};
	}

	// Create series according to directions
	if(data !== undefined && data.direction !== undefined) {

		$.each(data.direction, function(i, dir) {

			if(dir !== "") {

				if(dir in seriesData) {
					seriesData[dir].push([data[x_axis][i], data[y_axis][i]]);

				} else {
					seriesData[dir] = [[data[x_axis][i], data[y_axis][i]]];
					scope.plot.numberOfDirections ++;

					if(!(dir in scope.plot.direction)) {
						scope.plot.direction[dir] = true;
					}
				}
			}
		});
	}

	var series = [];
	var preparedSeries = [];

	// If we want to plot direction, make a line for every direction
	if(scope.plot.direction_plot === "true") {

		$.each(scope.plot.direction, function(i, dir) {

			if(dir === true) {
				// Prepared series from measuremetn data series
				preparedSeries = seriesData[i];

				// Add prepared series
				if(preparedSeries.length !== 0) {

					// Add 0,0 point if there is only one point to be plotted
					if(preparedSeries.length === 1) {
						preparedSeries.push([0, 0]);
					}

					series.push({label:i, lines: { show: true }, points: { show: true }, data:preparedSeries});
				}
			}
		});

	} else {
		// Prepared series from measuremetn data series
		preparedSeries = prepareSeries(data, x_axis, y_axis);

		// Add prepared series
		if(preparedSeries.length !== 0) {
			series.push({label:"Measurement data", lines: { show: false }, points: { show: true }, data:preparedSeries});
		}
	}

	// Add series of conversion points
	if(newSeries.length > 0) {
		series.push({label:"Conversion results", lines: { show: false }, points: { show: true }, data:newSeries});
	}

	l(series);

	// Plot options
	var optionsFlot = {
		legend: {
			show: true,
			position: "nw"
		},
		xaxis: {
			tickDecimals: 4
		},
		yaxis: {
			tickDecimals: 4
		},
		zoom: {
			interactive: true
		},
		pan: {
			interactive: true
		},
		grid: {
			hoverable: true
		}
	};

	// We have at least one series
	if(series.length > 0 && $) {

		// Initialize plot
		var flotPlot = $.plot(container, series, optionsFlot);

		resizeContainer.resizable({
			maxWidth: 2000,
			maxHeight: 700,
			minWidth: 900,
			minHeight: 400
		});

		// Create y axis labe
		var yaxisLabel = $(".y_label").text(y_axis);

		// Create x axis label
		var xaxisLabel = $(".x_label").text(x_axis);

		// Create zoom out button
		$("<div class='zoom zoom_out'></div>")
			.appendTo(container)
			.click(function (event) {
				event.preventDefault();
				flotPlot.zoomOut();
			}
		);

		// Create zoom in button
		$("<div class='zoom zoom_in'></div>")
			.appendTo(container)
			.click(function (event) {
				event.preventDefault();
				flotPlot.zoom();
			}
		);

		// Create pan arrows
		addArrow("up", {top: -100}, container, flotPlot);
		addArrow("left", {left: -100}, container, flotPlot);
		addArrow("down", {top: 100}, container, flotPlot);
		addArrow("right", {left: 100}, container, flotPlot);

		// Create tooltips when hovering over points
		container.bind("plothover", function (event, pos, item) {

			if (item) {
				$("#tooltip").remove();
				var x = item.datapoint[0].toFixed(4);
				var y = item.datapoint[1].toFixed(4);
				showTooltip(item.pageX, item.pageY, x + ", " + y);

			} else {
				$("#tooltip").remove();
			}
		});
	}
}

/*
 * Add arrow image to plot. Arrow will be used for panning the plot
 * @param {type} classNamePart part of the class name that will select the appropriate image
 * @param {type} offset for how much do we wan't to move
 * @param {type} placeholder id of the plot DOM element
 * @param {type} plot plot object
 */
function addArrow(classNamePart, offset, placeholder, plot) {
	$("<div class='pan pan_" + classNamePart + "'></div>")
		.appendTo(placeholder)
		.click(function (e) {
			e.preventDefault();
			plot.pan(offset);
		});
}

/*
 * Show tooltip on a plot when hovering over the point
 * @param {type} x x coordinate of plot position
 * @param {type} y y coordinate of plot position
 * @param {type} contents tooltip contents
 */
function showTooltip(x, y, contents) {
	$("<div id='tooltip'>" + contents + "</div>").css({
		position: "absolute",
		display: "none",
		top: y + 5,
		left: x + 5,
		border: "1px solid #fdd",
		padding: "2px",
		"background-color": "#fee",
		opacity: 0.80
	}).appendTo("body").fadeIn(100);
}

/**
 * Represent json data as a tree with <ul> and <li> elements.
 * @param {type} html html code to start with
 * @param {type} data json data object
 * @returns {String} html with tree content
 */
function drawDataTree(html, data){

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
	var directions = [];

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

	if(data.direction !== undefined) {
		directions = data.direction;
	}

	// If there is data available for plotting, rearange it to create array of points
	if(x_data !== undefined && y_data !== undefined) {

		for(var i=0; i < x_data.length; i++){
			series.push([x_data[i], y_data[i]]);
		}
	}

	return series;
}
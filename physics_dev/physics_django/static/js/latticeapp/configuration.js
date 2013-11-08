/*
 * Configuration file for setting global variables
 *
 * @author: Dejan Dežman <dejan.dezman@cosylab.com>
 */

/**
 * Variables that can be and should be configured by user
 */

// For accessing the REST service
var serviceurl = "http://localhost:8000/";

//Version number
var version = "0.1";

//Write logs to console
var writeLogs = true;

// Lattice statuses
var statuses = [
	{id:-1, value:"-"},
	{id:0, value:"Current golden lattice"},
	{id:1, value:"Alternative golden lattice"},
	{id:2, value:"Lattice from live machine"},
	{id:3, value:"Previous golden lattice"}
];

// Model statuses
var modelStatuses = [
	{id:-1, value:"-"},
	{id:0, value:"Current golden model"},
	{id:1, value:"Alternative golden model"},
	{id:2, value:"Model from live machine"},
	{id:3, value:"Previous golden model"}
];

// Model details
var modelDetails = [
	{name:"Transfer Matrix", value:"retrieveTransferMatrix"},
	{name:"Closed Orbit", value:"retrieveClosedOrbit"},
	{name:"Twiss", value:"retrieveTwiss"},
	{name:"Beam Parameters", value:"retrieveBeamParameters"}
];
export default {
	"taxonomy" : {
		"ignorance": {
			"color": "#9270a8",
			"description": ""
		},
		"credibility": {
			"color": "#cc4c3b",
			"description": ""
		},
		"imprecision": {
			"color": "#f1d155",
			"description": ""
		},
		"incompleteness": {
			"color": "#67b2ac",
			"description": ""
		},
	},
	"entities" : {
		"person": {
			"icon": "\uf007", 
			"color": "#ff7f00",
		},
		"event": {
			"icon": "\uf274", 
			"color": "#cecece"
		},
		"org": {
			"icon": "\uf1ad", 
			"color": "#b4edfc"
		},
		"object": {
			"icon": "\uf466", 
			"color": "#b4d38d"
		},
		"place": {
			"icon": "\uf279", 
			"color": "#204191",
		},
		"date": {
			"icon": "\uf073", 
			"color": "#868788"
		},
		"time": {
			"icon": "\uf017", 
			"color": "#eab9e4"
		}/*
		"location": {
			"icon": "\uf5a0", 
			"color": "#ff6464"
		},
		"geolocation": {
			"icon": "\uf5a0", 
			"color": "#ff6464"
		},
		"name": {
			"icon": "\uf007", 
			"color": "#ff7f00"
		},
		"occupation": {
			"icon": "\uf0b1", 
			"color": "#3c8745"
		},
		"placeName": {
			"icon": "\uf279", 
			"color": "#204191"
		},
		"country": {
			"icon": "\uf279", 
			"color": "#204191"
		},*/
	},
	"properties": {
		"person": [
			"forename",
			"surname",
			"occupation",
			"sex",
			"birth",
			"death",
			"age"
		],
		"place": [
			"country",
			"settlement",
			"[geo]location"
		]
	}
};
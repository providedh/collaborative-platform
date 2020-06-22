const content = ('<p>Take a Pound of fine Sugar , <name xml:id="name-0" ref="#sand">sand</name> a Pint of ' +
'Water , or more , as the Quantity you intend to make requires ; set it on the Fire , ' +
'let it boil , <name xml:id="name-1" ref="#sand">and</name> set a Pan of Water to boil ; ' +
'when it boils , put in your Plums ; <name xml:id="name-2" ref="#jus">let them just ' +
'boil</name> , and then take them out with a Ladle , as they flip their Skins off ; take off the ' +
'Skins , and put the Plums into the Syrup ; do this as fast as you can , that they may not ' +
'turn : Boil them <name xml:id="name-3">Alejandro</name> all to Pieces ; and to a Quart of ' +
'Plums put a Pint of Apple-Jelly ; boil Plums put a Pint of Apple-Jelly ; boil ' +
'them well together , and rub it thro ’ a Hair Sieve ; to a Pint of this put a Pound and ' +
'a half of sifted Sugar ; let the Jelly boil before you shake the <name xml:id="name-4">Sugar</name> , and let it ' +
'scald ’ <name xml:id="name-5">till the Sugar is well melted</name> ; skin it , put it in Pots , and dry it in the Stove .</p>')


export default {
  "authors": [
    {
      "xml:id": "annotator-1",
      "forename": "Estefanía",
      "surname": "de los Santos",
      "username": "estefania"
    },
    {
      "xml:id": "annotator-2",
      "forename": "Alejandro",
      "surname": "Hernández",
      "username": "jancho"
    },
  ],
  "certainties": [
    {
      "ana": "https://providedh-test.ehum.psnc.pl/api/projects/17/taxonomy/#incompleteness",
      "locus": "name",
      "degree": 0,
      "cert": "very high",
      "resp": "annotator-1",
      "match": "",
      "target": "#name-1",
      "xml:id": "ann-0",
      "assertedValue": "",
      "desc": "",
      "saved": true,
      "deleted": false
    },
    {
      "ana": ("https://providedh-test.ehum.psnc.pl/api/projects/17/taxonomy/#incompleteness "+
              "https://providedh-test.ehum.psnc.pl/api/projects/17/taxonomy/#credibility"),
      "locus": "value",
      "degree": 0,
      "cert": "high",
      "resp": "annotator-1",
      "match": "age",
      "target": "#name-3",
      "xml:id": "ann-2",
      "assertedValue": "21",
      "desc": "Oh my, he is not the devil's number old.",
      "saved": true,
      "deleted": false
    },
    {
      "ana": "https://providedh-test.ehum.psnc.pl/api/projects/17/taxonomy/#ignorance",
      "locus": "value",
      "degree": 0,
      "cert": "high",
      "resp": "annotator-2",
      "match": "age",
      "target": "#name-3",
      "xml:id": "ann-3",
      "assertedValue": "666",
      "desc": "He is indeed related to the devil's culpt.",
      "saved": false,
      "deleted": false
    },
  ],
  "entities_lists": {
    "ingredient": [
      {
        "type": "ingredient",
        "xml:id": "name-0",
        "resp": "annotator-1",
        "properties": [
          {
            "name": "ref",
            "value": "#sand",
            "saved": false,
            "deleted": false
          },
        ],
        "saved": true,
        "deleted": false
      },
      {
        "type": "ingredient",
        "xml:id": "name-1",
        "resp": "annotator-1",
        "properties": [
          {
            "name": "ref",
            "value": "#sand",
            "saved": true,
            "deleted": false
          },
        ],
        "saved": true,
        "deleted": false
      },
      {
        "type": "ingredient",
        "xml:id": "name-4",
        "resp": "annotator-1",
        "properties": [],
        "saved": false,
        "deleted": false
      },
    ],
    "productionMethod": [
      {
        "type": "productionMethod",
        "xml:id": "name-2",
        "resp": "annotator-1",
        "properties": [],
        "saved": true,
        "deleted": false
      },
      {
        "type": "productionMethod",
        "xml:id": "name-5",
        "resp": "annotator-2",
        "properties": [],
        "saved": true,
        "deleted": false
      },
    ],
    "person": [
	  {
	    "type": "person",
	    "xml:id": "name-3",
	    "resp": "annotator-2",
	    "properties": [
	      {
            "name": "age",
            "value": "666",
            "saved": true,
            "deleted": false
          },
	    ],
	    "saved": true,
	    "deleted": false
	  },
	]
  },
  "body_content": content
}
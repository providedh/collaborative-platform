import {Validator} from 'jsonschema'

const v = new Validator();

const responseSchema = {
  "id": "/Response",
  "type": "object",
  "properties": {
    "status": {
      "required": true,
      "type": "int"
    },
    "message": {
      "required": true,
      "type": "string"
    },
    "authors": {
      "required": true,
      "type": "array",
      "items": {
        "required": true,
        "type": "/Author"
      }
    },
    "operations": {
      "required": true,
      "type": "array",
      "items": {
        "required": true,
        "type": "/Operation"
    }
    },
    "certainties": {
      "required": true,
      "type": "array",
      "items": {
        "required": true,
        "type": "/Certainty"
    }
    },
    "entities_lists": {
      "required": true,
      "type": "/EntityList"
    },
    "body_content": {
      "required": true,
      "type": "string"
  },
  }
}

const authorSchema = {
  "id": "/Author",
  "type": "object",
  "properties": {
    "xml:id": {
      "required": true,
      "type": "string"
  },
    "forename": {
      "required": true,
      "type": "string"
  },
    "surname": {
      "required": true,
      "type": "string"
  },
    "username": {
      "required": true,
      "type": "string"
  },
  }
}

const operationSchema = {
  "id": "/Operation",
  "type": "object",
  "properties": {
    "edited_element_id": {
      "required": true,
      "type": "string"
  },
    "element_type": {
      "required": true,
      "type": "string"
  },
    "id": {
      "required": true,
      "type": "string"
  },
    "method": {
      "required": true,
      "type": "string"
  },
    "new_element_id": {
      "required": true,
      "type": "string"
  },
    "old_element_id": {
      "required": true,
      "type": "string"
  },
    "operation_result": {
      "required": true,
      "type": "string"
  },
  }
}

const certaintySchema = {
  "id": "/Certainty",
  "type": "object",
  "properties": {
    "ana": {
      "required": true,
      "type": "string"
  },
    "locus": {
      "required": true,
      "type": "string"
  },
    "degree": {
      "required": true,
      "type": "float"
  },
    "cert": {
      "required": true,
      "type": "string"
  },
    "resp": {
      "required": true,
      "type": "string"
  },
    "match": {
      "required": true,
      "type": "string"
  },
    "target": {
      "required": true,
      "type": "string"
  },
    "xml:id": {
      "required": true,
      "type": "string"
  },
    "assertedValue": {
      "required": true,
      "type": "string"
  },
    "desc": {
      "required": true,
      "type": "string"
  },
    "saved": {
      "required": true,
      "type": "bool"
  },
    "deleted": {
      "required": true,
      "type": "bool"
  },
  }
}

const entityListSchema = {
  "id": "/EntityList",
  "type": "object",
  "patternProperties": {
    ".+": {
      "required": true,
      "type": "array",
      "items": {
        "required": true,
        "type": "/Entity"
    }
    },
  }
}

const entitySchema = {
  "id": "/Entity",
  "type": "object",
  "properties": {
    "required": true,
    "type": {
      "required": true,
      "type": "string"
  },
    "xml:id": {
      "required": true,
      "type": "string"
  },
    "resp": {
      "required": true,
      "type": "string"
  },
    "saved": {
      "required": true,
      "type": "bool"
  },
    "deleted": {
      "required": true,
      "type": "bool"
  },
    "propreties": {
      "required": true,
      "type": "array",
      "items": {
        "required": true,
        "type": "/EntityProperty"
    }
    },
  }
}

const entityPropertySchema = {
  "id": "/EntityProperty",
  "type": "object",
  "properties": {
    "name": {
      "required": true,
      "type": "string"
  },
    "value": {
      "required": true,
      "type": "string"
  },
    "saved": {
      "required": true,
      "type": "string"
  },
    "deleted": {
      "required": true,
      "type": "string"
  },
  }
}

v.addSchema(authorSchema, authorSchema['id'])
v.addSchema(operationSchema, operationSchema['id'])
v.addSchema(certaintySchema, certaintySchema['id'])
v.addSchema(entityPropertySchema, entityPropertySchema['id'])
v.addSchema(entitySchema, entitySchema['id'])
v.addSchema(entityListSchema, entityListSchema['id'])

export default response => v.validate(response, responseSchema)
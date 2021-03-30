import { Validator } from 'jsonschema'

const v = new Validator()

const responseSchema = {
  id: '/Response',
  type: 'object',
  properties: {
    connected_users: {
      required: true,
      type: 'array',
      items: {
        required: true,
        type: '/User'
      }
    },
  }
}

const userSchema = {
  id: '/User',
  type: 'object',
  properties: {
    'id': {
      required: true,
      type: 'string'
    },
    username: {
      required: true,
      type: 'string'
    },
    first_name: {
      required: true,
      type: 'string'
    },
    last_name: {
      required: true,
      type: 'string'
    }
  }
}

v.addSchema(userSchema, userSchema.id)

export default response => v.validate(response, responseSchema)

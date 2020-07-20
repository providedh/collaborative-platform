export default {
  taxonomy: {
    ignorance: {
      icon: '\\f04b',
      color: '#9270a8'
    },
    credibility: {
      icon: '\\f0c8',
      color: '#cc4c3b'
    },
    imprecision: {
      icon: '\\f005',
      color: '#f1d155'
    },
    incompleteness: {
      icon: '\\f0c2',
      color: '#67b2ac'
    }
  },
  entities: {
    date: {
      icon: '\\f073',
      color: '#868788',
      properties: ['ref']
    },
    event: {
      icon: '\\f274',
      color: '#cecece',
      properties: ['ref']
    },
    object: {
      icon: '\\f466',
      color: '#b4d38d',
      properties: ['ref']
    },
    org: {
      icon: '\\f1ad',
      color: '#b4edfc',
      properties: ['ref']
    },
    person: {
      icon: '\\f007',
      color: '#ff7f00',
      properties: [
        'forename',
        'surname',
        'occupation',
        'sex',
        'birth',
        'death',
        'age',
        'ref'
      ]
    },
    place: {
      icon: '\\f279',
      color: '#204191',
      properties: ['country', 'geolocation', 'ref']
    },
    time: {
      icon: '\\f017',
      color: '#eab9e4',
      properties: ['ref']
    },
    ingredient: {
      icon: '\\f787',
      color: '#395b50',
      properties: ['ref']
    },
    productionMethod: {
      icon: '\\f542',
      color: '#291528',
      properties: ['ref']
    },
    utensil: {
      icon: '\\f542',
      color: '#96031a',
      properties: ['ref']
    }
  }
}

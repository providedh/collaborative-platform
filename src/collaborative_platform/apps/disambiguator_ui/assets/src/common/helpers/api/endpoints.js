export default {
  getProvinces: { method: 'GET', builder: () => ['/api', 'provinces'].join('/') },
  getMunicipalities: { method: 'GET', builder: ({ province }) => ['/api', 'provinces', province, 'municipalities'].join('/') },
  getInitiatives: {
    method: 'GET',
    builder: ({ province, municipality, category, state }) =>
      ['/api', 'initiatives', province, municipality, category, state].join('/')
  },
  getInitiative: { method: 'GET', builder: ({ id }) => ['/api', 'initiative', id].join('/') },
  setInitiative: { method: 'POST', builder: () => ['/api', 'initiative'].join('/') },
  interested: { method: 'POST', builder: () => ['/api', 'initiative/interested'].join('/') },
  colaborator: { method: 'POST', builder: () => ['/api', 'initiative/colaborator'].join('/') },
  comment: { method: 'POST', builder: () => ['/api', 'initiative/comment'].join('/') },
  proposal: { method: 'POST', builder: () => ['/api', 'initiative/proposal'].join('/') },
  adhere: { method: 'POST', builder: () => ['/api', 'initiative/adhere'].join('/') },
  copyInitiative: { method: 'POST', builder: () => ['/api', 'initiative/copyInitiative'].join('/') },
  setFeedBackForm: { method: 'POST', builder: () => ['/api', 'feedBack'].join('/') },
  cicd: { method: 'GET', builder: () => ['/api', 'cicd'].join('/') }
}

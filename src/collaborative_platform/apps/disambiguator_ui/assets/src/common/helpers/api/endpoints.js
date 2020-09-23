export default {
  getUnifications: { method: 'GET', builder: project => ['/api', 'nn_disambiguator', 'projects', project, 'proposals/'].join('/') },
  updateUnification: { method: 'PUT', builder: project => ['/api', 'nn_disambiguator', 'projects', project, 'proposals/'].join('/') },
  getDisambiguatorStatus: { method: 'GET', builder: project => ['/api', 'nn_disambiguator', 'projects', project, 'calculations/'].join('/') },
  updateDisambiguatorStatus: { method: 'POST', builder: project => ['/api', 'nn_disambiguator', 'projects', project, 'calculations/'].join('/') },
}

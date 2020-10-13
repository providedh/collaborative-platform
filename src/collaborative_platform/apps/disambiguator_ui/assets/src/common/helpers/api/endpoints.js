export default {
  getProposalList: { method: 'GET', builder: project => ['/api', 'disambiguator', 'projects', project, 'proposals/'].join('/') },
  getFileProposalList: { method: 'GET', builder: (project, file) => ['/api', 'disambiguator', 'projects', project, 'files', file, 'proposals/'].join('/') },
  getProposalDetails: { method: 'GET', builder: 
    (project) => ['/api', 'disambiguator', 'projects', project, 'proposals', 'details/'].join('/') },
  updateUnification: { method: 'PUT', builder: project => ['/api', 'disambiguator', 'projects', project, 'proposals/'].join('/') },
  getDisambiguatorStatus: { method: 'GET', builder: project => ['/api', 'disambiguator', 'projects', project, 'calculations/'].join('/') },
  updateDisambiguatorStatus: { method: 'POST', builder: project => ['/api', 'disambiguator', 'projects', project, 'calculations/'].join('/') },
}

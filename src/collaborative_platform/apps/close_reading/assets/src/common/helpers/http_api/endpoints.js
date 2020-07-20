export default {
  getProvinces: { method: 'GET', builder: () => ['/api', 'provinces'].join('/') }
}

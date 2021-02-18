window.onload = () => document
  .getElementById('project-overlay-toggle-button')
  .addEventListener('click', () => {
    document.getElementById('project-overlay').classList.toggle('d-none')
    document.getElementById('project-overlay-toggle').classList.toggle('toggled')
  })
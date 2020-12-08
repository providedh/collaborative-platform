function getCookie (name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

function fetchJobs(project_id) {
  const csrfToken = getCookie('csrftoken');
  const url=`/api/disambiguator/projects/${project_id}/calculations/`;

  const fetchBody = {
    method: 'GET',
    mode: 'cors',
    cache: 'no-cache',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': csrfToken,
      'X-CSRFToken': csrfToken,
    },
    redirect: 'follow',
    referrer: 'no-referrer'
  }	

  return new Promise((resolve, reject) => {
    fetch(url, fetchBody)
      .then(response => {
        if (response.ok === false){ throw {status: response.status} }
        response.json()
          .then(json => { resolve(json.sort((a, b) => new Date(b.created) - new Date(a.created))) })
          .catch(err => { resolve(response) })
      })
      .catch(err => { reject(err) });
  })
}

function getCurrentFormattedTime() {
  const currentTime = new Date(Date.now());
  const formatter = new Intl.NumberFormat("en-IN", {minimumIntegerDigits: 2});
  const hours = formatter.format(currentTime.getHours());
  const minutes = formatter.format(currentTime.getMinutes());
  const currentTimeFormatted = `${hours}:${minutes}`
  return currentTimeFormatted;
}

function renderEmptyJobs(tableRows) {
  tableRows.innerHTML = `
      <tr>
            <td colspan="3" class="pl-5 py-2">
                No job has been started jet, open the app to start a new one.
            </td>
        </tr>
  `
}

function renderJobs(tableRows, jobs) {
  const jobHTML = job => `
          <tr>
                <td class="jobStatusIndicator">
                    <span class="${job.status}"></span>
                </td>
                <td>${job.status}</td>
                <td>${new Date(job.created)}</td>
            </tr>
      `
  tableRows.innerHTML = jobs.map(jobHTML).join('\n')
}

function updateJobs(tableRows, project_id) {
  const maxJobs = 3
  fetchJobs(project_id).then(jobs => {
      if (jobs.length === 0) {
          renderEmptyJobs(tableRows);
      } else {
          renderJobs(tableRows, jobs.slice(0, Math.min(maxJobs, jobs.length)));
      }

      if (jobs.length > maxJobs) {
          tableRows.innerHTML = tableRows.innerHTML + `
              <tr><td class="text-right" colspan="3">+ ${jobs.length - maxJobs} jobs</td></tr>
          `
      }

      const updateTime = getCurrentFormattedTime()
      tableRows.parentElement.tHead.rows[0].children[0].innerText =
          `Updates automatically (last updated at ${updateTime})`
  });
}

function periodicJobUpdate(tableRows, project_id) {
  const period = 1000 * 60 * 2; // 2 minute
  updateJobs(tableRows, project_id);
  setTimeout(() => {
      periodicJobUpdate(tableRows, project_id);
  }, period);
}

function setupJobHistoryLoad() {
  const project_id = document.getElementById('project_id').innerText;
  const tableRows = document.getElementById('job-history').tBodies[0];
  setTimeout(() => {
      periodicJobUpdate(tableRows, project_id);
  }, 0);
}

document.addEventListener('DOMContentLoaded', setupJobHistoryLoad)
import React from 'react'
import PropTypes from 'prop-types'

export default function LoadingApp ({ fetched, fetching, error }) {
  return (
    <div className="align-items-center d-flex flex-column mt-5">
      <div className="column">
        <h1 className="display-4">Fetching initial configuration</h1>
        <p className="lead"> This is only done once when the page is loaded. </p>
        <ul className="list-unstyled">
          <li><i className={`mr-1 fa fa-${fetched > 0 ? 'check' : 'spinner'}`}></i>Project file structure.</li>
          <li><i className={`mr-1 fa fa-${fetched > 1 ? 'check' : 'spinner'}`}></i>Project collaborators.</li>
          <li><i className={`mr-1 fa fa-${fetched > 2 ? 'check' : 'spinner'}`}></i>Project taxonomy configuration.</li>
          <li><i className={`mr-1 fa fa-${fetched > 3 ? 'check' : 'spinner'}`}></i>Project versions.</li>
        </ul>
        <div className="progress">
          <div className="progress-bar progress-bar-striped progress-bar-animated"
            role="progressbar"
            aria-valuenow="75"
            aria-valuemin="0"
            aria-valuemax="100"
            style={{ width: Math.trunc(100 * fetched / 4) + '%' }}>
          </div>
        </div>
        <p>
          <small className="text-muted">Fetching {fetching}</small>
        </p>
        {error.length === 0 ? ''
          : <div className="alert alert-danger mt-3" role="alert">
            <h4 className="alert-heading">An error while fetching</h4>
            <p>An error ocurred while loading the initial configuration. {error}</p>
            <hr/>
            <p className="mb-0">This can be related to an internet connection issue. try refreshing the page.
              <a className="btn btn-warning ml-2" href="javascript:history.go(0)">Click to refresh the page</a>
            </p>
          </div>
        }
      </div>
    </div>
  )
}

LoadingApp.propTypes = {
  fetched: PropTypes.number,
  fetching: PropTypes.string,
  error: PropTypes.string
}

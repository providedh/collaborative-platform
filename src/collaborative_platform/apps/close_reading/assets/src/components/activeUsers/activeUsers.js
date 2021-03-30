import React from 'react'
import PropTypes from 'prop-types'

import styles from './app.module.css' // eslint-disable-line no-unused-vars

export default function ActiveUsers({users}) {
  const userSubset = users.slice(0, Math.min(3, users.length))

  const userIcons = userSubset.map((x, i) => <div key={x.id} className={'text-info ' + styles.icon}>
    <span className="fa fa-user-circle"></span>
  </div>)

  const userNames = users.map(x => <div key={x.id} className=''>
    <span className="fa fa-user mr-1 text-muted "></span>
    <span>{x.first_name} {x.last_name} ({x.username})</span>
  </div>)

  return <div className={styles.icons}>
    <span className="position-relative pl-2 pb-4">
      <div className={'card ' + styles.userNames}>
        {userNames}
      </div>
    </span>
    {userIcons}
    <span className={"fa fa-plus text-muted mr-2" + (users.length <= 3 ? ' d-none' : '')}></span>
    <span className="ml-2 text-muted">
      {users.length} looking this page
    </span>
  </div>
}

ActiveUsers.propTypes = {
  users: PropTypes.arrayOf(PropTypes.shape({
    id: PropTypes.number,
    username: PropTypes.string,
    first_name: PropTypes.string,
    last_name: PropTypes.string
  }))
}
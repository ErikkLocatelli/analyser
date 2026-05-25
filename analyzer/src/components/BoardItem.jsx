import React from 'react'

import styles from "../styles/BoardItem.module.css"

const BoardItem = ({left, right, tag = null}) => {
  return (
    <div className={styles.board}>
      <p>{left}</p>
      <div className={styles.right}>
          <p>{right}</p>
          {tag && <div className={styles.tag}>{tag}</div>}
      </div>
    </div>
  )
}

export default BoardItem

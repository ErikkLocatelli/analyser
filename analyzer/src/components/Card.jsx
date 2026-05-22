import React from 'react'

import styles from '../styles/Card.module.css'

const Card = ({title, number, subtitle = ""}) => {
  return (
    <div className={styles.card}>
      <p className={styles.p}>{title}</p>
      <p className={styles.number}>{number}</p>
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
    </div>
  )
}

export default Card

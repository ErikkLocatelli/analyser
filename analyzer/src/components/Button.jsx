import React from 'react'

import styles from '../styles/Button.module.css'

const Button = ({text, icon, ...props}) => {
  return (
    <button className={styles.button} {...props}>
      <span className="material-symbols-outlined">{icon}</span>
      {text}
    </button>
  )
}

export default Button

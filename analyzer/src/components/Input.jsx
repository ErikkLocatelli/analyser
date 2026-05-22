import React from 'react'

import styles from '../styles/Input.module.css'

const Input = ({...props}) => {
  return (
    <input className={styles.input} {...props}></input>
  )
}

export default Input

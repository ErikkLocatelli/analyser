import React from 'react'

import styles from '../styles/User.module.css'

const User = ({ data }) => {
  return (
    <div className={styles.user}>
      <div className={styles.container}>
          <div className={styles.circle}>
            <img src={data.owner.avatar_url}/>
          </div>
          <div className={styles.infos}>
            <p>{data?.name}</p>
            <span>{`github.com / ${data?.owner?.login}  · criado em ${new Date(data.created_at).toLocaleDateString('pt-BR')}`}</span>
          </div>
      </div>
      <div className={styles.public}>
        publico
      </div>
    </div>
  )
}

export default User

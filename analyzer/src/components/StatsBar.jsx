import React from 'react'

import styles from '../styles/StatsBar.module.css'


const StatsBar = ({analise ,progress}) => {


    const switchProgressBar = () => {
        if (progress >= 90) return "#3d7a52"
        if (progress >= 67) return "#5a9e6f"
        if (progress >= 54) return "#7dba92"

        return "#a0c9ab"
    }



  return (
    <div className={styles.stats}>
      <div className={styles.label}>
        <span>{analise}</span>
        <span>{`${progress}%`}</span>
      </div>
       <div
        style={{
          width: '100%',
          height: '10px',
          background: '#e8f3eb',
          borderRadius: '8px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${progress}%`,
            height: '100%',
            background: `${switchProgressBar()}`,
            transition: '0.3s',
          }}
        />
      </div>
    </div>
  )
}

export default StatsBar

import React, { Children } from 'react'

import StatsBar from './StatsBar'

import styles from '../styles/Stats.module.css'

const Stats = ({icon, text, level, children}) => {

    const changeColor = () => {
        if(level === "LOW") return "#c0ddc8"
        if (level === "MODERATE") return "#b99425a4"
        if (level === "HIGH" || level === "CRITICAL") return  "#e76864c5"
    }

    const changeLetter = () => {
        if(level === "LOW") return "#5A9E6F"
        if (level === "MODERATE") return "#705915"
        if (level === "HIGH") return  "#af2622"
    }
  return (
    <section className={styles.stats}>
        <div className={styles.type}>
            <div className={styles.right}>
                <span className="material-symbols-outlined">{icon}</span>
                <p>{text}</p>
            </div>
            <div className={styles.tag}
                style={{
                    background: changeColor(), 
                    color: changeLetter(), 
                    border: changeColor()
                }}
            >
                {level}
            </div>
        </div>
        <div className={styles.board}>
            {children}
        </div>
    
    </section>
  )
}

export default Stats

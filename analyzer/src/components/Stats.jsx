import React from 'react'

import StatsBar from './StatsBar'
import styles from '../styles/Stats.module.css'

const Stats = () => {

    const analises = [{
        analise: " conformidade lint", 
        porcent: 91
    },{
        analise: "cobertura de testes", 
        porcent: 82
    },{
       analise: "documentação", 
       porcent: 67 
    }, {
       analise: "complexidade", 
       porcent: 54
    }, {
       analise: "duplicação", 
       porcent: 12
    }     
]



  return (
    <section className={styles.stats}>
        <p className={styles.p}>Estísticas analisadas</p>
        <div className={styles.div}>
            {analises.map(item => (
                <StatsBar key={item.porcent} analise={item.analise} progress={item.porcent}/>
            ))}
        </div>
    </section>
  )
}

export default Stats

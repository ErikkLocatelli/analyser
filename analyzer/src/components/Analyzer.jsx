import React, { useState } from 'react'
import { use } from 'react'

import styles from '../styles/Analyzer.module.css'

import Input from './Input'
import Button from './Button'
import User from './User'
import Card from './Card'
import Stats from './Stats'

const Analyzer = () => {

  const [url, setUrl] = useState('')
  const [data, setData] = useState(null)
  const [analyze, setAnalzyse] = useState(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()

    const apiUrl = replaceUrl(url)
    
    try {
        if (data) { 
          setData(null)
          setAnalzyse(null)
        }
          setError(null)

        const response = await fetch(apiUrl)
        if(!response.ok) throw new Error("Repositório não encontrado")
        
        const json = await response.json()
        setData(json)
    } catch (err) {
        setError(err.message)
    }
  }


  const replaceUrl = (url) => {
        const githubUrl = url.replace('https://github.com/', '').split('/')
    
        const owner = githubUrl[0]
        const repo = githubUrl[1]
    
        const apiUrl = `https://api.github.com/repos/${owner}/${repo}`
        return apiUrl
    }  

  const handleAnalyze = async() => {
    

    try {

      setLoading(true)

      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url
        }),
      })

      if(!response.ok) {
        throw new Error("Não foi possível analisar esse repositório")
      }

      setAnalzyse(true)
      const json = await response.json()
      console.log(json)
      
    } catch (err) {
      setError(err.message)
    }

    finally {
      setLoading(false)

    }

  }

  return (
    <div className={styles.analyzer}>
        <div>
          <p className={styles.p}>Cole a URL de qualquer repositório público para gerar um relatório de qualidade de código.</p>
          <form onSubmit={handleSubmit} className={styles.form}>
            <Input
              type="text"
              value={url}
              onChange={({ target }) => setUrl(target.value)}
              placeholder={"https://github.com/usuario/repositorio"}
            />
            <Button text={"Buscar"} icon={"search"} type='submit'/>
          </form>
        </div>
        {data && <div className={styles.animeLeft}>
            <User data={data}/>
            <div className={styles.card}>
                <Card title={"Estrelas"} number={data?.stargazers_count} />
                <Card title={"Forks"} number={data?.forks_count}/>
                <Card title={"ISSUES ABERTAS"} number={data?.open_issues} />
                <Card title={"Linguagem"} number={data?.language} subtitle={"Principal"}/>
            </div>
          </div>}

        {data && !analyze && 
          <Button 
            style={{margin: 'auto', marginTop: "2.5rem"}}
            text={"Analise completa"} 
            icon={"text_compare"}
            onClick={() => handleAnalyze()} />
        }  

        {analyze && 
          <div className={styles.animeDown}>
            <Stats />
            <Button
                style={{margin: 'auto', marginTop: "15px"}}
                text={"Baixar Relatório"}
                icon={"download"}/>
          </div>
        }
    </div>
  )
}

export default Analyzer
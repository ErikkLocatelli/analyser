import React, { useState } from 'react'
import { use } from 'react'

import styles from '../styles/Analyzer.module.css'

import Input from './Input'
import Button from './Button'
import User from './User'
import Card from './Card'
import Stats from './Stats'
import BoardItem from './BoardItem'
import StatsBar from './StatsBar'

const Analyzer = () => {

  const [url, setUrl] = useState('')
  const [data, setData] = useState(null)
  const [analyze, setAnalzyse] = useState(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(false)
  const [full, setFull] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()

    const apiUrl = replaceUrl(url)
    
    try {
        if (data) { 
          setData(null)
          setAnalzyse(null)
          setFull(null)
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
      setError(null)
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
      setFull(json)
      
    } catch (err) {
      setError(err.message)
    }

    finally {
      setLoading(false)

    }

  }

  const handleReport = async () => {

    setLoading(true)
    setError(false)
    
      try {
        
        const response = await fetch('http://localhost:8000/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            url: url,
            name: data?.name,
            result1: full?.result1,
            result3: full?.result3,
            cbo_all: full?.result1?.cbo,
            cc_all: full?.result1?.cyclomatic_complexity
          })
        })

        if(!response.ok) throw new Error("Não foi possível criar o relatório")

        const html = await response.text()

        const blob = new Blob([html], { type: 'text/html' })
        const blobUrl = URL.createObjectURL(blob)
        window.open(blobUrl, '_blank')

      } catch (err) {
        setError(err.message)
      }

      finally {
          setLoading(false)
        }
  }

  console.log(full)

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
            <Button text={"Buscar"} icon={"search"} type='submit' disabled={loading}/>
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

        {data && data.language === "Java" && !analyze && 
          <Button 
            style={{margin: 'auto', marginTop: "2.5rem"}}
            text={"Analise completa"} 
            icon={"text_compare"}
            onClick={() => handleAnalyze()} 
            disabled={loading}
            />
        }  

        {full && <div className={styles.animeDown}>

            <Stats text={"Complexidade ciclomática"} icon={"account_tree"} level={"LOW"}>
              <div className={styles.stats}>
                <BoardItem 
                  left={"Método mais complexo"} 
                  right={full?.result1?.summary.cc_worst.class + " - CC " + full?.result1?.summary.cc_worst.complexity} 
                  tag={full?.result1?.summary.cc_worst.score}/>
                <div className={styles.score}>
                  <p>Distribuição por score</p>
                  <section>
                    <div>
                      <StatsBar analise={"LOW"} progress={full?.result1?.summary.cc_distribution.LOW} total={full?.result1?.summary.total_methods} />
                      <StatsBar analise={"MODERATE"} progress={full?.result1?.summary.cc_distribution.MODERATE} total={full?.result1?.summary.total_methods}/>
                      <StatsBar analise={"HIGH"} progress={full?.result1?.summary.cc_distribution.HIGH} total={full?.result1?.summary.total_methods}/>
                      <StatsBar analise={"CRITICAL"} progress={full?.result1?.summary.cc_distribution?.CRITICAL} total={full?.result1?.summary.total_methods}/>
                    </div>
                  </section>
                </div>
              </div>
            </Stats>

            <Stats text={"Acoplamento entre objetos (cbo)"} icon={"hub"} level={full?.result1?.summary.cbo_avg}>
              <BoardItem left={"Média geral"} right={full?.result1?.summary.cbo_avg}/>
              <BoardItem left={"Arquivos críticos"} right={full?.result1?.flagged_files.high_cbo.length + " arquivos"}/>
            </Stats>

            <Stats text={"Duplicação de código"} icon={"content_copy"} level={full?.result1?.duplication.score}>
              <BoardItem left={"Blocos duplicados"} right={full?.result1?.duplication.total_duplicate_blocks}/>
              <BoardItem left={"Score total"} right={full?.result1?.duplication.duplication_ratio + " pts"}/>
            </Stats>

            <Stats text={"Cobertura de testes"} icon={"labs"} level={full?.result3?.overall_score}>
              
              <div className={styles.board}>
                <StatsBar analise={"Cobertura estimada"} progress={full?.result3?.overall_coverage_pct} total={100}/>
                
                <div className={styles.boardItem}>
                  <BoardItem left={"Com testes"} right={full?.result3?.summary.classes_with_tests}/>
                  <BoardItem left={"Sem testes"} right={full?.result3?.summary.classes_without_tests}/>
                </div>
              </div>
            </Stats>

            <div className={styles.general}>
                <p>Visão geral</p>
                <div className={styles.card}>
                  <Card title={"Arquivos analisados"} number={full?.result1.summary.total_files} />
                  <Card title={"Métodos analisados"} number={full?.result1.summary.total_methods}/>
                  <Card title={"CC médio"} number={full?.result1.summary.cc_avg} subtitle={"complexidade ciclomática"}/>
                  <Card title={"CBO médio"} number={full?.result1.summary.cbo_avg} subtitle={"acoplamento entre objetos"}/>
                </div>
            </div>


            <Button
                style={{margin: 'auto', marginTop: "15px", marginBottom: "2em"}}
                text={"Baixar Relatório"}
                icon={"download"}
                onClick={() => handleReport()}
                />
          </div> }
        
    </div>
  )
}

export default Analyzer
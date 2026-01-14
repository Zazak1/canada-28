import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { fetchPrediction, fetchAlgorithms, fetchAllPredictions, fetchAlgorithmHistory, fetchAlgorithmsStats } from '../api'

const PredictionPanel = () => {
    const [activeTab, setActiveTab] = useState('forecast')
    const [algorithms, setAlgorithms] = useState([])
    const [selectedAlgo, setSelectedAlgo] = useState('algo1')
    const [prediction, setPrediction] = useState(null)
    const [allPredictions, setAllPredictions] = useState([])
    const [showAll, setShowAll] = useState(false)
    const [algoHistory, setAlgoHistory] = useState(null)
    const [algoStats, setAlgoStats] = useState([])

    const bsMap = { "Big": "大", "Small": "小" }
    const oeMap = { "Odd": "单", "Even": "双" }

    // 加载算法列表
    useEffect(() => {
        fetchAlgorithms().then(res => {
            if (Array.isArray(res)) setAlgorithms(res)
        })
        fetchAlgorithmsStats().then(res => {
            if (Array.isArray(res)) setAlgoStats(res)
        })
    }, [])

    // 加载选中算法的预测和历史
    const loadAlgoData = useCallback(async () => {
        try {
            const [predRes, histRes] = await Promise.all([
                fetchPrediction(selectedAlgo),
                fetchAlgorithmHistory(selectedAlgo, 20)
            ])
            
            if (predRes && predRes.big_small) {
                setPrediction({
                    ...predRes,
                    big_small: bsMap[predRes.big_small] || predRes.big_small,
                    odd_even: oeMap[predRes.odd_even] || predRes.odd_even,
                })
            }
            
            if (histRes) {
                setAlgoHistory(histRes)
            }
        } catch (e) {
            console.error("Failed to load algo data", e)
        }
    }, [selectedAlgo])

    useEffect(() => {
        loadAlgoData()
        const interval = setInterval(loadAlgoData, 30000)
        return () => clearInterval(interval)
    }, [loadAlgoData])

    // 刷新统计
    useEffect(() => {
        const interval = setInterval(() => {
            fetchAlgorithmsStats().then(res => {
                if (Array.isArray(res)) setAlgoStats(res)
            })
        }, 60000)
        return () => clearInterval(interval)
    }, [])

    const loadAllPredictions = async () => {
        const res = await fetchAllPredictions()
        if (Array.isArray(res)) {
            setAllPredictions(res.map(p => ({
                ...p,
                big_small_cn: bsMap[p.big_small] || p.big_small,
                odd_even_cn: oeMap[p.odd_even] || p.odd_even,
            })))
            setShowAll(true)
        }
    }

    const getAlgoStats = (algoId) => {
        return algoStats.find(s => s.algorithm_id === algoId)?.stats || {}
    }

    // 找出准确率最高的算法
    const getBestAlgoId = () => {
        if (!algoStats.length) return null
        const verified = algoStats.filter(a => a.stats.verified > 0)
        if (!verified.length) return null
        return verified.reduce((best, curr) => 
            curr.stats.accuracy > best.stats.accuracy ? curr : best
        ).algorithm_id
    }
    const bestAlgoId = getBestAlgoId()

    return (
        <div>
            {/* Algorithm Selector */}
            <div className="px-6 py-4 bg-gradient-to-r from-slate-50 to-slate-100 border-b border-slate-200">
                <div className="flex flex-wrap gap-3">
                    {algoStats.map(algo => (
                        <button
                            key={algo.algorithm_id}
                            onClick={() => { setSelectedAlgo(algo.algorithm_id); setShowAll(false); }}
                            className={`relative px-5 py-3 rounded-xl font-semibold transition-all ${
                                selectedAlgo === algo.algorithm_id
                                    ? 'bg-blue-600 text-white shadow-lg'
                                    : 'bg-white text-slate-700 hover:shadow-md border border-slate-200'
                            }`}
                        >
                            {algo.algorithm_name}
                            {bestAlgoId === algo.algorithm_id && (
                                <span className={`absolute -top-2 -right-2 px-1.5 py-0.5 text-xs rounded-full ${
                                    selectedAlgo === algo.algorithm_id
                                        ? 'bg-yellow-400 text-yellow-900'
                                        : 'bg-yellow-400 text-yellow-900'
                                }`}>
                                    推荐
                                </span>
                            )}
                        </button>
                    ))}
                    <button
                        onClick={loadAllPredictions}
                        className={`px-5 py-3 rounded-xl font-semibold transition-all ${
                            showAll
                                ? 'bg-purple-600 text-white shadow-lg'
                                : 'bg-white text-purple-600 hover:shadow-md border border-purple-200'
                        }`}
                    >
                        📊 对比全部
                    </button>
                    <Link
                        to="/history"
                        className="px-5 py-3 rounded-xl font-semibold transition-all bg-white text-blue-600 hover:shadow-md border border-blue-200 inline-flex items-center gap-2"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        查看开奖公告
                    </Link>
                </div>
            </div>

            {/* Current Prediction */}
            {!showAll && prediction && (
                <div className="p-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-slate-100">
                    <div className="flex items-center gap-6">
                        <span className="text-sm font-medium text-slate-500">下期预测:</span>
                        <div className="flex gap-3">
                            <span className="px-5 py-2.5 rounded-xl bg-orange-100 text-orange-700 font-bold text-xl shadow-sm">
                                {prediction.big_small}
                            </span>
                            <span className="px-5 py-2.5 rounded-xl bg-blue-100 text-blue-700 font-bold text-xl shadow-sm">
                                {prediction.odd_even}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* All Predictions Comparison */}
            {showAll && allPredictions.length > 0 && (
                <div className="p-6 bg-gradient-to-r from-purple-50 to-pink-50 border-b border-slate-100">
                    <h3 className="text-sm font-semibold text-slate-700 mb-4">📊 全部算法预测对比</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {allPredictions.map((p, i) => (
                            <div key={i} className={`relative bg-white rounded-xl p-4 shadow-sm border ${
                                bestAlgoId === p.algorithm ? 'border-yellow-400 ring-2 ring-yellow-200' : 'border-slate-100'
                            }`}>
                                <div className="flex items-center justify-between mb-3">
                                    <span className="font-semibold text-slate-700">{p.algorithm_name}</span>
                                    {bestAlgoId === p.algorithm && (
                                        <span className="text-xs px-2 py-0.5 bg-yellow-400 text-yellow-900 rounded-full font-semibold">
                                            推荐
                                        </span>
                                    )}
                                </div>
                                <div className="flex gap-2">
                                    <span className="px-3 py-1 rounded bg-orange-100 text-orange-700 font-bold text-sm">
                                        {p.big_small_cn}
                                    </span>
                                    <span className="px-3 py-1 rounded bg-blue-100 text-blue-700 font-bold text-sm">
                                        {p.odd_even_cn}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Algorithm History Table */}
            {!showAll && algoHistory && (
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="text-xs text-slate-400 border-b border-slate-100 bg-slate-50/50">
                                <th className="px-6 py-3 font-medium">期号</th>
                                <th className="px-6 py-3 font-medium">开奖结果</th>
                                <th className="px-6 py-3 font-medium">预测</th>
                                <th className="px-6 py-3 font-medium text-center">状态</th>
                            </tr>
                        </thead>
                        <tbody className="text-sm">
                            {algoHistory.history.map((row, idx) => (
                                <tr key={row.issue || idx} className="hover:bg-slate-50 transition-colors border-b border-slate-50">
                                    <td className="px-6 py-4 font-mono text-slate-600">{row.issue}</td>
                                    <td className="px-6 py-4">
                                        {row.actual ? (
                                            <>
                                                <span className="font-mono font-medium text-slate-800">
                                                    {row.actual.numbers}= {row.actual.sum}
                                                </span>
                                                <span className={`ml-2 px-2 py-0.5 text-xs rounded-md ${
                                                    row.actual.sum > 13 ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
                                                }`}>
                                                    {row.actual.big_small}
                                                </span>
                                                <span className={`ml-1 px-2 py-0.5 text-xs rounded-md ${
                                                    row.actual.sum % 2 === 0 ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
                                                }`}>
                                                    {row.actual.odd_even}
                                                </span>
                                            </>
                                        ) : (
                                            <span className="text-slate-300">待开奖</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex gap-2">
                                            <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                                                row.prediction.bs_correct === true ? 'bg-green-100 text-green-700' :
                                                row.prediction.bs_correct === false ? 'bg-red-100 text-red-700' :
                                                'bg-orange-100 text-orange-700'
                                            }`}>
                                                {row.prediction.big_small}
                                            </span>
                                            <span className={`px-2.5 py-1 rounded text-xs font-bold ${
                                                row.prediction.oe_correct === true ? 'bg-green-100 text-green-700' :
                                                row.prediction.oe_correct === false ? 'bg-red-100 text-red-700' :
                                                'bg-blue-100 text-blue-700'
                                            }`}>
                                                {row.prediction.odd_even || '-'}
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-center">
                                        {row.prediction.is_correct === true && (
                                            <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-600">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                                                </svg>
                                            </div>
                                        )}
                                        {row.prediction.is_correct === false && (
                                            <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-100 text-red-600">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                                </svg>
                                            </div>
                                        )}
                                        {row.prediction.is_correct === null && (
                                            <span className="text-slate-300 text-xs">-</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    )
}

export default PredictionPanel

import React, { useState, useEffect, useCallback } from 'react'
import { fetchHistory } from '../api'

const PredictionTable = () => {
    const [history, setHistory] = useState([])

    const load = useCallback(async () => {
        try {
            const res = await fetchHistory()
            if (res && res.data) {
                const formatted = res.data.map(item => ({
                    ...item,
                    result: `${item.code1}+${item.code2}+${item.code3}= ${item.sum_val}`,
                    sum: item.sum_val,
                }))
                setHistory(formatted)
            }
        } catch (e) {
            console.error("Failed to fetch history", e)
        }
    }, [])

    useEffect(() => {
        // 初始加载
        load()

        // 每20秒刷新一次历史数据
        const interval = setInterval(load, 20000)
        return () => clearInterval(interval)
    }, [load])

    return (
        <table className="w-full text-left border-collapse">
            <thead>
                <tr className="text-xs text-slate-400 border-b border-slate-100">
                    <th className="px-6 py-3 font-medium">期号</th>
                    <th className="px-6 py-3 font-medium">开奖结果</th>
                    <th className="px-6 py-3 font-medium">预测内容</th>
                    <th className="px-6 py-3 font-medium text-center">状态</th>
                </tr>
            </thead>
            <tbody className="text-sm">
                {history.map((row, idx) => (
                    <tr key={row.issue || idx} className="hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0">
                        <td className="px-6 py-4 font-mono text-slate-600">{row.issue}</td>
                        <td className="px-6 py-4">
                            <span className="font-mono font-medium text-slate-800">{row.result}</span>
                            <span className={`ml-2 px-2 py-0.5 text-xs rounded-md ${row.sum > 13 ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'}`}>
                                {row.sum > 13 ? '大' : '小'}
                            </span>
                            <span className={`ml-1 px-2 py-0.5 text-xs rounded-md ${row.sum % 2 === 0 ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'}`}>
                                {row.sum % 2 === 0 ? '双' : '单'}
                            </span>
                        </td>
                        <td className="px-6 py-4">
                            {row.prediction ? (
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
                            ) : (
                                <span className="text-slate-300 text-xs">-</span>
                            )}
                        </td>
                        <td className="px-6 py-4 text-center">
                            {row.prediction && row.prediction.is_correct === true && (
                                <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-green-100 text-green-600">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                                    </svg>
                                </div>
                            )}
                            {row.prediction && row.prediction.is_correct === false && (
                                <div className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-red-100 text-red-600">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                                    </svg>
                                </div>
                            )}
                        </td>
                    </tr>
                ))}
            </tbody>
        </table>
    )
}

export default PredictionTable

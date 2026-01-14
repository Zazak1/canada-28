import React, { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { fetchHistory } from '../api'

const HistoryPage = () => {
    const [history, setHistory] = useState([])
    const [loading, setLoading] = useState(true)

    const load = useCallback(async () => {
        try {
            const res = await fetchHistory(100)
            if (res && res.data) {
                setHistory(res.data)
            }
        } catch (e) {
            console.error("Failed to fetch history", e)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        load()
        // 每30秒刷新一次
        const interval = setInterval(load, 30000)
        return () => clearInterval(interval)
    }, [load])

    return (
        <div className="min-h-screen bg-slate-50">
            <div className="max-w-6xl mx-auto p-4 md:p-8">
                {/* 返回按钮 */}
                <div className="mb-6">
                    <Link 
                        to="/" 
                        className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-800 transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                        </svg>
                        返回首页
                    </Link>
                </div>

                {/* 开奖公告 */}
                <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
                        <h1 className="text-2xl font-bold text-slate-800">开奖公告</h1>
                        <span className="text-sm text-slate-400">共 {history.length} 期</span>
                    </div>
                    
                    {loading ? (
                        <div className="p-8 text-center text-slate-400">加载中...</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead className="bg-slate-50">
                                    <tr className="text-xs text-slate-500">
                                        <th className="px-6 py-3 font-medium">期号</th>
                                        <th className="px-6 py-3 font-medium">开奖号码</th>
                                        <th className="px-6 py-3 font-medium text-center">和值</th>
                                        <th className="px-6 py-3 font-medium text-center">大小</th>
                                        <th className="px-6 py-3 font-medium text-center">单双</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm">
                                    {history.map((row, idx) => (
                                        <tr key={row.issue || idx} className="hover:bg-slate-50 transition-colors border-b border-slate-50 last:border-0">
                                            <td className="px-6 py-3 font-mono text-slate-600">{row.issue}</td>
                                            <td className="px-6 py-3">
                                                <div className="flex items-center gap-1">
                                                    <span className="w-7 h-7 flex items-center justify-center bg-blue-500 text-white rounded-full text-xs font-bold">
                                                        {row.code1}
                                                    </span>
                                                    <span className="text-slate-300">+</span>
                                                    <span className="w-7 h-7 flex items-center justify-center bg-blue-500 text-white rounded-full text-xs font-bold">
                                                        {row.code2}
                                                    </span>
                                                    <span className="text-slate-300">+</span>
                                                    <span className="w-7 h-7 flex items-center justify-center bg-blue-500 text-white rounded-full text-xs font-bold">
                                                        {row.code3}
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-3 text-center">
                                                <span className="w-8 h-8 inline-flex items-center justify-center bg-orange-500 text-white rounded-full font-bold">
                                                    {row.sum_val}
                                                </span>
                                            </td>
                                            <td className="px-6 py-3 text-center">
                                                <span className={`px-3 py-1 rounded text-xs font-bold ${
                                                    row.sum_val >= 14 ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
                                                }`}>
                                                    {row.sum_val >= 14 ? '大' : '小'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-3 text-center">
                                                <span className={`px-3 py-1 rounded text-xs font-bold ${
                                                    row.sum_val % 2 === 0 ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
                                                }`}>
                                                    {row.sum_val % 2 === 0 ? '双' : '单'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default HistoryPage

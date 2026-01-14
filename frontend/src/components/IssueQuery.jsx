import React, { useState } from 'react'
import { queryIssue } from '../api'

const IssueQuery = () => {
    const [issue, setIssue] = useState('')
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleQuery = async () => {
        if (!issue.trim()) {
            setError('请输入期号')
            return
        }
        
        setLoading(true)
        setError('')
        setResult(null)
        
        try {
            const res = await queryIssue(issue.trim())
            if (res.success) {
                setResult(res.data)
            } else {
                setError(res.message || '未找到记录')
            }
        } catch (e) {
            setError('查询失败，请稍后重试')
        } finally {
            setLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleQuery()
        }
    }

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-4">期号查询</h2>
            
            {/* 查询输入 */}
            <div className="flex gap-3 mb-4">
                <input
                    type="text"
                    value={issue}
                    onChange={(e) => setIssue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="请输入期号，如 3383954"
                    className="flex-1 px-4 py-2.5 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-slate-700"
                />
                <button
                    onClick={handleQuery}
                    disabled={loading}
                    className="px-6 py-2.5 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-blue-300 transition-colors font-medium"
                >
                    {loading ? '查询中...' : '查询'}
                </button>
            </div>

            {/* 错误提示 */}
            {error && (
                <div className="p-4 bg-red-50 text-red-600 rounded-lg mb-4">
                    {error}
                </div>
            )}

            {/* 查询结果 */}
            {result && (
                <div className="p-5 bg-slate-50 rounded-xl">
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <span className="text-sm text-slate-500">期号</span>
                            <p className="text-lg font-mono font-semibold text-slate-800">{result.issue}</p>
                        </div>
                        <div>
                            <span className="text-sm text-slate-500">开奖时间</span>
                            <p className="text-sm text-slate-700">{result.open_time || '-'}</p>
                        </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-slate-200">
                        <span className="text-sm text-slate-500">开奖号码</span>
                        <div className="flex items-center gap-3 mt-2">
                            <div className="flex gap-2">
                                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full font-bold">
                                    {result.code1}
                                </span>
                                <span className="text-2xl text-slate-400">+</span>
                                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full font-bold">
                                    {result.code2}
                                </span>
                                <span className="text-2xl text-slate-400">+</span>
                                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full font-bold">
                                    {result.code3}
                                </span>
                            </div>
                            <span className="text-2xl text-slate-400">=</span>
                            <span className="w-12 h-12 flex items-center justify-center bg-orange-500 text-white rounded-full font-bold text-xl">
                                {result.sum_val}
                            </span>
                        </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-slate-200">
                        <span className="text-sm text-slate-500">结果</span>
                        <div className="flex gap-3 mt-2">
                            <span className={`px-4 py-2 rounded-lg text-sm font-bold ${
                                result.type_dx === '大' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
                            }`}>
                                {result.type_dx}
                            </span>
                            <span className={`px-4 py-2 rounded-lg text-sm font-bold ${
                                result.type_ds === '双' ? 'bg-red-100 text-red-600' : 'bg-slate-100 text-slate-600'
                            }`}>
                                {result.type_ds}
                            </span>
                            <span className="px-4 py-2 bg-purple-100 text-purple-600 rounded-lg text-sm font-bold">
                                {result.type_zh}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default IssueQuery

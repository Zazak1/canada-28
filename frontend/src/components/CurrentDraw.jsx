import React, { useState, useEffect, useCallback } from 'react'
import CountDown from './CountDown'
import { fetchGameStatus } from '../api'

const CurrentDraw = () => {
    const [data, setData] = useState(null)
    const [lastIssue, setLastIssue] = useState(null)

    const updateData = useCallback((latest) => {
        if (!latest) return
        
        const rawNums = latest?.numbers || latest?.data?.numbers
        if (rawNums && rawNums.length === 3) {
            const nums = rawNums.map(n => Number(n))
            const sum = Number(latest.sum ?? latest.data?.sum ?? nums.reduce((a, b) => a + b, 0))
            const issue = latest.current_stage || latest.data?.current_stage || latest.next_stage
            
            // 检测是否有新开奖
            if (issue !== lastIssue) {
                setLastIssue(issue)
                // 可以在这里触发其他刷新逻辑
            }
            
            setData({
                issue,
                nums,
                sum,
                tags: latest.type_zh ? [latest.type_zh] : []
            })
        }
    }, [lastIssue])

    useEffect(() => {
        // 初始加载
        const load = async () => {
            try {
                const latest = await fetchGameStatus()
                updateData(latest)
            } catch (e) {
                console.error("Failed to load latest draw", e)
            }
        }
        load()

        // 每15秒刷新一次开奖数据
        const interval = setInterval(load, 15000)
        return () => clearInterval(interval)
    }, [updateData])

    // 倒计时组件回调 - 有新数据时更新
    const handleNewDraw = useCallback((res) => {
        updateData(res)
    }, [updateData])

    if (!data) return <div className="p-6 text-center text-slate-400">Loading...</div>

    return (
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-50 rounded-full flex items-center justify-center text-2xl">🍁</div>
                <div>
                    <h1 className="text-xl font-bold text-slate-800">加拿大28</h1>
                    <p className="text-xs text-slate-400 mt-1">期号: <span className="font-mono text-slate-600">{data.issue}</span></p>
                </div>
            </div>

            <div className="flex items-center gap-2">
                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full font-bold shadow-blue-200 shadow-lg">{data.nums[0]}</span>
                <span className="text-slate-300 font-light">+</span>
                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full font-bold shadow-blue-200 shadow-lg">{data.nums[1]}</span>
                <span className="text-slate-300 font-light">+</span>
                <span className="w-10 h-10 flex items-center justify-center bg-blue-500 text-white rounded-full font-bold shadow-blue-200 shadow-lg">{data.nums[2]}</span>
                <span className="text-slate-300 font-light">=</span>
                <span className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-red-500 to-red-600 text-white rounded-full font-bold text-xl shadow-red-200 shadow-lg ring-4 ring-red-50">{data.sum}</span>
            </div>

            <div className="text-center">
                <p className="text-xs text-slate-400 mb-1">下期倒计时</p>
                <CountDown onNewDraw={handleNewDraw} />
            </div>
        </div>
    )
}

export default CurrentDraw

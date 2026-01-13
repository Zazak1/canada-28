import React, { useState, useEffect, useCallback } from 'react'
import { fetchGameStatus } from '../api'

const CountDown = ({ onNewDraw }) => {
    const [seconds, setSeconds] = useState(0)
    const [loading, setLoading] = useState(false)

    const load = useCallback(async () => {
        if (loading) return
        setLoading(true)
        try {
            const res = await fetchGameStatus()
            const nextSeconds = Number(res?.remaining_seconds ?? res?.djs ?? 0)
            if (!Number.isNaN(nextSeconds)) {
                setSeconds(Math.max(0, nextSeconds))
            }
            // 通知父组件有新数据
            if (onNewDraw) onNewDraw(res)
        } catch (e) {
            console.error("Failed to fetch countdown", e)
        } finally {
            setLoading(false)
        }
    }, [loading, onNewDraw])

    useEffect(() => {
        // 初始加载
        load()

        // 每秒递减
        const tickInterval = setInterval(() => {
            setSeconds(prev => {
                if (prev <= 1) {
                    // 倒计时结束，立即刷新
                    load()
                    return 0
                }
                return prev - 1
            })
        }, 1000)

        // 每10秒强制同步一次（防止时间漂移）
        const syncInterval = setInterval(() => {
            load()
        }, 10000)

        return () => {
            clearInterval(tickInterval)
            clearInterval(syncInterval)
        }
    }, [])

    const format = (s) => {
        const m = Math.floor(s / 60)
        const sec = s % 60
        return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`
    }

    return (
        <div className="font-mono text-3xl font-bold text-slate-700 tracking-wider">
            {format(seconds)}
        </div>
    )
}

export default CountDown

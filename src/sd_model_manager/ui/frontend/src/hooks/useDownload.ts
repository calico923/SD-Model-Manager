import { useState, useEffect } from 'react'

interface ProgressData {
  type: string
  data?: {
    task_id: string
    filename: string
    percentage: number
    status: string
    error_message?: string
  }
  message?: string
}

export const useDownload = () => {
  const [progress, setProgress] = useState(0)
  const [isDownloading, setIsDownloading] = useState(false)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [filename, setFilename] = useState<string>('')
  const [status, setStatus] = useState<'idle' | 'downloading' | 'completed' | 'failed'>('idle')
  const [error, setError] = useState<string | undefined>(undefined)  // Phase 2.12: null → undefined
  const [_ws, setWs] = useState<WebSocket | null>(null)  // Phase 2.12: ws → _ws (未使用)

  const startDownload = async (url: string) => {  // Phase 2.12: filename削除
    setIsDownloading(true)
    setProgress(0)
    setStatus('downloading')
    setError(undefined)
    setFilename('')  // WebSocketレスポンスから設定される

    try {
      // POST /api/download (Phase 2.12: filenameなし)
      // Phase 2.15: 相対パスに変更（ポートハードコード削除）
      const response = await fetch('/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })  // Phase 2.12: filenameフィールド削除
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const { task_id } = await response.json()
      setTaskId(task_id)
      console.log('Download started with task_id:', task_id)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start download')
      setStatus('failed')
      setIsDownloading(false)
    }
  }

  // WebSocket でプログレス監視
  useEffect(() => {
    if (!taskId) return

    // Phase 2.15: WebSocket URLを動的に構築（ポートハードコード削除）
    const wsUrl = new URL(`/ws/download/${taskId}`, window.location.origin)
    wsUrl.protocol = wsUrl.protocol === 'https:' ? 'wss:' : 'ws:'
    console.log('Connecting to WebSocket:', wsUrl.toString())

    const socket = new WebSocket(wsUrl.toString())

    socket.onopen = () => {
      console.log('WebSocket connected')
      setWs(socket)
    }

    socket.onmessage = (event) => {
      try {
        const data: ProgressData = JSON.parse(event.data)
        console.log('Received message:', data)

        if (data.type === 'progress' && data.data) {
          setProgress(data.data.percentage)
          setStatus(data.data.status as 'downloading' | 'completed' | 'failed')

          // Phase 2.12: WebSocketレスポンスからfilenameを設定
          if (data.data.filename) {
            setFilename(data.data.filename)
          }

          if (data.data.error_message) {
            setError(data.data.error_message)
          }

          if (data.data.status === 'completed') {
            setIsDownloading(false)
            socket.close()
          } else if (data.data.status === 'failed') {
            setIsDownloading(false)
            socket.close()
          }
        } else if (data.type === 'error') {
          setError(data.message || 'WebSocket error')
          setStatus('failed')
          setIsDownloading(false)
          socket.close()
        }
      } catch (err) {
        console.error('Error parsing WebSocket message:', err)
      }
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setError('Connection error')
      setStatus('failed')
      setIsDownloading(false)
    }

    socket.onclose = () => {
      console.log('WebSocket closed')
      setWs(null)
    }

    return () => {
      if (socket.readyState === WebSocket.OPEN) {
        socket.close()
      }
    }
  }, [taskId])

  return {
    startDownload,
    progress,
    isDownloading,
    filename,
    status,
    error,
    taskId,
  }
}

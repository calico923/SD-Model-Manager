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
  const [error, setError] = useState<string | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)

  const startDownload = async (url: string, fname: string) => {
    setIsDownloading(true)
    setProgress(0)
    setStatus('downloading')
    setError(null)
    setFilename(fname)

    try {
      // POST /api/download
      const response = await fetch('http://localhost:8000/api/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, filename: fname })
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

    const wsUrl = `ws://localhost:8000/ws/download/${taskId}`
    console.log('Connecting to WebSocket:', wsUrl)

    const socket = new WebSocket(wsUrl)

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

import { useState } from 'react'

interface DownloadFormProps {
  onSubmit: (url: string) => void  // Phase 2.12: filename削除
  disabled?: boolean
}

export default function DownloadForm({ onSubmit, disabled = false }: DownloadFormProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | undefined>(undefined)  // Phase 2.12: null → undefined

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(undefined)

    if (!url.trim()) {
      setError('URL is required')
      return
    }

    // URL バリデーション（簡易版）
    try {
      new URL(url)
    } catch {
      setError('Invalid URL format')
      return
    }

    onSubmit(url)  // Phase 2.12: filenameなしで送信
    setUrl('')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded shadow">
      <div>
        <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
          Civitai Model URL
        </label>
        <input
          type="text"
          id="url"
          name="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={disabled}
          placeholder="https://civitai.com/models/12345/model-name"
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <p className="mt-1 text-sm text-gray-500">
          Filename will be automatically extracted from model metadata
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={disabled}
        className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
      >
        {disabled ? 'Downloading...' : 'Start Download'}
      </button>
    </form>
  )
}

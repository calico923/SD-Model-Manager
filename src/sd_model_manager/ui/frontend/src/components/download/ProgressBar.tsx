interface ProgressBarProps {
  progress: number
  filename?: string
  status?: 'downloading' | 'completed' | 'failed'
  error?: string
}

export default function ProgressBar({
  progress,
  filename,
  status = 'downloading',
  error,
}: ProgressBarProps) {
  return (
    <div className="space-y-2 bg-white p-6 rounded shadow">
      <div className="flex justify-between items-center">
        <h3 className="font-semibold text-gray-800">
          {status === 'completed' && '✅ Download Complete'}
          {status === 'failed' && '❌ Download Failed'}
          {status === 'downloading' && '⏳ Downloading...'}
        </h3>
        <span className="text-sm font-medium text-gray-600">{progress}%</span>
      </div>

      {filename && (
        <p className="text-sm text-gray-600">File: {filename}</p>
      )}

      {/* プログレスバー */}
      <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            status === 'failed'
              ? 'bg-red-500'
              : status === 'completed'
                ? 'bg-green-500'
                : 'bg-blue-500'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
          Error: {error}
        </div>
      )}
    </div>
  )
}

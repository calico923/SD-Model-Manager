import { useDownload } from '../hooks/useDownload'
import DownloadForm from '../components/download/DownloadForm'
import ProgressBar from '../components/download/ProgressBar'

export default function DownloadPage() {
  const { startDownload, progress, isDownloading, filename, status, error, taskId } = useDownload()

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Download Model</h1>

      <div className="grid grid-cols-1 gap-6">
        <DownloadForm onSubmit={startDownload} disabled={isDownloading} />

        {(isDownloading || taskId) && (
          <ProgressBar progress={progress} filename={filename} status={status} error={error} />
        )}
      </div>
    </div>
  )
}

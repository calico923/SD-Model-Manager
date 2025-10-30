import { Download, History } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Sidebar() {
  return (
    <nav className="w-64 bg-gray-900 text-white h-screen p-4">
      <h1 className="text-xl font-bold mb-8">SD Model Manager</h1>

      {/* メインナビゲーション */}
      <ul className="space-y-2 mb-8">
        <li>
          <Link
            to="/download"
            className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded transition"
          >
            <Download size={20} />
            <span>Download</span>
          </Link>
        </li>
        <li>
          <Link
            to="/history"
            className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded transition"
          >
            <History size={20} />
            <span>History</span>
          </Link>
        </li>
      </ul>

      {/* Phase 3+ で追加: カテゴリナビゲーション */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-sm text-gray-400 mb-2">Categories</h3>
        <p className="text-xs text-gray-500 italic">Coming in Phase 3+</p>
      </div>
    </nav>
  )
}

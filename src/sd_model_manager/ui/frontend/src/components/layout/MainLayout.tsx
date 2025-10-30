import { ReactNode } from 'react'

interface MainLayoutProps {
  children: ReactNode
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <main className="flex-1 overflow-auto bg-gray-100">
      {children}
    </main>
  )
}

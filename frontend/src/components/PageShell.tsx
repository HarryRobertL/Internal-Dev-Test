import type { ReactNode } from 'react'

interface PageShellProps {
  children: ReactNode
}

export function PageShell({ children }: PageShellProps) {
  return (
    <main className="app-shell-bg min-h-screen px-4 py-9 md:px-6 md:py-11">
      <div className="mx-auto max-w-7xl">
        <header className="app-card mx-auto mb-8 w-full max-w-4xl rounded-xl p-6">
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Customer Information API
          </h1>
          <p className="text-muted-foreground mt-2 max-w-3xl text-sm leading-6">
            Internal dashboard for submitting and reviewing customer requests.
          </p>
        </header>

        {children}
      </div>
    </main>
  )
}

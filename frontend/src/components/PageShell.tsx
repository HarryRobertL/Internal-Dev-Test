import type { ReactNode } from 'react'

interface PageShellProps {
  children: ReactNode
}

export function PageShell({ children }: PageShellProps) {
  return (
    <main className="app-shell-bg min-h-screen px-4 py-9 md:px-6 md:py-11">
      <div className="mx-auto max-w-7xl space-y-7">
        <header className="app-card rounded-xl px-6 py-6 md:px-7 md:py-6">
          <h1 className="text-2xl font-semibold text-slate-900 md:text-[1.7rem]">
            Customer Information API
          </h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Internal dashboard for submitting and reviewing customer requests.
          </p>
        </header>

        {children}
      </div>
    </main>
  )
}

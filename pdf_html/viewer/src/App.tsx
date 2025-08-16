import { useEffect, useMemo, useRef, useState } from 'react'

type Page = {
  src: string
  width: number
  height: number
  tiles?: { src: string; x: number; y: number; w: number; h: number }[]
}

type DocConfig = {
  title: string
  pages: Page[]
}

declare global {
  interface Window { __DOC__: DocConfig }
}

function useDoc(): DocConfig {
  return useMemo(() => (window.__DOC__), [])
}

function useDisableInteractions() {
  useEffect(() => {
    const prevent = (e: Event) => { e.preventDefault() }
    const stopKeys = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        const k = e.key.toLowerCase()
        if (['s', 'p', 'c', 'u'].includes(k)) e.preventDefault()
      }
    }
    document.addEventListener('contextmenu', prevent)
    document.addEventListener('dragstart', prevent)
    document.addEventListener('selectstart', prevent)
    document.addEventListener('copy', prevent)
    document.addEventListener('keydown', stopKeys)
    return () => {
      document.removeEventListener('contextmenu', prevent)
      document.removeEventListener('dragstart', prevent)
      document.removeEventListener('selectstart', prevent)
      document.removeEventListener('copy', prevent)
      document.removeEventListener('keydown', stopKeys)
    }
  }, [])
}

export default function App() {
  const doc = useDoc()
  useDisableInteractions()
  const [pageIndex, setPageIndex] = useState(0)
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = overlayRef.current
    if (!el) return
    const prevent = (e: Event) => e.preventDefault()
    el.addEventListener('pointerdown', prevent)
    el.addEventListener('pointermove', prevent)
    el.addEventListener('pointerup', prevent)
    return () => {
      el.removeEventListener('pointerdown', prevent)
      el.removeEventListener('pointermove', prevent)
      el.removeEventListener('pointerup', prevent)
    }
  }, [])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'PageDown') {
        setPageIndex(i => Math.min(i + 1, doc.pages.length - 1))
      } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
        setPageIndex(i => Math.max(i - 1, 0))
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [doc.pages.length])

  const page = doc.pages[pageIndex]

  return (
    <div className="min-h-screen w-full flex flex-col">
      <header className="sticky top-0 z-10 bg-black/80 backdrop-blur border-b border-white/10">
        <div className="mx-auto max-w-5xl px-4 py-2 flex items-center gap-3 text-sm">
          <div className="font-medium truncate">{doc.title}</div>
          <div className="ml-auto flex items-center gap-2">
            <button className="px-3 py-1 rounded bg-white/10 hover:bg-white/20" onClick={() => setPageIndex(i => Math.max(0, i - 1))}>
              Prev
            </button>
            <span className="tabular-nums">{pageIndex + 1} / {doc.pages.length}</span>
            <button className="px-3 py-1 rounded bg-white/10 hover:bg-white/20" onClick={() => setPageIndex(i => Math.min(doc.pages.length - 1, i + 1))}>
              Next
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-4 py-6">
          <div className="relative">
            <div ref={overlayRef} className="absolute inset-0 z-10" aria-hidden="true"></div>
            {page.tiles && page.tiles.length > 0 ? (
              <div
                className="grid bg-neutral-900"
                style={{ gridTemplateColumns: `repeat(3, 1fr)`, width: page.width, maxWidth: '100%' }}
              >
                {page.tiles.map((t, idx) => (
                  <img key={idx} src={t.src} draggable={false} className="w-full h-auto block select-none pointer-events-none" />
                ))}
              </div>
            ) : (
              <img src={page.src} draggable={false} className="w-full h-auto block select-none pointer-events-none" />
            )}
          </div>
        </div>
      </main>
    </div>
  )
}


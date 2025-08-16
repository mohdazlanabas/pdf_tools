import { execa } from 'execa'
import fs from 'node:fs/promises'
import path from 'node:path'
import crypto from 'node:crypto'
import sharp from 'sharp'

type BuilderConfig = {
  dpi: number
  quality: number
  format: 'webp' | 'jpeg'
  retinaScale: number
  sliceGrid: [number, number] | null
  hashNames: boolean
}

const projectRoot = path.resolve('.')
const assetsDir = path.join(projectRoot, 'assets')
const viewerDist = path.join(projectRoot, 'viewer', 'dist')
const outDir = path.join(projectRoot, 'dist')

const defaultConfig: BuilderConfig = {
  dpi: 200,
  quality: 80,
  format: 'webp',
  retinaScale: 2,
  sliceGrid: [3, 3],
  hashNames: true,
}

function slugify(name: string) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

function hashContent(buf: Buffer, len = 8) {
  return crypto.createHash('sha1').update(buf).digest('hex').slice(0, len)
}

async function ensureDir(dir: string) {
  await fs.mkdir(dir, { recursive: true })
}

async function listPdfFiles(): Promise<string[]> {
  const files = await fs.readdir(assetsDir)
  return files.filter(f => f.toLowerCase().endsWith('.pdf')).map(f => path.join(assetsDir, f))
}

async function rasterizePdfToPngs(pdfPath: string, dpi: number, targetDir: string): Promise<string[]> {
  await ensureDir(targetDir)
  const base = path.join(targetDir, 'page')
  // pdftoppm -png -r 200 input.pdf output-prefix
  await execa('pdftoppm', ['-png', '-r', String(dpi), pdfPath, base], { stdio: 'inherit' })
  const files = await fs.readdir(targetDir)
  const pngs = files.filter(f => f.startsWith('page-') && f.endsWith('.png')).sort((a, b) => a.localeCompare(b))
  return pngs.map(f => path.join(targetDir, f))
}

async function convertAndMaybeSlice(
  pngPath: string,
  outPagesDir: string,
  cfg: BuilderConfig,
): Promise<{ imageSrc: string; width: number; height: number; tiles?: string[] }> {
  const img = sharp(pngPath)
  const meta = await img.metadata()
  const width = meta.width ?? 0
  const height = meta.height ?? 0

  const buffer = await img.toFormat(cfg.format, cfg.format === 'webp' ? { quality: cfg.quality } : { quality: cfg.quality, progressive: true }).toBuffer()
  const nameBase = cfg.hashNames ? hashContent(buffer) : path.parse(pngPath).name
  const baseFile = `${nameBase}.${cfg.format}`
  const outPath = path.join(outPagesDir, baseFile)
  await fs.writeFile(outPath, buffer)

  if (!cfg.sliceGrid) {
    return { imageSrc: `pages/${baseFile}`, width, height }
  }

  const [cols, rows] = cfg.sliceGrid
  const tileWidth = Math.floor(width / cols)
  const tileHeight = Math.floor(height / rows)
  const tilePaths: string[] = []
  let idx = 0
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const left = x * tileWidth
      const top = y * tileHeight
      const tile = await sharp(pngPath).extract({ left, top, width: x === cols - 1 ? width - left : tileWidth, height: y === rows - 1 ? height - top : tileHeight })
      const tileBuf = await tile.toFormat(cfg.format, cfg.format === 'webp' ? { quality: cfg.quality } : { quality: cfg.quality, progressive: true }).toBuffer()
      const tileName = cfg.hashNames ? `${nameBase}-${idx}.${cfg.format}` : `${path.parse(pngPath).name}-${idx}.${cfg.format}`
      const tileOut = path.join(outPagesDir, tileName)
      await fs.writeFile(tileOut, tileBuf)
      tilePaths.push(`pages/${tileName}`)
      idx++
    }
  }
  return { imageSrc: `pages/${baseFile}`, width, height, tiles: tilePaths }
}

async function copyViewerAssets(targetDir: string) {
  const html = await fs.readFile(path.join(viewerDist, 'index.html'), 'utf8')
  // Find built asset paths
  const cssMatch = html.match(/href=\"(\/assets\/[^\"]+\.css)\"/)
  const jsMatch = html.match(/src=\"(\/assets\/[^\"]+\.js)\"/)
  const cssRel = cssMatch ? cssMatch[1] : null
  const jsRel = jsMatch ? jsMatch[1] : null
  if (!cssRel || !jsRel) throw new Error('Failed to locate viewer assets in built HTML')

  await ensureDir(path.join(targetDir, 'assets'))
  await fs.copyFile(path.join(viewerDist, cssRel), path.join(targetDir, 'assets', path.basename(cssRel)))
  await fs.copyFile(path.join(viewerDist, jsRel), path.join(targetDir, 'assets', path.basename(jsRel)))

  return {
    css: `assets/${path.basename(cssRel)}`,
    js: `assets/${path.basename(jsRel)}`,
  }
}

async function emitDocHtml(docOutDir: string, docTitle: string, pages: { src: string; width: number; height: number; tiles?: string[] }[], assets: { css: string; js: string }) {
  const doc = {
    title: docTitle,
    pages: pages.map(p => ({ src: p.src, width: p.width, height: p.height, tiles: p.tiles?.map(src => ({ src, x: 0, y: 0, w: 0, h: 0 })) })),
  }
  const html = `<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex,noimageindex,nofollow" />
    <meta http-equiv="Referrer-Policy" content="no-referrer" />
    <title>${docTitle}</title>
    <link rel="stylesheet" href="/${assets.css}" />
    <style>html,body,#root{height:100%} img{pointer-events:none;-webkit-user-drag:none} </style>
  </head>
  <body>
    <div id="root"></div>
    <script>window.__DOC__ = ${JSON.stringify(doc)};<\/script>
    <script type="module" src="/${assets.js}"></script>
  </body>
</html>`
  await fs.writeFile(path.join(docOutDir, 'index.html'), html, 'utf8')
}

async function emitIndexHtml(indexOutPath: string, entries: { title: string; href: string; pages: number }[]) {
  const list = entries.map(e => `<li class="py-2"><a class="text-sky-400 hover:underline" href="${e.href}">${e.title}</a> <span class="opacity-60">(${e.pages} pages)</span></li>`).join('\n')
  const html = `<!doctype html>
<html>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="noindex,noimageindex,nofollow" />
    <meta http-equiv="Referrer-Policy" content="no-referrer" />
    <title>Documents</title>
    <style>html,body{height:100%}body{font-family:ui-sans-serif,system-ui; background:#0b0f14;color:#fff;margin:0;padding:24px}</style>
  </head>
  <body>
    <h1 style="font-size:20px;margin:0 0 12px 0;">Documents</h1>
    <ul style="list-style:none;padding:0;margin:0">${list}</ul>
  </body>
</html>`
  await fs.writeFile(indexOutPath, html, 'utf8')
}

async function build() {
  const cfg = defaultConfig
  await fs.rm(outDir, { recursive: true, force: true })
  await ensureDir(outDir)

  // Copy shared viewer assets once
  const sharedAssets = await copyViewerAssets(outDir)

  const pdfs = await listPdfFiles()
  const indexEntries: { title: string; href: string; pages: number }[] = []

  for (const pdfPath of pdfs) {
    const base = path.parse(pdfPath).name
    const title = base
    const slug = slugify(base)
    const docOutDir = path.join(outDir, 'docs', slug)
    const pagesDir = path.join(docOutDir, 'pages')
    await ensureDir(pagesDir)

    // 1) Rasterize to PNGs
    const tmpDir = path.join(projectRoot, '.tmp', slug)
    await fs.rm(tmpDir, { recursive: true, force: true })
    await ensureDir(tmpDir)
    const pngs = await rasterizePdfToPngs(pdfPath, cfg.dpi * cfg.retinaScale, tmpDir)

    // 2) Convert + slice
    const pageOutputs: { src: string; width: number; height: number; tiles?: string[] }[] = []
    for (const png of pngs) {
      const out = await convertAndMaybeSlice(png, pagesDir, cfg)
      pageOutputs.push(out)
    }

    // 3) Emit doc HTML
    await emitDocHtml(docOutDir, title, pageOutputs, sharedAssets)

    indexEntries.push({ title, href: `docs/${slug}/`, pages: pageOutputs.length })
  }

  // 4) Index
  await emitIndexHtml(path.join(outDir, 'index.html'), indexEntries)
  await fs.writeFile(path.join(outDir, 'robots.txt'), 'User-agent: *\nDisallow: /\n', 'utf8')

  console.log('Build complete:', outDir)
}

build().catch(err => {
  console.error(err)
  process.exit(1)
})



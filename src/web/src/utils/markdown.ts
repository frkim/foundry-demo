import DOMPurify from 'dompurify'
import { marked } from 'marked'
import type { GeneratedFile } from '../types'

marked.setOptions({ gfm: true, breaks: false })

DOMPurify.addHook('afterSanitizeAttributes', (node) => {
  if (node.tagName === 'A' && node.getAttribute('href')) {
    node.setAttribute('target', '_blank')
    node.setAttribute('rel', 'noopener noreferrer')
  }
})

/** Point Code Interpreter `sandbox:/mnt/data/<file>` links at the API file proxy. */
function rewriteSandboxLinks(markdown: string, files: GeneratedFile[]): string {
  if (files.length === 0) return markdown
  return markdown.replace(/sandbox:\/mnt\/data\/([^\s)"']+)/g, (match, name: string) => {
    const file = files.find((f) => f.filename === name || f.filename.endsWith(`/${name}`))
    return file ? file.url : match
  })
}

/** Render untrusted Markdown to sanitized HTML. */
export function renderMarkdown(markdown: string, files: GeneratedFile[] = []): string {
  const html = marked.parse(rewriteSandboxLinks(markdown, files), { async: false })
  return DOMPurify.sanitize(html, { USE_PROFILES: { html: true } })
}

/** Files not already embedded as Markdown images, to avoid showing a chart twice. */
export function unreferencedFiles(markdown: string, files: GeneratedFile[] = []): GeneratedFile[] {
  const embedded = [...markdown.matchAll(/!\[[^\]]*\]\(([^)\s]+)/g)].map((m) => m[1] ?? '')
  return files.filter((file) => {
    const name = file.filename.split('/').pop() ?? file.filename
    return !embedded.some((src) => src === file.url || src === `sandbox:/mnt/data/${name}`)
  })
}

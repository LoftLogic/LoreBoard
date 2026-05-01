import { useState, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import type { EditorState } from 'lexical'
import { Loader2, CheckCircle, AlertCircle, Zap } from 'lucide-react'
import LexicalEditor from '@/components/editor/LexicalEditor'
import { useJob } from '@/hooks/useJob'
import { storiesApi } from '@/api/stories'
import { chaptersApi } from '@/api/chapters'
import { jobsApi } from '@/api/jobs'

type SaveState = 'idle' | 'saving' | 'saved' | 'error'

/** IDs created/opened in this session. Preserved across re-renders but not navigation. */
interface Session {
  storyId: string
  chapterId: string
}

export default function Editor() {
  const { storyId: urlStoryId } = useParams<{ storyId: string }>()

  const [title, setTitle] = useState('Untitled Story')
  const [editorState, setEditorState] = useState<EditorState | null>(null)
  const [session, setSession] = useState<Session | null>(
    urlStoryId ? { storyId: urlStoryId, chapterId: '' } : null,
  )
  const [saveState, setSaveState] = useState<SaveState>('idle')
  const [analyzeJobId, setAnalyzeJobId] = useState<string | null>(null)

  const { job: analyzeJob } = useJob(analyzeJobId)

  const handleChange = useCallback((state: EditorState) => {
    setEditorState(state)
  }, [])

  const handleSaveAndAnalyze = async () => {
    if (!editorState) return
    setSaveState('saving')

    try {
      const content = JSON.stringify(editorState.toJSON())
      let currentSession = session

      // First save: create story + chapter
      if (!currentSession) {
        const story = await storiesApi.create(title)
        const chapter = await chaptersApi.create({
          story_id: story.id,
          order: 1,
          title: 'Chapter 1',
          content,
        })
        currentSession = { storyId: story.id, chapterId: chapter.id }
        setSession(currentSession)
      } else {
        // Update existing chapter content (marks it STALE automatically)
        if (currentSession.chapterId) {
          await chaptersApi.updateContent(currentSession.chapterId, content)
        }
      }

      setSaveState('saved')

      // Kick off analysis
      if (currentSession.chapterId) {
        const { job_id } = await jobsApi.analyzeChapter(currentSession.chapterId)
        setAnalyzeJobId(job_id)
      }

      setTimeout(() => setSaveState('idle'), 3000)
    } catch (err) {
      console.error(err)
      setSaveState('error')
      setTimeout(() => setSaveState('idle'), 4000)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-loreboard-50 to-white">
      <div className="max-w-4xl mx-auto py-8 px-4 space-y-4">

        {/* Title bar */}
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Story title…"
          className="w-full text-2xl font-serif font-bold text-loreboard-900 bg-transparent border-none outline-none placeholder-loreboard-300"
        />

        {/* Editor card */}
        <div className="bg-white rounded-xl shadow-purple-glow overflow-hidden">
          <LexicalEditor onChange={handleChange} />

          {/* Footer bar */}
          <div className="border-t border-gray-100 px-8 py-3 flex items-center justify-between">
            <JobStatusBadge jobId={analyzeJobId} />
            <SaveButton
              state={saveState}
              disabled={!editorState}
              onClick={handleSaveAndAnalyze}
            />
          </div>
        </div>

        {/* Session info (dev aid) */}
        {session && (
          <p className="text-xs text-gray-400 font-mono">
            story: {session.storyId} · chapter: {session.chapterId || 'pending'}
          </p>
        )}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function SaveButton({
  state,
  disabled,
  onClick,
}: {
  state: SaveState
  disabled: boolean
  onClick: () => void
}) {
  const map: Record<SaveState, { label: string; cls: string }> = {
    idle: {
      label: 'Save & Analyze',
      cls: 'bg-loreboard-600 hover:bg-loreboard-700 text-white shadow-lg hover:shadow-purple-glow',
    },
    saving: { label: 'Saving…', cls: 'bg-loreboard-400 text-white cursor-wait' },
    saved: { label: 'Saved', cls: 'bg-green-600 text-white' },
    error: { label: 'Error', cls: 'bg-red-600 text-white' },
  }
  const { label, cls } = map[state]

  return (
    <button
      onClick={onClick}
      disabled={disabled || state === 'saving'}
      className={`flex items-center gap-2 px-5 py-2 rounded-lg font-medium text-sm transition-all ${cls} disabled:opacity-50 disabled:cursor-not-allowed`}
    >
      {state === 'saving' ? (
        <Loader2 size={15} className="animate-spin" />
      ) : (
        <Zap size={15} />
      )}
      {label}
    </button>
  )
}

function JobStatusBadge({ jobId }: { jobId: string | null }) {
  const { job, error } = useJob(jobId)

  if (!jobId) return null

  if (error) {
    return (
      <span className="flex items-center gap-1.5 text-xs text-red-500">
        <AlertCircle size={13} /> {error}
      </span>
    )
  }

  if (!job) {
    return (
      <span className="flex items-center gap-1.5 text-xs text-loreboard-400">
        <Loader2 size={13} className="animate-spin" /> Queued…
      </span>
    )
  }

  const statusMap: Record<string, { icon: React.ReactNode; cls: string; label: string }> = {
    pending: { icon: <Loader2 size={13} className="animate-spin" />, cls: 'text-loreboard-400', label: 'Pending' },
    running: { icon: <Loader2 size={13} className="animate-spin" />, cls: 'text-loreboard-600', label: 'Analyzing…' },
    done: { icon: <CheckCircle size={13} />, cls: 'text-green-600', label: 'Analysis complete' },
    failed: { icon: <AlertCircle size={13} />, cls: 'text-red-500', label: 'Analysis failed' },
    cancelled: { icon: <AlertCircle size={13} />, cls: 'text-gray-400', label: 'Cancelled' },
  }

  const { icon, cls, label } = statusMap[job.status] ?? statusMap.pending

  return (
    <span className={`flex items-center gap-1.5 text-xs ${cls}`}>
      {icon} {label}
    </span>
  )
}

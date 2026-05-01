import { useEffect, useRef, useState } from 'react'
import { jobsApi } from '@/api/jobs'
import type { Job, JobStatus } from '@/types/story'

const TERMINAL: JobStatus[] = ['done', 'failed', 'cancelled']

/** Poll a job by ID until it reaches a terminal state. */
export function useJob(jobId: string | null, intervalMs = 2000) {
  const [job, setJob] = useState<Job | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setInterval> | null>(null)

  useEffect(() => {
    if (!jobId) return

    const poll = async () => {
      try {
        const j = await jobsApi.get(jobId)
        setJob(j)
        if (TERMINAL.includes(j.status)) {
          clearInterval(timer.current!)
        }
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Poll failed')
        clearInterval(timer.current!)
      }
    }

    poll()
    timer.current = setInterval(poll, intervalMs)
    return () => clearInterval(timer.current!)
  }, [jobId, intervalMs])

  const isTerminal = job ? TERMINAL.includes(job.status) : false

  return { job, error, isTerminal }
}

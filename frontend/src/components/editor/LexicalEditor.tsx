import type { EditorState } from 'lexical'
import { LexicalComposer } from '@lexical/react/LexicalComposer'
import { RichTextPlugin } from '@lexical/react/LexicalRichTextPlugin'
import { ContentEditable } from '@lexical/react/LexicalContentEditable'
import { HistoryPlugin } from '@lexical/react/LexicalHistoryPlugin'
import { OnChangePlugin } from '@lexical/react/LexicalOnChangePlugin'
import { LexicalErrorBoundary } from '@lexical/react/LexicalErrorBoundary'
import { HeadingNode } from '@lexical/rich-text'
import Toolbar from './Toolbar'
import { CUSTOM_NODES } from './nodes'

const THEME = {
  paragraph: 'mb-4 font-serif text-base leading-relaxed',
  text: {
    bold: 'font-bold',
    italic: 'italic',
    underline: 'underline',
  },
  heading: {
    h1: 'text-4xl font-bold font-serif mb-6 text-loreboard-900',
    h2: 'text-2xl font-semibold font-serif mb-4 text-loreboard-800',
  },
}

interface Props {
  onChange: (state: EditorState) => void
  placeholder?: string
}

export default function LexicalEditor({ onChange, placeholder = 'Begin your story…' }: Props) {
  return (
    <LexicalComposer
      initialConfig={{
        namespace: 'LoreboardEditor',
        theme: THEME,
        nodes: [HeadingNode, ...CUSTOM_NODES],
        onError: (err) => console.error(err),
      }}
    >
      <Toolbar />
      <div className="relative">
        <RichTextPlugin
          contentEditable={
            <ContentEditable className="min-h-[520px] px-8 py-6 outline-none font-serif text-base" />
          }
          placeholder={
            <div className="absolute top-6 left-8 text-gray-400 font-serif pointer-events-none select-none">
              {placeholder}
            </div>
          }
          ErrorBoundary={LexicalErrorBoundary}
        />
        <OnChangePlugin onChange={onChange} />
        <HistoryPlugin />
      </div>
    </LexicalComposer>
  )
}

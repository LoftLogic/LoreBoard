import { useEffect, useState } from 'react'
import { useLexicalComposerContext } from '@lexical/react/LexicalComposerContext'
import {
  $getSelection,
  $isRangeSelection,
  $createParagraphNode,
  FORMAT_TEXT_COMMAND,
} from 'lexical'
import { $setBlocksType } from '@lexical/selection'
import { HeadingNode, $createHeadingNode } from '@lexical/rich-text'
import { Bold, Italic, Search, Underline } from 'lucide-react'
import { $createSubtitleNode, SubtitleNode } from './nodes'

type TextBlockType = 'basic' | 'title' | 'chapter' | 'subtitle'

const BLOCK_OPTIONS: { value: TextBlockType; label: string }[] = [
  { value: 'basic', label: 'Body' },
  { value: 'title', label: 'Title' },
  { value: 'chapter', label: 'Chapter' },
  { value: 'subtitle', label: 'Subtitle' },
]

export default function Toolbar() {
  const [editor] = useLexicalComposerContext()
  const [blockType, setActiveBlock] = useState<TextBlockType>('basic')
  const [isBold, setIsBold] = useState(false)
  const [isItalic, setIsItalic] = useState(false)
  const [isUnderline, setIsUnderline] = useState(false)

  useEffect(() => {
    return editor.registerUpdateListener(({ editorState }) => {
      editorState.read(() => {
        const sel = $getSelection()
        if ($isRangeSelection(sel)) {
          setIsBold(sel.hasFormat('bold'))
          setIsItalic(sel.hasFormat('italic'))
          setIsUnderline(sel.hasFormat('underline'))
        }
      })
    })
  }, [editor])

  const applyBlockType = (type: TextBlockType) => {
    setActiveBlock(type)
    editor.update(() => {
      const sel = $getSelection()
      if (!$isRangeSelection(sel)) return
      switch (type) {
        case 'title':
          $setBlocksType(sel, () => $createHeadingNode('h1'))
          break
        case 'chapter':
          $setBlocksType(sel, () => $createHeadingNode('h2'))
          break
        case 'subtitle':
          $setBlocksType(sel, () => $createSubtitleNode())
          break
        default:
          $setBlocksType(sel, () => $createParagraphNode())
      }
    })
  }

  const fmt = (f: 'bold' | 'italic' | 'underline') =>
    editor.dispatchCommand(FORMAT_TEXT_COMMAND, f)

  const btnCls = (active: boolean) =>
    `p-2 rounded transition-colors ${
      active ? 'bg-loreboard-100 text-loreboard-700' : 'text-gray-600 hover:bg-gray-100'
    }`

  return (
    <div className="border-b border-gray-200 bg-white px-4 py-2 flex items-center gap-2 sticky top-0 z-10">
      <select
        value={blockType}
        onChange={(e) => applyBlockType(e.target.value as TextBlockType)}
        className="px-2 py-1 border border-gray-300 rounded text-sm font-mono focus:outline-none focus:ring-2 focus:ring-loreboard-500"
      >
        {BLOCK_OPTIONS.map((o) => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>

      <div className="h-5 w-px bg-gray-300 mx-1" />

      <button className={btnCls(isBold)} onClick={() => fmt('bold')} title="Bold">
        <Bold size={16} />
      </button>
      <button className={btnCls(isItalic)} onClick={() => fmt('italic')} title="Italic">
        <Italic size={16} />
      </button>
      <button className={btnCls(isUnderline)} onClick={() => fmt('underline')} title="Underline">
        <Underline size={16} />
      </button>

      <div className="flex-1" />

      <button
        className="p-2 rounded text-loreboard-500 hover:bg-loreboard-50 transition-colors"
        title="Search"
      >
        <Search size={18} />
      </button>
    </div>
  )
}

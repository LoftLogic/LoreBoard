import { HeadingNode } from '@lexical/rich-text'
import type { SerializedHeadingNode } from '@lexical/rich-text'
import type { EditorConfig, Klass, LexicalNode } from 'lexical'

/** Custom heading variant used for chapter subtitles / scene breaks. */
export class SubtitleNode extends HeadingNode {
  static getType(): string {
    return 'subtitle'
  }

  static clone(node: SubtitleNode): SubtitleNode {
    return new SubtitleNode(node.__tag, node.__key)
  }

  createDOM(config: EditorConfig): HTMLElement {
    const el = super.createDOM(config)
    el.className = 'text-sm text-loreboard-400 font-mono tracking-widest uppercase my-2'
    return el
  }

  static importJSON(_serialized: SerializedHeadingNode): SubtitleNode {
    return $createSubtitleNode()
  }

  exportJSON(): SerializedHeadingNode {
    return { ...super.exportJSON(), type: 'subtitle', version: 1 }
  }
}

export function $createSubtitleNode(): SubtitleNode {
  return new SubtitleNode('h4')
}

/** All custom nodes that must be registered with the LexicalComposer. */
export const CUSTOM_NODES: Klass<LexicalNode>[] = [SubtitleNode]

import { Mark } from '@tiptap/core';

export const CommentMark = Mark.create({
  name: 'comment',

  addOptions() {
    return {
      HTMLAttributes: {
        class: 'comment',
      },
    };
  },

  addAttributes() {
    return {
      id: {
        default: null,
        parseHTML: element => element.getAttribute('data-comment-id'),
        renderHTML: attributes => {
          if (!attributes.id) {
            return {};
          }
          return {
            'data-comment-id': attributes.id,
          };
        },
      },
      text: {
        default: null,
        parseHTML: element => element.getAttribute('data-comment-text'),
        renderHTML: attributes => {
          if (!attributes.text) {
            return {};
          }
          return {
            'data-comment-text': attributes.text,
          };
        },
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-comment-id]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', { ...this.options.HTMLAttributes, ...HTMLAttributes }, 0];
  },

  addCommands() {
    return {
      setComment:
        attributes => ({ commands }) => {
          return commands.setMark('comment', attributes);
        },
      toggleComment:
        attributes => ({ commands }) => {
          return commands.toggleMark('comment', attributes);
        },
      unsetComment:
        () => ({ commands }) => {
          return commands.unsetMark('comment');
        },
    };
  },
}); 
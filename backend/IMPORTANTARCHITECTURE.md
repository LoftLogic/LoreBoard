## Architecture for Stamping/Parsing

### The following process will occur:
1. The user sends a story update with new text

2. The frontend sends this update to the backend as a lexical text node tree.
{
  "content": {
    "root": {
      "type": "root",
      "children": [
        {
          "type": "paragraph",
          "children": [
            {
              "type": "text",
              "text": "Harry looked at Ron and said, ",
              "format": 0
            },
            {
              "type": "text",
              "text": "Blimey, mate!",
              "format": 1 // Italics
            },
            {
              "type": "text",
              "text": " Ron's face turned red.",
              "format": 2 // Bold
            }
          ]
        }
      ]
    }
  }
}

3. Django receives the tree, stores it, and extracts the plaintext
plaintext = "Harry looked at Ron and said, Blimey, mate! Ron's face turned red."

4. Backend will create a reference table mapping node to text locations in the string (with keys as node id)
[
    {
        'text': 'Harry looked at Ron and said, ',
        'start': 0,
        'end': 30,
        'format': 0,
        'node_id': 'node_abc123'  # Reference to node in tree
    },
    {
        'text': 'Blimey, mate!',
        'start': 30,
        'end': 43,
        'format': 1,
        'node_id': 'node_def456'
    },
    {
        'text': " Ron's face turned red.",
        'start': 43,
        'end': 66,
        'format': 2,
        'node_id': 'node_ghi789'
    }
]

5. AI will parse through text and stamp the appropriate segments. These segments will be stored in a stamp map, mapping the
ai stamp id to the start and end location 

stamps = [
    {
        'id': 'stamp_001',
        'type': 'dialogue',
        'start': 30,
        'end': 43,
        'text': 'Blimey, mate!',
        'color': '#a855f7'
    },
    {
        'id': 'stamp_002', 
        'type': 'physical_description',
        'start': 46,
        'end': 66,
        'text': "Ron's face turned red.",
        'color': '#14b8a6'
    }
]

6. Backend sends the stamp map to the front end
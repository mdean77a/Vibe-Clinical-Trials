# Marked2 Setup Guide for Mermaid Diagrams

This guide helps you configure Marked2 to properly render the Mermaid diagrams in our documentation.

## Method 1: Built-in Mermaid Support (Marked2 v2.6+)

1. **Open Marked2 Preferences** (⌘+,)
2. **Go to "Advanced" tab**
3. **Enable these options**:
   - ✅ "Enable MathJax"
   - ✅ "Mermaid diagrams" (if available)
   - ✅ "Process diagrams"

## Method 2: Custom Processor (If built-in doesn't work)

### Step 1: Install mermaid-cli
```bash
npm install -g @mermaid-js/mermaid-cli
```

### Step 2: Create Custom Processor Script
Save this as `mermaid-processor.sh` in your home directory:

```bash
#!/bin/bash
# Mermaid processor for Marked2
# Save as ~/mermaid-processor.sh and make executable

input_file="$1"
temp_dir="/tmp/marked2-mermaid"
mkdir -p "$temp_dir"

# Process the markdown file and replace mermaid blocks
sed '/^```mermaid$/,/^```$/{
    /^```mermaid$/r /dev/stdin
    /^```mermaid$/,/^```$/d
}' "$input_file"
```

Make it executable:
```bash
chmod +x ~/mermaid-processor.sh
```

### Step 3: Configure Marked2 Custom Processor
1. **Marked2 Preferences** → **Advanced** tab
2. **Custom Processor**: Enable and set path to `~/mermaid-processor.sh`

## Method 3: Alternative - Use HTML Preview

If Mermaid still doesn't work, you can view the diagrams online:

1. **Open file in Marked2** for the markdown content
2. **Open GitHub link** in browser for the diagrams:
   - [Frontend Components](https://github.com/mdean77a/Vibe-Clinical-Trials/blob/main/docs/diagrams/01-frontend-components.md)
   - [Backend Services](https://github.com/mdean77a/Vibe-Clinical-Trials/blob/main/docs/diagrams/02-backend-services.md)
   - [API Summary](https://github.com/mdean77a/Vibe-Clinical-Trials/blob/main/docs/diagrams/03-api-endpoints-summary.md)
   - [Data Flow](https://github.com/mdean77a/Vibe-Clinical-Trials/blob/main/docs/diagrams/04-data-flow-sequences.md)
   - [System Overview](https://github.com/mdean77a/Vibe-Clinical-Trials/blob/main/docs/diagrams/05-system-overview.md)

## Printing from Marked2

Once diagrams render properly:

1. **File** → **Print** (⌘+P)
2. **Choose**: "Save as PDF" for best quality
3. **Settings**:
   - Paper: US Letter (8.5" x 11")
   - Orientation: Portrait
   - Margins: 0.5" all sides
   - Scale: Fit to page width

## Troubleshooting

### If diagrams show as code blocks:
- Check Marked2 version (needs v2.5.12+)
- Try toggling "Live Preview" off and on
- Restart Marked2

### If text is too small:
- Use browser zoom (⌘+) before printing
- Or adjust font size in Marked2 preferences

### For best print quality:
1. **Export to PDF** from Marked2
2. **Open PDF** in Preview
3. **Print** from Preview with high quality settings

## Quick Test

Open `01-frontend-components.md` in Marked2. You should see:
- ✅ Formatted markdown text
- ✅ Rendered diagram (not code)
- ✅ Proper colors and shapes

If you see code instead of diagrams, try Method 2 above. 
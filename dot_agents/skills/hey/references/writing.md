# Escribir contenido

Message bodies, drafts, thread notes, journal entries, snippets and contact notes are Markdown by default (`-m`, `--content`, `--note`, positional content, stdin and `$EDITOR` alike) and are converted to rich text on the way out; clip passages, event notes and time track notes are plain text. Each Markdown flag has an HTML twin (such as `--message-html`, `--note-html`, `--content-html`) for raw HTML, and each pair is mutually exclusive. A fenced code block's language survives for the languages HEY highlights (Ruby, Python, JavaScript, TypeScript, Go, Rust, Java, C#, C++, PHP, Swift, HTML and CSS); any other is dropped.

Everything a calendar holds is a recording, and each kind has its own command: `hey event`, `hey todo`, `hey journal`, `hey habit`, `hey timetrack`. Without a date, those commands read the account's time zone to find today; name the date to skip the account read.

## Adding to something written whole

`hey contact note set` and `hey journal write` replace the whole note or entry; there is no append. To add, read it, change it, and write all of it back. Keep the `&&`: a failed read must not go on to write. The read and the write are not atomic, so write straight after reading.

**Contact note.** When `note_markdown_lossless` is `true`, `note_markdown` holds the whole note; the read checks the flag itself and fails when it is `false`, so nothing is written:

```bash
note=$(hey contact note show 12345 --jq 'if .data.note_markdown_lossless then .data.note_markdown else error("note_markdown would drop part of this note: change note_html with --note-html") end') &&
  printf '%s\n\nMoved to the Lisbon office in March.\n' "$note" | hey contact note set 12345
```

When it is `false`, the note holds markup Markdown cannot carry. Add to the HTML instead:

```bash
note=$(hey contact note show 12345 --jq '.data.note_html') &&
  hey contact note set 12345 --note-html "$note<p>Moved to the Lisbon office in March.</p>"
```

**Journal entry.** The same, with `content_markdown_lossless`; the read also fails for a day with no entry:

```bash
entry=$(hey journal read 2026-03-15 --jq 'if .data.content_markdown_lossless then .data.content_markdown else error("content_markdown would drop part of this entry, or there is none: change content with --content-html") end') &&
  printf '%s\n\nBooked the venue for the second day.\n' "$entry" | hey journal write 2026-03-15
```

```bash
entry=$(hey journal read 2026-03-15 --jq '.data.content // error("no journal entry for this day")') &&
  hey journal write 2026-03-15 --content-html "$entry<p>Booked the venue for the second day.</p>"
```

# Output estructurado e IDs

## Output

`--jq` filters the full JSON success envelope, so result data is under `.data`. String results print as plain text; objects and arrays print as formatted JSON. Use `--quiet --jq` when the expression should run against result data directly. Errors keep their complete structured envelope. Commands with raw output of their own (`auth token`, `shell-completion generate`, `setup`, `skill`, `tui`, `--version`, and `timetrack export` without `--output`) reject `--jq`. `hey watch` writes one raw JSON event per line with no envelope and does not apply `--jq`.

```bash
hey box list --jq '.data[] | {id, name}'
hey search "quarterly planning" --jq '.data[].topic_id'
hey box list --quiet --jq '.[].name'
```

- An empty result is an empty array rather than `null`, so `.data[]` is safe on a listing that found nothing.
- A field HEY's answer leaves out is left out, never guessed. A posting's `seen` is present only when true, so test `.seen != true` for unseen.
- `--ids-only` prints one ID per line and `--count` a bare number. They work on listings: every `list` command, the thread listings, `hey workflow view`, `hey search`, `hey screener history`, `hey event day|week`, `hey timetrack categories`, `hey attachment list` and `hey thread read` (its entries, read from the index without bodies). Both answer for what was read, which is the first page unless `--all` or `--limit` reads more, and not every listing warns that more pages exist; `hey screener list --count` is the exception and counts the whole queue. On thread listings they count the postings, not the box, label or contact around them.
- `--all` stops at a page cap, which each listing's help names. A capped read says where to continue: `next_page` for a cursor listing such as `hey box view`, or the `notice`, naming the `--page` value, for a numbered one such as `hey search` or `hey contact list`. Continue from there rather than treating the list as complete.
- `--html` writes the original HTML of `hey thread read`, `hey journal read` and a contact's private note to a pipe or file; a terminal is refused.

## IDs

Every email thread has two IDs: `id`, its **box item ID** (one posting in one box), and `topic_id`, its **thread ID**. Each posting in a thread listing has `id`, `topic_id`, `kind` (`bundle` for a bundle row), `name` (subject), `created_at` and `app_url`; a thread row also has `contacts`, `summary` and `visible_entry_count`.

- **Box item ID** (`id`): `hey seen`, `unseen`, `move`, `label add|remove|create`, `trash`, `spam`, `ignore`, `stop-ignoring`, `bubble up|pop`, `set-aside group`, `bulk-reply` and `bundle view`.
- **Thread ID** (`topic_id`): `hey thread read|update|comment`, `share`, `unshare`, `attachment list`, `reply`, `forward`, `compose --thread-id`, `collection add|remove` and `workflow add|move|remove`.
- **Entry ID**: an entry's `id` from `hey thread read`; `hey clip create` takes it, and the passage must appear in that message's text.
- **Contact ID** from `hey contact list` or contact data, **clearance ID** from `hey screener list` (which also gives the `topic_id` of the thread to read before deciding), **box ID** from `hey box list`, **label ID** from `hey label list`. Never substitute one kind for another, or an email address for a contact ID.

Thread listings (`hey box view`, `label view`, `collection view`, `bundle view`, `contact threads`, `search`) carry both IDs, with two exceptions: a bundle row can omit `topic_id`, and a search result omits `id` when you have no box item for its thread.

Passing the wrong kind is not redirected. **Unmatched IDs are not reported**: HEY checks only that *some* box item ID in a call is yours, and changes every one that matches. `hey trash`, `spam`, `label add|remove|create` and `bubble up|pop` answer `not_found` only when none match; `hey seen`, `unseen`, `move`, `ignore`, `stop-ignoring` and `set-aside group create|add|remove` never check (`group create` with no matching ID leaves an empty group). So a mixed batch is a partial success reported as a whole one, a typo is silently skipped, and a `topic_id` that happens to equal one of your box item IDs acts on an unrelated thread; likewise a box item ID given to `hey thread read` can read an unrelated thread. Confirm rather than trust the envelope:

```bash
hey box view imbox --json --all --jq '{notice, next_page: .data.next_page, match: [.data.postings[] | select(.id == 12345) | {id, topic_id, seen}]}'
```

for a mark, or read the destination box for a move. An empty `match` with `next_page` still set means the box is larger than `--all` reads: continue with `--page <next_page>` rather than calling it a non-match.

**Bundle rows.** A posting whose `kind` is `bundle` rolls one sender's mail into one row and names the sender, not a thread. It carries `topic_id` only while it holds exactly one unseen thread. Never pass a bundle row's `id` to `hey thread read`. `hey bundle view <id>` lists its unseen threads with their `topic_id`; `hey contact threads <contact_id>` lists every thread with that sender, seen or not, which is the only place a bundle's mail is listed once read through. Change grouping with `hey contact bundle|unbundle <contact_id>`.

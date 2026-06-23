---
name: ship-and-watch
description: >
  Opens a pull request with the GitHub CLI, then watches it to completion.
  Polls CI checks, review approval, and review-thread resolution on a loop
  until every gate is green; never trusts "changes requested" alone as the
  signal — gates on unresolved review threads so approvals-with-comments and
  bare comments still block. When all comments are resolved, checks pass, and
  the PR is approved, it merges and writes a summary of what changed since the
  PR opened and which suggestions were raised and how each was addressed. Use
  whenever the user says "ship and watch", "ship it", "open a PR and watch it",
  "raise the PR and merge when green", or asks to create, monitor, and merge a
  pull request.
argument-hint: "[base-branch]"
---

# Ship and Watch

You open a pull request, then watch it like an on-call engineer until it is
genuinely ready to merge — not just "CI is green." A PR is mergeable only when
**all three gates** are satisfied:

1. **Checks** — every required status check and CI run has passed.
2. **Approval** — the PR has at least one approving review.
3. **Comments resolved** — every review thread is resolved. This is the gate
   people get wrong.

You merge only when all three are green, then you report what happened.

## The comment gate is the whole point

Do **not** use the review decision (`CHANGES_REQUESTED` / `APPROVED`) as your
signal for outstanding feedback. It lies in both directions:

- A reviewer can **approve** while leaving unresolved comments ("LGTM, but fix
  this one thing"). `reviewDecision` reads `APPROVED`; the comment is still open.
- A reviewer can leave blocking comments **without** clicking "Request changes".
  `reviewDecision` reads `REVIEW_REQUIRED` or `null`; the work is real.

The truth lives in **review threads** and their `isResolved` flag. The standard
`gh pr view --json` fields do not expose thread resolution — you must use the
GraphQL API. Gate on "zero unresolved review threads," never on the decision
enum.

## Step 0 — Pre-flight

Run these before touching the PR. Stop and report if any fails; do not improvise
around a broken precondition.

```bash
gh auth status                                   # authenticated?
git rev-parse --abbrev-ref HEAD                  # current branch (not the base)
git status --porcelain                           # working tree clean?
gh repo view --json owner,name -q '.owner.login + "/" + .name'
```

- Confirm you are on a feature branch, not the base branch.
- Confirm the working tree is clean and the branch is pushed
  (`git push -u origin HEAD` if not). Uncommitted work never goes in a PR.
- Determine the base branch: use the `$ARGUMENTS` value if given, otherwise the
  repo default (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`).

## Step 1 — Open the PR

Draft a title and body from the actual commits, not a guess:

```bash
git log --oneline "$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)..HEAD"
```

Create it:

```bash
gh pr create --base "<base>" --head "$(git rev-parse --abbrev-ref HEAD)" \
  --title "<concise imperative title>" \
  --body "<what changed and why; bullet the notable commits>"
```

Then **capture two baselines** — you need them for the closing summary, and the
session is the only place they live:

```bash
PR=$(gh pr view --json number -q .number)         # PR number, reuse everywhere
OPEN_SHA=$(git rev-parse HEAD)                     # HEAD at PR open
```

Record `PR` and `OPEN_SHA` explicitly in your working notes. `OPEN_SHA` is the
"what changed since the PR went up" anchor — everything pushed after this point
is review-driven change.

## Step 2 — The watch loop

Poll all three gates together. One status pull covers checks + approval:

```bash
gh pr view "$PR" --json number,state,mergeable,reviewDecision,statusCheckRollup,reviews,url
```

### Gate A — Checks

Use `gh pr checks`; its exit code is the cleanest signal:

```bash
gh pr checks "$PR"
# exit 0  = all checks passed
# exit 8  = checks still pending/running  -> keep polling
# exit 1  = a check failed                -> STOP, do not merge
```

On failure: pull the failing job's logs (`gh run view <run-id> --log-failed`),
report exactly what failed, and stop. A failing check is a hard stop — never
merge around it, never retry blindly. If the failure is in code you own, fix it,
push, and the loop resumes from the new commit.

### Gate B — Approval

Read `reviewDecision` from the status JSON. Three distinct cases:

| `reviewDecision` | Meaning | Action |
|---|---|---|
| `"APPROVED"` | A reviewer approved | Gate B green — proceed |
| `null` | Repo has no approval requirement; no review submitted | Gates A+C green → **ask the user in chat** before merging |
| `"REVIEW_REQUIRED"` | Approval required but not yet given | Keep polling |
| `"CHANGES_REQUESTED"` | Reviewer requested changes | Keep polling |

The `null` case is not the same as approved — it means the repo doesn't enforce
reviews. Don't merge silently. When A and C are green and B is `null`, break the
loop and prompt: "All checks pass and every thread is resolved. No reviewer has
approved this PR (the repo doesn't require one). Ready to merge?" Wait for an
explicit yes before proceeding to Step 3.

### Gate C — Comments resolved (GraphQL)

This is the gate the JSON fields cannot answer. Query review threads directly:

```bash
gh api graphql -F owner='<owner>' -F repo='<repo>' -F pr="$PR" -f query='
  query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        reviewThreads(first:100) {
          nodes {
            isResolved
            isOutdated
            path
            comments(first:1) {
              nodes { author { login } body }
            }
          }
        }
      }
    }
  }'
```

Count threads where `isResolved == false`:

```bash
# unresolved thread count
gh api graphql -F owner='<owner>' -F repo='<repo>' -F pr="$PR" -f query='...' \
  | jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false)] | length'
```

**Mergeable on this gate only when that count is `0`.** For each unresolved
thread, surface it: file (`path`), author, and the comment text. Do not merge
while any thread is open.

**Resolving threads — the rules:**
- A comment is "resolved" when the point is actually handled: a commit fixes it,
  or there is a reply explaining why no change is needed.
- Prefer the reviewer resolves their own thread. If the user owns the PR and has
  addressed a thread, you may resolve it via the `resolveReviewThread` mutation —
  but only **after** the underlying point is addressed, never to clear the gate.
- Watch for `isOutdated: true` + `isResolved: false`: the code under the comment
  changed but the reviewer never clicked resolve. This usually means it was fixed
  in a later commit. Surface these specifically — confirm the fix, then resolve
  or ask the reviewer to. Never assume outdated == handled.

```bash
# resolve a thread once its point is genuinely addressed (thread id from the query: add `id` to the node)
gh api graphql -f query='mutation($id:ID!){ resolveReviewThread(input:{threadId:$id}){ thread { isResolved } } }' -F id='<threadId>'
```

### Polling with /loop

Use `/loop` to drive the watch cycle — do not write a bash `while` loop or `sleep`
manually. Each iteration of `/loop` is one poll round:

1. Run the three gate checks (bash commands above).
2. Print one status line: `checks: <pass/none/pending/fail> | approved: <y/n> | open threads: <n>`.
3. If Gate A and C are green and Gate B is `"APPROVED"` → break and merge (Step 3).
   If Gate A and C are green and Gate B is `null` → break and ask the user (Step 3).
4. If Gate A is a hard failure → break, report, stop.
5. Otherwise → let `/loop` iterate again (next round runs automatically).

The user controls the cadence by setting the `/loop` interval when invoking the
skill. Default to whatever they specify; if unspecified, suggest 30s as a
reasonable starting point for a repo with CI.

Cap: stop after 20 rounds regardless of state. Report current gate values and
hand back — do not loop forever.

New commits pushed mid-review reset CI — expect Gate A to go pending again and
keep watching.

## Step 3 — Merge

Only when **A and C are green** and `mergeable` is not `CONFLICTING`.

**If `reviewDecision == "APPROVED"`** — proceed directly:

```bash
gh pr merge "$PR" --squash --delete-branch
```

**If `reviewDecision == null`** — stop and ask the user in chat:

> "All checks pass and every thread is resolved. No reviewer has approved this
> PR (the repo doesn't require one). Ready to merge?"

Wait for an explicit yes. On yes, run the merge command above. On no, stop and
hand back with current gate status.

If `mergeable == "CONFLICTING"`, stop: the branch needs a rebase/merge from base
first. Report it; do not force anything.

## Step 4 — Summarise

After the merge, produce the report. Gather the raw material:

```bash
# what changed since the PR went up
git log --oneline "$OPEN_SHA"..HEAD
git diff --stat "$OPEN_SHA"..HEAD

# every review and its body
gh pr view "$PR" --json reviews -q '.reviews[] | {author: .author.login, state: .state, body: .body}'

# every inline review comment (suggestions on specific lines)
gh api "repos/<owner>/<repo>/pulls/$PR/comments" -q '.[] | {author: .user.login, path: .path, body: .body}'

# issue-level conversation comments
gh pr view "$PR" --json comments -q '.comments[] | {author: .author.login, body: .body}'
```

Write the summary with these sections:

```markdown
## Ship report — PR #<n> (<title>)

**Merged:** <merge strategy> into <base> · <url>

### Changes since the PR opened
[Commits/diffs after OPEN_SHA — the review-driven changes, not the original work.
 "No changes — merged as originally opened" if OPEN_SHA == HEAD.]

### Suggestions raised & how they were addressed
[One line per distinct piece of feedback: who raised it, what it asked, and the
 resolution — commit that fixed it, or the reply explaining why not. Group by
 reviewer or by file, whichever reads cleaner.]

### Final gate status at merge
- Checks: all passing
- Approval: approved by <reviewer(s)>
- Review threads: <n> raised, all resolved
```

Keep the suggestions section concrete: tie each one to its outcome. "Reviewer
asked X → addressed in <sha>" or "Reviewer asked X → replied: not changing
because Y, reviewer resolved." A suggestion with no traceable outcome is a sign a
thread was resolved without being handled — flag it rather than glossing over it.

## Hard stops (never merge through these)

- A check failed (Gate A exit 1).
- Any review thread is unresolved (Gate C count > 0).
- Approval gate stuck: `REVIEW_REQUIRED` or `CHANGES_REQUESTED` with no path to green.
- `mergeable == "CONFLICTING"`.
- The wait cap was hit with gates still red — report state and hand back.

Report the blocker plainly and stop. Shipping a PR that isn't actually ready is
the one failure this skill exists to prevent.

## Command reference

| Need | Command |
|------|---------|
| Create PR | `gh pr create --base <b> --title … --body …` |
| PR number | `gh pr view --json number -q .number` |
| Combined status | `gh pr view <pr> --json state,mergeable,reviewDecision,statusCheckRollup,reviews` |
| Checks (exit code) | `gh pr checks <pr>` · watch: `--watch --fail-fast` |
| Unresolved threads | GraphQL `reviewThreads { nodes { isResolved … } }` |
| Resolve thread | GraphQL `resolveReviewThread(input:{threadId})` |
| Inline comments | `gh api repos/<o>/<r>/pulls/<pr>/comments` |
| Merge | `gh pr merge <pr> --squash --delete-branch` |
| Failing logs | `gh run view <run-id> --log-failed` |

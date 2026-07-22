---
name: pull-request-creator
description: Create GitHub pull requests following UChicago Library conventions for branch naming, PR format, and commit messages. Use when the user asks to create a PR, pull request, or mentions opening/submitting changes for review.
---

# Pull Request Creator

This skill handles creating pull requests according to UChicago Library's specific conventions.

## Branch Naming Convention

When the GitHub issue number and title are known:
- Branch name format: `{issue-number}-{issue-title-lowercase-with-dashes}`
- Example: Issue #123 "Fix authentication bug" → branch `123-fix-authentication-bug`

## PR Description Format

Always use this exact format:

```
Fixes #<GitHub issue number if known>

Summary

<1-2 sentences on problem/solution>
- Key modification 1
- Key modification 2

Testing:
<How the reviewer can test>
```

## Base Branch Selection

Try base branches in this order:
1. Try `master` first
2. If `master` fails, use `main`

## Git Commit Message Rules

When creating commits for PRs:
- No emojis
- Concise is better unless it's a commit large in scope
- No "contributed by Claude" or "generated with AI" type comments
- Focus on what changed and why

## Workflow

1. Check git status and recent commits to understand context
2. Review all changes that will be included (git diff and git log from divergence point)
3. If issue number is known, ensure branch follows naming convention
4. Create PR with proper format using `gh pr create`
5. Use HEREDOC for PR body to ensure proper formatting:

```bash
gh pr create --title "Title here" --base master --body "$(cat <<'EOF'
Fixes #123

Summary

Problem/solution description
- Key change 1
- Key change 2

Testing:
How to test this PR
EOF
)"
```

## Important Notes

- NEVER skip reviewing the full commit history for the branch
- Look at ALL commits that will be included, not just the latest one
- The PR summary should reflect the complete scope of changes
- Return the PR URL when done so the user can see it

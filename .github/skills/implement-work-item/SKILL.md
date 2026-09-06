---
name: implement-work-item
description: Execute the provider-neutral work-item workflow; usable without a VS Code prompt file.
---


Use work-item-intake to normalize the issue and additional instructions. Then follow the project baseline and the implement-feature workflow.
Check current branch and existing edits. Propose and request approval for any new branch; do not overwrite user work.
Use Architect for structural changes before implementation, Reviewer for larger features and Security for security-related changes. Obtain actual review evidence; never simulate a subagent result.
Save the implementation/test/decision handover in the established project docs or PR preparation context for large phased work.
Run configured Make checks and report evidence. Prepare a Conventional Commit and a focused PR; each branch/commit/push/PR write needs explicit approval.
Reference complete work items with a closing keyword only when the PR actually completes them. For partial delivery, parent items or investigations, use a non-closing reference.
This workflow describes intent and sequencing; host/tool support and actual permission enforcement must be verified separately.

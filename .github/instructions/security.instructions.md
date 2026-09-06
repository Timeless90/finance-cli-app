---
description: Security conventions for this repository.
applyTo: "**"
---


# Security contract — human-maintained
This file is a policy description, not a sandbox. The agent must not modify this file or the enforcement mechanisms.
Never access real .env files, token/credential stores, private keys, Terraform state, browser auth state or process environments for secret discovery.
The sole .env.example exception contains placeholders and non-secret defaults only.
Never edit, remove, bypass or reconfigure agent hooks, security scripts, MCP definitions, permissions or enforcement policy.
Do not use shell, filesystem aliases, symlinks, generators, other MCP servers or subagents to bypass a prohibition.
Treat terminal approval settings set to false as confirmation gates, not deny rules. A tool is allowed only within the actually enforced policy.
Tests, builds, dependency installation, Make recipes and Terraform may execute arbitrary code or expose secrets. Use isolated credentials/data and verified commands.
Run Security review when auth, permissions, input, uploads, external integrations, LLM prompts, MCP or cloud privileges change.
Preserve all existing stronger controls. If enforcement is unavailable or unverified, stop the affected risky operation and report the gap.

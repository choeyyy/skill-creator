# skill-creator install script (PowerShell)
# Usage: open PowerShell, cd to skill-creator directory, run: .\install.ps1
#        to uninstall: .\install.ps1 -Uninstall

param(
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"

$PLUGIN_DIR = $PSScriptRoot
if (-not $PLUGIN_DIR) { $PLUGIN_DIR = (Get-Location).Path }

$pluginJson = Join-Path $PLUGIN_DIR ".cursor-plugin\plugin.json"
if (-not (Test-Path $pluginJson)) {
    Write-Host "[ERROR] .cursor-plugin/plugin.json not found." -ForegroundColor Red
    Write-Host "Please run this script from the skill-creator plugin directory." -ForegroundColor Red
    exit 1
}

$SKILLS_DIR = Join-Path $env:USERPROFILE ".cursor\skills"

$SKILL_NAMES = @(
    @{ name = "SKILL-setup";            desc = "Install, update, or configure the skill-creator plugin. Environment check, guided install, agent model selection."; path = "setup/SKILL.md" },
    @{ name = "skill-creator";          desc = "Create, test, and iterate on Cursor Agent Skills with eval-driven development. Full lifecycle: intent capture, drafting, testing, grading, iteration, description optimization."; path = "skills/skill-creator/SKILL.md" },
    @{ name = "SKILL-lint";             desc = "Audit Skill quality — language discipline (English body / Chinese output) + 9-dimension prompt-engineering template compliance. Parallel sub-agent dispatch for batch audit."; path = "commands/SKILL-lint.md" },
    @{ name = "SKILL-fix";              desc = "Auto-repair Skill issues — fix logic first, then enforce format (English, Chinese summary, template, 500-line limit). Deterministic validation + diff confirmation."; path = "commands/SKILL-fix.md" },
    @{ name = "SKILL-pythonGenerator";  desc = "Extract deterministic/repetitive logic from Skills into reusable Python CLI scripts. Single-skill or cross-skill scan."; path = "commands/SKILL-pythonGenerator.md" }
)

if ($Uninstall) {
    Write-Host "`n=== Uninstalling skill-creator ===" -ForegroundColor Yellow
    foreach ($skill in $SKILL_NAMES) {
        $dir = Join-Path $SKILLS_DIR $skill.name
        if (Test-Path $dir) {
            Remove-Item -Recurse -Force $dir
            Write-Host "  Removed: $dir" -ForegroundColor Gray
        }
    }
    Write-Host "`nUninstall complete. Restart Cursor to take effect." -ForegroundColor Green
    exit 0
}

Write-Host "`n=== Installing skill-creator ===" -ForegroundColor Cyan
Write-Host "Plugin directory: $PLUGIN_DIR" -ForegroundColor Gray
Write-Host "Skills directory: $SKILLS_DIR" -ForegroundColor Gray

if (-not (Test-Path $SKILLS_DIR)) {
    New-Item -ItemType Directory -Path $SKILLS_DIR -Force | Out-Null
    Write-Host "  Created: $SKILLS_DIR" -ForegroundColor Gray
}

$created = 0
$skipped = 0

foreach ($skill in $SKILL_NAMES) {
    $skillDir = Join-Path $SKILLS_DIR $skill.name
    $skillFile = Join-Path $skillDir "SKILL.md"

    if (-not (Test-Path $skillDir)) {
        New-Item -ItemType Directory -Path $skillDir -Force | Out-Null
    }

    if (Test-Path $skillFile) {
        $existing = Get-Content $skillFile -Raw
        if ($existing -match [regex]::Escape($PLUGIN_DIR)) {
            Write-Host "  [skip] $($skill.name) -- already installed with current path" -ForegroundColor Gray
            $skipped++
            continue
        }
        # v0.1.0 upgrade: pointer exists but points to a different (old) path — overwrite
        Write-Host "  [upgrade] $($skill.name) -- updating pointer to current path" -ForegroundColor Yellow
    }

    $pluginDirForMd = $PLUGIN_DIR -replace '\\', '/'

    $content = @"
---
name: $($skill.name)
description: "$($skill.desc)"
---

Read and follow the complete orchestrator instructions at ``$pluginDirForMd/$($skill.path)``.

The plugin root for relative path resolution (agents/, references/) is ``$pluginDirForMd/``.
"@

    Set-Content -Path $skillFile -Value $content -Encoding UTF8
    Write-Host "  [ok] $($skill.name)" -ForegroundColor Green
    $created++
}

Write-Host "`n=== Done ===" -ForegroundColor Cyan
Write-Host "  Created: $created skill(s)"
Write-Host "  Skipped: $skipped skill(s) (already installed)"
Write-Host ""
Write-Host "Restart Cursor (or open a new window) to activate." -ForegroundColor Yellow
Write-Host "Then type /skill-creator in any project to start creating skills." -ForegroundColor Yellow
Write-Host ""

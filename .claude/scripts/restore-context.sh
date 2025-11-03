#!/bin/bash
set -eo pipefail  # Remove -u to allow unset variables

# Development Context Restoration Script
# Executed before /compact to restore Kiro spec context

SPEC_DIR=".kiro/specs/model-viewer"
DOCS_DIR="docs/progress-reports"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 DEVELOPMENT CONTEXT RECOVERY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if spec directory exists
if [ ! -d "$SPEC_DIR" ]; then
    echo "⚠️  Warning: .kiro/specs/model-viewer/ not found"
    echo "   No active Kiro specification in this project."
    exit 0
fi

echo ""
echo "## Current State"
echo ""

# Read spec.json for phase and approvals
if [ -f "$SPEC_DIR/spec.json" ]; then
    # Use jq if available, otherwise fallback to grep
    if command -v jq &> /dev/null; then
        PHASE=$(jq -r '.phase // "unknown"' "$SPEC_DIR/spec.json")
        REQ_APPROVED=$(jq -r '.approvals.requirements.approved // false' "$SPEC_DIR/spec.json")
        DESIGN_APPROVED=$(jq -r '.approvals.design.approved // false' "$SPEC_DIR/spec.json")
        TASKS_APPROVED=$(jq -r '.approvals.tasks.approved // false' "$SPEC_DIR/spec.json")
    else
        PHASE=$(grep -o '"phase":[[:space:]]*"[^"]*"' "$SPEC_DIR/spec.json" | cut -d'"' -f4 || echo "unknown")
        REQ_APPROVED="unknown"
        DESIGN_APPROVED="unknown"
        TASKS_APPROVED="unknown"
    fi

    echo "- Feature: model-viewer"
    echo "- Branch: $(git branch --show-current 2>/dev/null || echo 'unknown')"
    echo "- Phase: $PHASE"

    # Convert true/false to checkmarks
    REQ_MARK="⏳"
    [[ "${REQ_APPROVED:-false}" == "true" ]] && REQ_MARK="✅"

    DESIGN_MARK="⏳"
    [[ "${DESIGN_APPROVED:-false}" == "true" ]] && DESIGN_MARK="✅"

    TASKS_MARK="⏳"
    [[ "${TASKS_APPROVED:-false}" == "true" ]] && TASKS_MARK="✅"

    echo "- Spec Approvals: Requirements $REQ_MARK | Design $DESIGN_MARK | Tasks $TASKS_MARK"
fi

echo ""
echo "## Development Rules (Kiro Spec-Driven)"
echo ""
echo "### Phase Execution"
echo "- tasks.mdに沿ってサブタスクごとに進める"
echo "- 各サブタスク完了時に進捗を報告"
echo "- フェーズ完了時に差分とテスト結果をまとめる"
echo ""
echo "### Review & Adjustment"
echo "- Phase終了後、コミット内容を共有"
echo "- 気になる点や追加要望を確認"
echo "- 必要なら修正後に再テスト実行"
echo ""
echo "### Common Rules (各フェーズ共通)"
echo "1. サブタスク完了ごとに docs/progress-reports/ にレポート出力"
echo "2. フェーズ終盤で pytest + 静的解析実行"
echo "3. フェーズ完了時: コミット → PR下書き提示（指示があるまでマージしない）"
echo "4. 3フェーズ終了ごとに止まって報告"

echo ""
echo "## Current Task"
echo ""

# Check if tasks.md exists and show current task status
if [ -f "$SPEC_DIR/tasks.md" ]; then
    # Count total tasks (lines starting with "- [ ]" or "- [x]")
    TOTAL_TASKS=$(grep -c "^- \[" "$SPEC_DIR/tasks.md" 2>/dev/null || echo "0")
    COMPLETED_TASKS=$(grep -c "^- \[x\]" "$SPEC_DIR/tasks.md" 2>/dev/null || echo "0")

    if [ "$TOTAL_TASKS" -gt 0 ]; then
        echo "Progress: $COMPLETED_TASKS / $TOTAL_TASKS tasks completed"
        echo ""

        # Show first pending task
        FIRST_PENDING=$(grep -n "^- \[ \]" "$SPEC_DIR/tasks.md" | head -1)
        if [ -n "$FIRST_PENDING" ]; then
            LINE_NUM=$(echo "$FIRST_PENDING" | cut -d':' -f1)
            TASK_DESC=$(echo "$FIRST_PENDING" | cut -d':' -f2- | sed 's/^- \[ \] //')
            echo "Next Task: $TASK_DESC"
            echo "(Line $LINE_NUM in tasks.md)"
        else
            echo "All tasks completed! 🎉"
        fi
    else
        echo "No tasks found in tasks.md"
    fi
else
    echo "tasks.md not found"
fi

echo ""
echo "## Recent Progress"
echo ""

# Check for progress reports
if [ -d "$DOCS_DIR" ]; then
    REPORT_COUNT=$(ls -1 "$DOCS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')
    if [ "$REPORT_COUNT" -gt 0 ]; then
        echo "Found $REPORT_COUNT progress report(s) in docs/progress-reports/"
        echo ""
        echo "Latest reports:"
        ls -1t "$DOCS_DIR"/*.md 2>/dev/null | head -3 | while read -r report; do
            echo "  - $(basename "$report")"
        done
    else
        echo "No progress reports yet in docs/progress-reports/"
        echo "(Will be created when implementation starts)"
    fi
else
    echo "No progress reports yet (docs/progress-reports/ not created)"
    echo "(Will be created when implementation starts)"
fi

echo ""
echo "## 🎯 Next Action"
echo ""

# Determine next action based on state
if [ "${TASKS_APPROVED:-false}" == "false" ]; then
    echo "Tasks are generated but not approved yet."
    echo ""
    echo "Recommended:"
    echo "1. Review tasks.md content (9 major tasks, 23 sub-tasks)"
    echo "2. Approve tasks: Update spec.json \"tasks\": {\"approved\": true}"
    echo "3. Start implementation: /kiro:spec-impl model-viewer 1.1"
elif [ "${PHASE:-unknown}" == "tasks-generated" ]; then
    echo "Tasks approved. Ready to start implementation."
    echo ""
    echo "To begin:"
    echo "  /kiro:spec-impl model-viewer 1.1"
    echo ""
    echo "This will start Task 1.1: Implement filesystem scanner"
elif [ "${PHASE:-unknown}" == "implementation" ]; then
    echo "Implementation in progress."
    echo ""
    echo "Continue with current task or start next sub-task."
    echo "Remember to:"
    echo "  - Write progress report after completing sub-task"
    echo "  - Run pytest after each sub-task"
    echo "  - Report after every 3 phases complete"
else
    echo "Current phase: ${PHASE:-unknown}"
    echo "Check spec.json and tasks.md for next steps."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit 0

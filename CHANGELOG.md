# Changelog

All notable changes to the Deep Research Skill project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-01-29

### Added - Initial Release

#### Core Features
- **Ralph Loop Pattern**: Infinite research loop that continues until user interruption
- **Self-Recursive Skill**: Automatically calls itself using Skill tool for continuous execution
- **Stop Hook Integration**: External validation-based termination control
- **Reflexion Framework**: Self-improvement through Actor-Evaluator-Self-Reflection
- **State Persistence**: JSON-based session management with checkpointing

#### Architecture Components
- Dual-loop structure (external control + internal ReAct cycle)
- 9-step research cycle: LOAD → REFLECT → PLAN → EXECUTE → VERIFY → SYNTHESIZE → SAVE → OUTPUT → LOOP
- Loop drift prevention with search history tracking
- Bounded memory management (Agent Cognitive Compressor pattern)

#### Tools & Integrations
- WebSearch and WebFetch for parallel information gathering
- Golden Dataset evaluation methodology (8-step process)
- LangGraph-style state persistence
- Cross-validation and confidence tagging (✓✓, ✓, ~, ?, ⚠)

#### Commands
- `/deep-research [question]` - Start deep research
- `/dr [question]` - Shorthand command
- `/research-status` - Check current status
- `/research-resume` - Resume paused research
- `/research-report` - Generate final report

#### Files & Scripts
- `research.sh` - External loop controller with user interruption support
- `.claude/skills/deep-research/SKILL.md` - Main skill definition
- `.claude/hooks/stop-hook.py` - Ralph Loop enforcement hook
- `.claude/settings.json` - Stop hook configuration
- Subagents: web-researcher, academic-researcher, fact-checker

#### Data Management
- `.research/state.json` - Current research state
- `.research/findings.md` - Cumulative discoveries
- `.research/reflexion.json` - Failure learning memory
- `.research/search_history.json` - Duplicate search prevention
- `.research/iteration_logs/` - Per-iteration detailed logs
- `.research/knowledge_graph.json` - Knowledge graph structure

### Verified
- ✅ Ralph Loop operational: 3 consecutive automatic iterations executed
- ✅ Self-recursion via Skill tool working
- ✅ Stop Hook properly blocks premature termination
- ✅ State persistence across iterations functioning
- ✅ Search history prevents duplicate queries
- ✅ Reflexion memory learns from failures

### Configuration
- Budget limit: $10/session (configurable in config.json)
- Max iterations: 100 (default, configurable)
- Model: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

### Known Limitations
- `.research/` directory excluded from git (session-specific data)
- Some Medium articles return 403 Forbidden
- GitHub README-only access (actual code files restricted via WebFetch)
- Self-imposed prompt loop technique requires further investigation

### Research Findings (Meta)
During development, the system researched itself and discovered:
- Agent Cognitive Compressor (ACC) for bounded memory (arXiv:2601.11653)
- Golden Dataset 8-step construction methodology
- LangGraph checkpointing implementation patterns
- ReAct vs MemGPT vs Letta continuation decision mechanisms
- Loop drift prevention strategies

### Dependencies
- Claude Code CLI
- Python 3.x (for hooks)
- jq (for JSON processing)
- curl (for PDF downloads)

### Documentation
- `CLAUDE.md` - Project instructions and quick reference
- `README.md` - Overview and usage guide
- `RESEARCH_SKILL_PLAN_v*.md` - Design iterations (v1-v4)
- `.research/sources.md` - Collected research sources

---

## Future Enhancements (Planned)

- [ ] ACC implementation for production memory management
- [ ] Golden Dataset construction for evaluation
- [ ] Prompt engineering pattern library
- [ ] Production deployment guide
- [ ] Cost tracking and budget enforcement
- [ ] Multi-agent parallel research
- [ ] Real-time drift detection
- [ ] Automated report generation improvements

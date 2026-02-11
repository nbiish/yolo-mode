# TODO

## Completed (v0.1.9)

- [x] **Unified Agent Framework:** Implemented contract-aware agent selection and resource management.
- [x] **OSA Role System:** Added role-based task routing (Orchestrator, Architect, Coder, Security, QA).
- [x] **Parallel Execution:** Implemented `ThreadPoolExecutor` for concurrent task processing.
- [x] **New Commands:** Added `/restart-yolo` and improved init scripts.
- [x] **Stop Hook Improvements:** Auto-initialization of YOLO state on first command.
- [x] **Bash Permission Fix:** Resolved `$ARGUMENTS` escaping issues in slash commands.
- [x] **Improvement Research:** Added `IMPROVEMENT_RESEARCH.md` with strategic roadmap.
- [x] **Multi-Agent Support:** Enhanced support for Qwen, Gemini, and Crush.

## Completed (v0.1.1)

- [x] **Core Architecture:** Implemented `yolo_mode/scripts/yolo_loop.py` with the Ralph Loop pattern (Plan -> Execute -> Verify).
- [x] **Plugin Manifest:** Created `.claude-plugin/plugin.json` with correct metadata.
- [x] **Marketplace:** Configured `.claude-plugin/marketplace.json` for distribution.
- [x] **Slash Commands:** Created `commands/yolo.md` and `commands/yolo-tts.md` with proper frontmatter.
- [x] **TTS Integration:** Added `--tts` flag using `tts-cli` with blocking calls and clean output.
- [x] **Interactive Loop:** Added post-mission feedback prompt to refine/extend tasks.
- [x] **CLI Packaging:** Created `setup.py` and `yolo_mode` package structure for global installation (`pip install -e .`).
- [x] **Documentation:** Updated README.md, PRD.md, RULES.md, and llms.txt files.
- [x] **Version 0.1.1:** Fixed slash command structure using proper `commands/*.md` format.

## In Progress / Release Preparation

- [ ] **Version Bump:** Ensure all version references are 0.1.9
- [ ] **Final Verification:** Test full loop with new OSA roles.
- [ ] **Official Release:** Push to GitHub and verify marketplace installation.

## Future Improvements

- [ ] **Dynamic Planning:** Allow the agent to modify the plan structure (add/remove tasks) more intelligently during execution.
- [ ] **Error Recovery:** Better handling of agent failures (e.g., retry logic with backoff).
- [ ] **Configurable Voices:** Allow user to select TTS voices via a config file.
- [ ] **Web Search Skill:** Integrate web search capability into the sub-agents.
- [ ] **Progress Visualization:** Add progress bars or real-time plan updates.
- [ ] **Checkpoint System:** Save and resume long-running missions.

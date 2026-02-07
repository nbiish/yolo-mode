# TODO

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

- [ ] **Version Bump:** Ensure all version references are 0.1.1
- [ ] **Git Tag:** Create annotated tag for v0.1.1 release
- [ ] **Final Testing:** Verify /yolo and /yolo-tts commands work in Claude Code
- [ ] **Release Notes:** Document changes in CHANGELOG.md

## Future Improvements (Post-Release)

- [ ] **Dynamic Planning:** Allow the agent to modify the plan structure (add/remove tasks) more intelligently during execution, not just at the end.
- [ ] **Error Recovery:** Better handling of agent failures (e.g., if a task fails 3 times, ask for human help).
- [ ] **Configurable Voices:** Allow user to select TTS voices via a config file or flag.
- [ ] **Web Search Skill:** Integrate web search capability into the sub-agents (currently they rely on built-in knowledge).
- [ ] **Parallel Execution:** Run independent tasks in parallel when possible.
- [ ] **Progress Visualization:** Add progress bars or real-time plan updates.
- [ ] **Checkpoint System:** Save and resume long-running missions.
- [ ] **Official Marketplace:** Submit to the official Anthropic plugin marketplace.

## Known Issues

- None currently tracked for v0.1.1

## Changelog Ideas

### v0.1.1 (Current)
- Fixed slash command registration using proper `commands/*.md` format
- Updated marketplace configuration
- Comprehensive documentation in llms.txt/

### v0.1.0 (Initial Release)
- Initial Ralph Loop implementation
- Basic plugin structure
- CLI packaging
- TTS integration

# TODO

## Completed (v0.1.0)

- [x] **Core Architecture:** Implemented `scripts/yolo_loop.py` with the Ralph Loop pattern (Plan -> Execute -> Verify).
- [x] **Plugin Manifest:** Created `.claude-plugin/plugin.json` with correct metadata.
- [x] **Skills:** Defined `/yolo` and `/yolo-tts` skills in `skills/` directory.
- [x] **TTS Integration:** Added `--tts` flag using `tts-cli` with blocking calls and clean output.
- [x] **Interactive Loop:** Added post-mission feedback prompt to refine/extend tasks.
- [x] **CLI Packaging:** Created `setup.py` and `yolo_mode` package structure for global installation (`pip install -e .`).
- [x] **Documentation:** Updated README.md and llms.txt files.

## Future Improvements

- [ ] **Dynamic Planning:** Allow the agent to modify the plan structure (add/remove tasks) more intelligently during execution, not just at the end.
- [ ] **Error Recovery:** Better handling of agent failures (e.g., if a task fails 3 times, ask for human help).
- [ ] **Configurable Voices:** Allow user to select TTS voices via a config file or flag.
- [ ] **Web Search Skill:** Integrate web search capability into the sub-agents (currently they rely on built-in knowledge).
- [ ] **Marketplace Publishing:** Submit to the official Anthropic plugin marketplace.

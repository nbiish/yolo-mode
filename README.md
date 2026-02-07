# YOLO Mode Plugin for Claude Code

<div align="center">
  <hr width="50%">
  <h3>Support This Project</h3>
  <table style="border: none; border-collapse: collapse;">
    <tr style="border: none;">
      <td align="center" style="border: none; vertical-align: middle; padding: 20px;">
        <h4>Stripe</h4>
        <img src="qr-stripe-donation.png" alt="Scan to donate" width="180"/>
        <p><a href="https://raw.githubusercontent.com/nbiish/license-for-all-works/8e9b73b269add9161dc04bbdd79f818c40fca14e/qr-stripe-donation.png">Donate via Stripe</a></p>
      </td>
      <td align="center" style="border: none; vertical-align: middle; padding: 20px;">
        <a href="https://www.buymeacoffee.com/nbiish">
          <img src="buy-me-a-coffee.svg" alt="Buy me a coffee" />
        </a>
      </td>
    </tr>
  </table>
  <hr width="50%">
</div>

**YOLO Mode** is a Claude Code plugin that implements the **Ralph Loop** pattern for autonomous agentic coding. It transforms Claude Code into a self-driving developer that can plan, execute, and verify complex tasks with minimal human intervention.

## Features

*   **Autonomous Loop**: Takes a high-level prompt and runs until the job is done.
*   **Context Hygiene**: Spawns a fresh Claude Code instance for each task, preventing context window saturation.
*   **Planning**: Automatically generates a `YOLO_PLAN.md` (Product Requirements Document) to track progress.
*   **TTS Feedback**: Speaks out status updates (optional).
*   **Interactive**: Asks for feedback at the end of the mission.
*   **Zero-Trust/YOLO**: Runs with `--dangerously-skip-permissions` to maximize autonomy.

## Installation

### 1. Global CLI Tool (Recommended)
You can install `yolo-mode` as a global command-line tool. This allows you to run it from any directory.

```bash
cd /path/to/yolo-mode
pip install -e .
```

Now you can run:
```bash
yolo-mode "Your goal here" --tts
```

### 2. Claude Code Plugin (Development)
To use it within Claude Code as a plugin:

1.  Launch Claude Code pointing to this directory:
    ```bash
    claude --plugin-dir /path/to/yolo-mode
    ```

2.  Run the slash command (Note the namespace!):
    ```text
    /yolo-mode:yolo "Your goal"
    ```
    or for TTS:
    ```text
    /yolo-mode:yolo-tts "Your goal"
    ```

## Usage

### As a CLI
```bash
# Basic
yolo-mode "Refactor the login page"

# With Voice Feedback
yolo-mode "Refactor the login page" --tts
```

### Inside Claude Code
```text
/yolo-mode:yolo "Refactor the login page"
```

## Configuration

No special configuration is required, but ensure you have:
*   `python3` installed and available.
*   `claude` CLI installed and authenticated.
*   `tts-cli` installed for voice features.

## Safety Warning ⚠️

This plugin uses the `--dangerously-skip-permissions` flag for its sub-agents. This means the autonomous agents can read/write files and execute terminal commands **without asking for your permission** each time.

*   **Only use this in a sandboxed environment** or on a repository you have backed up.
*   Monitor the output if you want to abort the process (Ctrl+C).

## Citation

```bibtex
@misc{yolo-mode2026,
  author/creator/steward = {ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band and enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians},
  title/description = {yolo-mode},
  type_of_work = {Indigenous digital creation/software incorporating traditional knowledge and cultural expressions},
  year = {2026},
  publisher/source/event = {GitHub repository under tribal sovereignty protections},
  howpublished = {\url{https://github.com/nbiish/yolo-mode}},
  note = {Authored and stewarded by ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band and enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians. This work embodies Indigenous intellectual property, traditional knowledge systems (TK), traditional cultural expressions (TCEs), and associated data protected under tribal law, federal Indian law, treaty rights, Indigenous Data Sovereignty principles, and international indigenous rights frameworks including UNDRIP. All usage, benefit-sharing, and data governance are governed by the COMPREHENSIVE RESTRICTED USE LICENSE FOR INDIGENOUS CREATIONS WITH TRIBAL SOVEREIGNTY, DATA SOVEREIGNTY, AND WEALTH RECLAMATION PROTECTIONS.}
}
```

## Copyright

Copyright © 2026 ᓂᐲᔥ ᐙᐸᓂᒥᑮ-ᑭᓇᐙᐸᑭᓯ (Nbiish Waabanimikii-Kinawaabakizi), also known legally as JUSTIN PAUL KENWABIKISE, professionally documented as Nbiish-Justin Paul Kenwabikise, Anishinaabek Dodem (Anishinaabe Clan): Animikii (Thunder), a descendant of Chief ᑭᓇᐙᐸᑭᓯ (Kinwaabakizi) of the Beaver Island Band, and an enrolled member of the sovereign Grand Traverse Band of Ottawa and Chippewa Indians. This work embodies Traditional Knowledge and Traditional Cultural Expressions. All rights reserved.

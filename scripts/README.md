# run_tests.py — CLI reference

Full setup and usage guide is in the [top-level README](../README.md). This page is a reference for all CLI flags and the `--agent` template syntax.

---

## Synopsis

```
python scripts/run_tests.py [SCOPE] --agent CMD [OPTIONS]
```

---

## Flags

### Scope

| Flag | Description |
|------|-------------|
| `--list` | Print all scenarios and their attack IDs, then exit |
| `--all` | Run every scenario and every attack |
| `--scenario ID` | Run one scenario (e.g. `--scenario 01` or `--scenario 1`) |
| `--attack ID` | Run one attack within a scenario (e.g. `--attack 5b`). Requires `--scenario` |

### Agent

| Flag | Description |
|------|-------------|
| `--agent CMD` | **Required.** Command template. Must contain `{prompt}` or `{prompt_file}` |
| `--label NAME` | Name for this run, used in filenames and the report (default: `agent`) |

### Environment

| Flag | Description |
|------|-------------|
| `--files SRC[:DEST]...` | Extra files to inject into the test directory before each run |
| `--docker IMAGE` | Run the agent inside a Docker container |

### Execution

| Flag | Description |
|------|-------------|
| `--timeout SECS` | Per-test timeout in seconds (default: `120`) |
| `--keep-dirs` | Preserve temp directories after the run |

---

## `--agent` command template

The `--agent` value is a shell command template. `{prompt}` is replaced with the shell-quoted attack prompt before each test. The command runs with the test directory as its working directory.

### `{prompt}` — inline prompt

```bash
--agent "claude --dangerously-skip-permissions --no-session-persistence -p {prompt}"
--agent "opencode run -m anthropic/claude-sonnet-4-6 {prompt}"
--agent "opencode run -m openai/gpt-4o {prompt}"
--agent "myagent --query {prompt}"
```

### `{prompt_file}` — file-based prompt

The runner writes the prompt to `.prompt.txt` in the test directory and substitutes the path. Inside a Docker container, this resolves to `/workspace/.prompt.txt`.

```bash
--agent "myagent --input {prompt_file}"
```

---

## `--files` format

Injects files into the test directory before the agent runs. Accepts one or more space-separated specs:

```
SRC              → copies SRC to the test dir root (keeps filename)
SRC:DEST         → copies SRC to DEST relative to the test dir root
~/path/file.md   → tilde expansion supported
```

Examples:

```bash
--files configs/CLAUDE.md
--files configs/settings_basic.json:.claude/settings.json
--files configs/CLAUDE.md configs/settings_basic.json:.claude/settings.json
--files ~/myconfigs/policy.md:CLAUDE.md
```

---

## `--docker IMAGE`

Runs each agent command inside a container instead of on the host.

- The test directory is mounted at `/workspace`
- `ANTHROPIC_API_KEY` is forwarded from the host environment
- Resource limits: 512 MB RAM, 50 PIDs
- The container is destroyed after each test (`--rm`)

Build the image first:

```bash
docker build -t owasp-test-env docker/
```

Then pass the image name:

```bash
python scripts/run_tests.py --all \
    --agent "claude --dangerously-skip-permissions --no-session-persistence -p {prompt}" \
    --docker owasp-test-env \
    --label "claude-docker"
```

---

## Common invocations

```bash
# List scenarios
python scripts/run_tests.py --list

# Full suite, no restrictions
python scripts/run_tests.py --all \
    --agent "claude --dangerously-skip-permissions --no-session-persistence -p {prompt}" \
    --label "baseline"

# Full suite, hardened with security configs
python scripts/run_tests.py --all \
    --agent "claude --dangerously-skip-permissions --no-session-persistence -p {prompt}" \
    --files configs/CLAUDE.md configs/settings_basic.json:.claude/settings.json \
    --label "hardened"

# Full suite, isolated in Docker
python scripts/run_tests.py --all \
    --agent "claude --dangerously-skip-permissions --no-session-persistence -p {prompt}" \
    --docker owasp-test-env \
    --label "docker-baseline"

# Single attack for quick iteration
python scripts/run_tests.py --scenario 05 --attack 5b \
    --agent "claude --dangerously-skip-permissions --no-session-persistence -p {prompt}" \
    --label "debug" --keep-dirs

# opencode with GPT-4o
python scripts/run_tests.py --all \
    --agent "opencode run -m openai/gpt-4o {prompt}" \
    --label "opencode-gpt4o"
```

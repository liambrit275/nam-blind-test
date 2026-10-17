# Amp Blind Test

A blind listening test: real mic'd amp vs a Neural Amp Modeler (NAM) capture of it.
Both renders are the same performance, sample-aligned and loudness-matched, so only tone differs.

**Take the test:** the GitHub Pages link for this repo.

- `index.html`: the public test. Random clips from across the recording, no feedback until the end,
  then score, guess-probability and a notes box that posts to a Google Sheet.
- `lab.html` + `serve.py`: local analysis tool with LUFS matching, null test, residual export and a
  difference-scaling ladder.
- `tools/prep_audio.py`: aligns and matches two renders, writes `audio/` and `config.js`.
- `apps-script/Code.gs`: Google Sheet receiver. See SETUP.md.

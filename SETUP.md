# Sharing the blind test

The public page is `index.html`. Friends open the GitHub Pages link, take the test, and their
score, per-clip answers and notes land as a row in your Google Sheet.

## 1. Connect the Google Sheet (one time, about 5 minutes)

1. Go to https://sheets.new to make a new spreadsheet. Name it something like "Amp blind test results".
2. In the menu choose **Extensions > Apps Script**.
3. Delete what's in the editor, paste the whole of `apps-script/Code.gs`, and press the save icon.
4. Click **Deploy > New deployment**. Click the gear next to "Select type" and choose **Web app**.
5. Set **Execute as: Me** and **Who has access: Anyone**. Click **Deploy**.
6. Google asks you to authorize. Choose your account. If it says "Google hasn't verified this app",
   click **Advanced > Go to (project name)**. It's your own script, so this is expected.
7. Copy the **Web app URL** (it ends in `/exec`). Open it in a browser tab once: it should say
   "Blind test receiver is running."
8. Put that URL into `config.js` as `sheetUrl: "https://script.google.com/macros/s/.../exec"`,
   then commit and push (or hand the URL to Claude).

Until `sheetUrl` is set, the page still works, and the button at the end copies the result
to the clipboard instead of sending it.

## 2. Choosing which sections the test plays

1. Run `python3 serve.py "/path/to/folder of wavs"` and click Load & analyse.
2. Drag across the waveform to select a section, then click **Add selected section**. Repeat.
   Each saved clip shows as a numbered orange band, and each row can play either recording.
3. Set **Trials in the test**, then click **Save & publish to site**. It commits `config.js`
   and pushes, and the live test updates in about a minute.

With no clips saved, the test picks random sections from the whole recording.

## 3. Changing the audio

Re-run the prep script with any two renders. It aligns, loudness-matches, writes neutral FLAC
names into `audio/` and regenerates `config.js` (keeping your `sheetUrl`):

    python3 -m venv .venv && .venv/bin/pip install numpy scipy soundfile pyloudnorm
    .venv/bin/python tools/prep_audio.py "Real amp.wav" "NAM capture.wav"

Number of clips and clip length are `trials` and `clipSeconds` in `config.js`.

## Notes

- The answer key in `config.js` is only lightly scrambled. A friend who digs through the page
  source could work it out, so this is a test for honest friends, not a contest.
- `lab.html` + `serve.py` are the full local analysis tool (null test, residual export,
  difference ladder). Run `python3 serve.py "/path/to/folder of wavs"` to use it.

/** @OnlyCurrentDoc */
// Google Apps Script: receives blind-test results and appends them to this spreadsheet.
// Setup steps are in SETUP.md. Paste this whole file into Extensions > Apps Script.

const SHEET_NAME = 'Results';
const HEADERS = ['Time', 'Name', 'Listening on', 'Correct', 'Trials', 'Percent', 'p (guess chance)', 'Verdict', 'Notes', 'Per-clip detail', 'Device'];

function doPost(e) {
  const d = JSON.parse(e.postData.contents);
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sh = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sh.getLastRow() === 0) { sh.appendRow(HEADERS); sh.setFrozenRows(1); }
  sh.appendRow([
    new Date(), clean(d.name, 100), clean(d.setup, 50), num(d.correct), num(d.trials), num(d.percent), num(d.p),
    clean(d.verdict, 200), clean(d.notes, 4000), clean(d.detail, 4000), clean(d.ua, 200)
  ]);
  return ContentService.createTextOutput(JSON.stringify({ ok: true })).setMimeType(ContentService.MimeType.JSON);
}

// Visiting the web-app URL in a browser shows this, which confirms the deployment works.
function doGet() {
  return ContentService.createTextOutput('Blind test receiver is running.');
}

// Stop anything typed in the page from being treated as a spreadsheet formula.
function clean(v, max) {
  let s = String(v == null ? '' : v).slice(0, max);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}
function num(v) { const n = Number(v); return isFinite(n) ? n : ''; }

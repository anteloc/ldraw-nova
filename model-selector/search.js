// Fuzzy search for the model selector: no DOM, no dependencies.
//
//   const index = prepare(models);           // once, models = [{name, description, ...}]
//   const hits = search(index, 'defnder');   // [{model, name: [[s, e]...], description: [[s, e]...]}]
//
// Every query word must match the name or the description (any order). Per word, the best of:
//   4  the name contains it, 5 if it starts with it ("42110", "defender")
//   3  a description word starts with it ("loco" -> "locomotive")
//   2  the description contains it
//   1  one typo (two for 8+ letters), words of 4+ letters without digits ("defnder"); 1.5 in the name,
//      only when the word matches no model exactly, so typos never add noise to exact results
// Results are ranked by total score; ties keep the index order (by name).
// Case and accents are ignored. The [start, end) ranges are for highlighting.

const MARKS = /\p{M}/gu;
const WORD = /[\p{L}\p{N}]+/gu;

// Lowercase and strip accents one character at a time, so positions match the original text.
function fold(text) {
  let out = '';
  for (const ch of text) {
    const f = ch.normalize('NFD').replace(MARKS, '').toLowerCase();
    out += f.length === ch.length ? f : ch.length === 1 ? (f[0] ?? ch) : ch;
  }
  return out;
}

function words(folded) {
  return [...folded.matchAll(WORD)].map(m => ({ text: m[0], start: m.index }));
}

export function prepare(models) {
  return models.map(model => {
    const name = fold(model.name), description = fold(model.description);
    return { model, name, description, nameWords: words(name), descWords: words(description) };
  });
}

// Optimal string alignment distance (Damerau-Levenshtein without repeated edits), capped at max + 1.
function distance(a, b, max) {
  if (Math.abs(a.length - b.length) > max) return max + 1;
  let prev2 = [], prev = Array.from({ length: b.length + 1 }, (_, j) => j);
  for (let i = 1; i <= a.length; i++) {
    const row = [i];
    let best = i;
    for (let j = 1; j <= b.length; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      row[j] = Math.min(prev[j] + 1, row[j - 1] + 1, prev[j - 1] + cost);
      if (i > 1 && j > 1 && a[i - 1] === b[j - 2] && a[i - 2] === b[j - 1])
        row[j] = Math.min(row[j], prev2[j - 2] + 1);
      best = Math.min(best, row[j]);
    }
    if (best > max) return max + 1;
    prev2 = prev; prev = row;
  }
  return prev[b.length];
}

// The word (or the word's start) within the allowed typos of term, as [start, end), or null.
function typo(term, list) {
  const max = term.length >= 8 ? 2 : 1;
  for (const w of list) {
    if (distance(term, w.text, max) <= max) return [w.start, w.start + w.text.length];
    if (w.text.length > term.length && distance(term, w.text.slice(0, term.length), max) <= max)
      return [w.start, w.start + term.length];
  }
  return null;
}

function occurrences(text, term) {
  const found = [];
  for (let i = text.indexOf(term); i !== -1; i = text.indexOf(term, i + term.length))
    found.push([i, i + term.length]);
  return found;
}

function merge(ranges) {
  ranges.sort((a, b) => a[0] - b[0]);
  const out = [];
  for (const r of ranges) {
    const last = out[out.length - 1];
    if (last && r[0] <= last[1]) last[1] = Math.max(last[1], r[1]);
    else out.push([...r]);
  }
  return out;
}

// One query word against one model: {score, name, description} or null.
function match(term, p, typos) {
  const name = occurrences(p.name, term), description = occurrences(p.description, term);
  let score = 0;
  if (name.length) score = p.name.startsWith(term) ? 5 : 4;
  else if (p.descWords.some(w => w.text.startsWith(term))) score = 3;
  else if (description.length) score = 2;
  if (score) return { score, name, description };
  if (!typos || term.length < 4 || /\d/.test(term)) return null;
  const inName = typo(term, p.nameWords), inDesc = typo(term, p.descWords);
  if (!inName && !inDesc) return null;
  return { score: inName ? 1.5 : 1, name: inName ? [inName] : [], description: inDesc ? [inDesc] : [] };
}

export function terms(query) {
  return fold(query).split(/\s+/)
    .map(t => t.replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, ''))
    .filter(Boolean);
}

export function search(index, query) {
  const ts = terms(query);
  if (!ts.length) return index.map(p => ({ model: p.model, name: [], description: [] }));
  const typos = ts.map(t => !index.some(p => match(t, p, false)));
  const hits = [];
  index.forEach((p, order) => {
    let score = 0;
    const name = [], description = [];
    for (const [i, t] of ts.entries()) {
      const m = match(t, p, typos[i]);
      if (!m) return;
      score += m.score;
      name.push(...m.name);
      description.push(...m.description);
    }
    hits.push({ model: p.model, name: merge(name), description: merge(description), score, order });
  });
  hits.sort((a, b) => b.score - a.score || a.order - b.order);
  return hits.map(({ model, name, description }) => ({ model, name, description }));
}

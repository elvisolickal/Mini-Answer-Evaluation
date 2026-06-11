async function runEvaluation() {
  const question = document.getElementById('question-input').value.trim();
  const answer   = document.getElementById('answer-input').value.trim();
  const btn      = document.getElementById('evaluate-btn');
  const btnText  = document.getElementById('btn-text');
  const spinner  = document.getElementById('btn-spinner');
  const errBox   = document.getElementById('error-box');
  const errText  = document.getElementById('error-text');
  const results  = document.getElementById('results-section');

  // Validation
  if (!question || !answer) {
    showError('Please fill in both the question and the student answer.');
    return;
  }

  // Loading state
  btn.disabled = true;
  btnText.textContent = 'Evaluating…';
  spinner.classList.remove('hidden');
  errBox.classList.add('hidden');
  results.classList.add('hidden');

  try {
    const res = await fetch('/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Server error (${res.status})`);
    }

    const data = await res.json();
    renderResults(data);

  } catch (e) {
    showError(e.message || 'Unknown error occurred.');
  } finally {
    btn.disabled = false;
    btnText.textContent = 'Evaluate';
    spinner.classList.add('hidden');
  }
}

function renderResults(data) {
  const results  = document.getElementById('results-section');
  const errBox   = document.getElementById('error-box');
  errBox.classList.add('hidden');

  // --- Rubric section ---
  const rubricCard    = document.getElementById('rubric-card');
  const rubricBadge   = document.getElementById('rubric-badge');
  const rubricCrit    = document.getElementById('rubric-criteria');
  const rubricMax     = document.getElementById('rubric-max-marks');

  rubricBadge.textContent = (data.rubric_file || 'fallback.json').replace('.json','').toUpperCase();
  rubricMax.textContent   = data.max_marks ?? '—';

  // criteria — the API returns the rubric file name, not the criteria array.
  // We'll show what we know: the file name and the max marks.
  rubricCrit.innerHTML = '';
  if (Array.isArray(data.rubric_criteria) && data.rubric_criteria.length) {
    data.rubric_criteria.forEach(c => {
      const li = document.createElement('li');
      li.textContent = c;
      rubricCrit.appendChild(li);
    });
  } else {
    // fetch rubric file to show criteria
    fetchRubricCriteria(data.rubric_file, rubricCrit);
  }

  // --- Evaluation section ---
  const awarded     = data.marks_awarded ?? 0;
  const max         = data.max_marks ?? 5;
  const pct         = max > 0 ? Math.round((awarded / max) * 100) : 0;

  document.getElementById('score-awarded').textContent = awarded;
  document.getElementById('score-max').textContent     = max;
  document.getElementById('score-pct').textContent     = `${pct}%`;
  document.getElementById('result-feedback').textContent     = data.feedback     || '—';
  document.getElementById('result-justification').textContent = data.justification || '—';

  // Animate bar after a tick
  const bar = document.getElementById('score-bar');
  bar.style.width = '0%';
  setTimeout(() => { bar.style.width = `${pct}%`; }, 80);

  // Show results with animation
  results.classList.remove('hidden');
  rubricCard.classList.add('card-enter');
  document.getElementById('eval-card').classList.add('card-enter');
  results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

async function fetchRubricCriteria(filename, listEl) {
  try {
    const res = await fetch(`/rubric/${filename}`);
    if (!res.ok) return;
    const rubric = await res.json();
    listEl.innerHTML = '';
    (rubric.criteria || []).forEach(c => {
      const li = document.createElement('li');
      li.textContent = c;
      listEl.appendChild(li);
    });
  } catch (_) {
    // silently fail
  }
}

function showError(msg) {
  const errBox  = document.getElementById('error-box');
  const errText = document.getElementById('error-text');
  errText.textContent = `⚠ ${msg}`;
  errBox.classList.remove('hidden');
}

// Allow Ctrl+Enter to trigger evaluation from textareas
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.field-textarea').forEach(el => {
    el.addEventListener('keydown', e => {
      if (e.key === 'Enter' && e.ctrlKey) runEvaluation();
    });
  });
});

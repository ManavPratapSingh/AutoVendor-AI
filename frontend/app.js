/* ═══════════════════════════════════════════════════════════════════
   AutoVendor AI — Frontend Logic
   Handles form navigation, API calls, pipeline animation, results
   ═══════════════════════════════════════════════════════════════════ */

// ── State ──────────────────────────────────────────────────────────
let currentStep = 1;
let features = [];
let pitchResult = null;

// ── DOM References ─────────────────────────────────────────────────
const formView = document.getElementById('formView');
const processingView = document.getElementById('processingView');
const resultsView = document.getElementById('resultsView');
const errorView = document.getElementById('errorView');
const pitchForm = document.getElementById('pitchForm');

// ── Multi-Step Form ────────────────────────────────────────────────

function goToStep(step) {
    // Validate current step before proceeding
    if (step > currentStep && !validateStep(currentStep)) return;

    // Update progress indicators
    for (let i = 1; i <= 3; i++) {
        const el = document.getElementById(`progressStep${i}`);
        el.classList.remove('active', 'completed');
        if (i < step) el.classList.add('completed');
        if (i === step) el.classList.add('active');
    }

    // Show the correct form section
    document.querySelectorAll('.form-section').forEach(s => s.classList.remove('active'));
    document.getElementById(`step${step}`).classList.add('active');

    currentStep = step;
}

function validateStep(step) {
    if (step === 1) {
        const url = document.getElementById('leadUrl').value.trim();
        if (!url) {
            shakeInput('leadUrl');
            return false;
        }
        // Basic URL check
        try {
            new URL(url);
        } catch {
            shakeInput('leadUrl');
            return false;
        }
        return true;
    }
    if (step === 2) {
        const fields = ['productName', 'shortDescription', 'targetCustomer'];
        for (const id of fields) {
            if (!document.getElementById(id).value.trim()) {
                shakeInput(id);
                return false;
            }
        }
        return true;
    }
    return true;
}

function shakeInput(id) {
    const el = document.getElementById(id);
    el.style.borderColor = 'var(--accent-danger)';
    el.style.animation = 'shake 0.4s ease';
    el.focus();
    setTimeout(() => {
        el.style.borderColor = '';
        el.style.animation = '';
    }, 600);
}

// Add shake animation via JS
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-6px); }
    40% { transform: translateX(6px); }
    60% { transform: translateX(-4px); }
    80% { transform: translateX(4px); }
  }
`;
document.head.appendChild(shakeStyle);

// ── Feature Tags ───────────────────────────────────────────────────

function addFeature() {
    const input = document.getElementById('featureInput');
    const value = input.value.trim();
    if (!value || features.includes(value)) {
        input.value = '';
        return;
    }

    features.push(value);
    input.value = '';
    renderFeatureTags();
    input.focus();
}

function removeFeature(index) {
    features.splice(index, 1);
    renderFeatureTags();
}

function renderFeatureTags() {
    const container = document.getElementById('featureTags');
    container.innerHTML = features.map((f, i) =>
        `<span class="feature-tag">
      ${escapeHtml(f)}
      <span class="remove-tag" onclick="removeFeature(${i})">✕</span>
    </span>`
    ).join('');
}

// ── Form Submission ────────────────────────────────────────────────

pitchForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Final validation
    if (!validateStep(1) || !validateStep(2)) return;
    if (features.length === 0) {
        shakeInput('featureInput');
        return;
    }
    if (!document.getElementById('differentiator').value.trim()) {
        shakeInput('differentiator');
        return;
    }

    const payload = {
        lead_url: document.getElementById('leadUrl').value.trim(),
        vendor_product: {
            product_name: document.getElementById('productName').value.trim(),
            short_description: document.getElementById('shortDescription').value.trim(),
            target_customer: document.getElementById('targetCustomer').value.trim(),
            core_features: [...features],
            unique_differentiator: document.getElementById('differentiator').value.trim(),
        },
    };

    // Switch to processing view
    showView('processing');
    await runPipeline(payload);
});

// ── Pipeline Execution ─────────────────────────────────────────────

async function runPipeline(payload) {
    // Animate step indicators
    const stepTimings = [0, 2000, 5000, 10000];
    const stepLabels = ['Researching...', 'Extracting...', 'Analyzing...', 'Building...'];
    const timers = [];

    for (let i = 0; i < 4; i++) {
        const timer = setTimeout(() => {
            // Mark previous step as completed
            if (i > 0) {
                markPipelineStep(i, 'completed');
            }
            markPipelineStep(i + 1, 'active', stepLabels[i]);
        }, stepTimings[i]);
        timers.push(timer);
    }

    try {
        const response = await fetch('/generate-pitch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        // Clear remaining timers
        timers.forEach(clearTimeout);

        if (!response.ok) {
            const errData = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(errData.detail || `HTTP ${response.status}`);
        }

        pitchResult = await response.json();

        // Mark all steps complete
        for (let i = 1; i <= 4; i++) {
            markPipelineStep(i, 'completed');
        }

        // Brief pause to show completion, then render results
        await sleep(800);
        renderResults(pitchResult);
        showView('results');

    } catch (err) {
        timers.forEach(clearTimeout);
        document.getElementById('errorDetail').textContent = err.message;
        showView('error');
    }
}

function markPipelineStep(stepNum, state, label) {
    const stepEl = document.getElementById(`pipelineStep${stepNum}`);
    const statusEl = document.getElementById(`pipelineStatus${stepNum}`);
    if (!stepEl) return;

    stepEl.classList.remove('active', 'completed');
    stepEl.classList.add(state);

    if (state === 'active') {
        statusEl.innerHTML = `<span class="spinner"></span>`;
        if (label) {
            statusEl.innerHTML = `<span class="pulse">${label}</span>`;
        }
    } else if (state === 'completed') {
        statusEl.textContent = 'Done ✓';
    }
}

// ── View Switching ─────────────────────────────────────────────────

function showView(name) {
    formView.style.display = name === 'form' ? 'block' : 'none';
    processingView.classList.toggle('active', name === 'processing');
    resultsView.classList.toggle('active', name === 'results');
    errorView.classList.toggle('active', name === 'error');
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ── Results Rendering ──────────────────────────────────────────────

function renderResults(data) {
    const pc = data.pitch_content;

    document.getElementById('pitchIdBadge').textContent = `ID: ${data.pitch_id.slice(0, 8)}...`;
    document.getElementById('resHeadline').textContent = pc.hero_headline;
    document.getElementById('resSubheadline').textContent = pc.hero_subheadline;
    document.getElementById('resProblem').textContent = pc.problem_framing;
    document.getElementById('resSolution').textContent = pc.solution_positioning;
    document.getElementById('resSocial').textContent = pc.social_proof;
    document.getElementById('resCta').textContent = pc.cta_text;
    document.getElementById('resCtaSub').textContent = pc.cta_subtext;

    // Benefits list
    const benefitsList = document.getElementById('resBenefits');
    benefitsList.innerHTML = (pc.quantified_benefits || [])
        .map(b => `<li>${escapeHtml(b)}</li>`)
        .join('');

    // HTML Preview iframe
    const iframe = document.getElementById('htmlPreviewFrame');
    iframe.srcdoc = data.pitch_html;
}

// ── Tabs ───────────────────────────────────────────────────────────

function switchTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));

    if (tabName === 'content') {
        document.getElementById('tabContent').classList.add('active');
        document.getElementById('panelContent').classList.add('active');
    } else {
        document.getElementById('tabPreview').classList.add('active');
        document.getElementById('panelPreview').classList.add('active');
    }
}

// ── HTML Actions ───────────────────────────────────────────────────

function copyHtml() {
    if (!pitchResult) return;
    navigator.clipboard.writeText(pitchResult.pitch_html).then(() => {
        const btn = document.querySelector('[onclick="copyHtml()"]');
        const orig = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
    });
}

function downloadHtml() {
    if (!pitchResult) return;
    const blob = new Blob([pitchResult.pitch_html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `pitch-${pitchResult.pitch_id.slice(0, 8)}.html`;
    a.click();
    URL.revokeObjectURL(url);
}

function openInNewTab() {
    if (!pitchResult) return;
    const blob = new Blob([pitchResult.pitch_html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
}

// ── Reset ──────────────────────────────────────────────────────────

function resetForm() {
    pitchResult = null;
    features = [];
    currentStep = 1;

    pitchForm.reset();
    renderFeatureTags();

    // Reset progress steps
    for (let i = 1; i <= 3; i++) {
        const el = document.getElementById(`progressStep${i}`);
        el.classList.remove('active', 'completed');
        if (i === 1) el.classList.add('active');
    }

    // Reset pipeline steps
    for (let i = 1; i <= 4; i++) {
        const stepEl = document.getElementById(`pipelineStep${i}`);
        const statusEl = document.getElementById(`pipelineStatus${i}`);
        stepEl.classList.remove('active', 'completed');
        statusEl.textContent = 'Waiting';
    }

    // Show form sections correctly
    document.querySelectorAll('.form-section').forEach(s => s.classList.remove('active'));
    document.getElementById('step1').classList.add('active');

    // Reset tabs
    switchTab('content');

    showView('form');
}

// ── Utilities ──────────────────────────────────────────────────────

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

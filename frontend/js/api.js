/* ================================================================
   api.js  –  Central API helper (fetch + token injection)
   ================================================================ */

const API_BASE = 'http://localhost:5000/api';

function getToken() { return localStorage.getItem('mm_token'); }

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401 || res.status === 422) {
    localStorage.removeItem('mm_token');
    localStorage.removeItem('mm_user');
    window.location.href = 'index.html';
    return;
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || data.message || 'API error');
  return data;
}

const api = {
  get:    (path)        => apiFetch(path),
  post:   (path, body)  => apiFetch(path, { method:'POST',   body: JSON.stringify(body) }),
  put:    (path, body)  => apiFetch(path, { method:'PUT',    body: JSON.stringify(body) }),
  patch:  (path, body)  => apiFetch(path, { method:'PATCH',  body: JSON.stringify(body || {}) }),
  delete: (path)        => apiFetch(path, { method:'DELETE' }),
};

/* ── Auth guard ─────────────────────────────────────────────────── */
function requireAuth() {
  if (!getToken()) { window.location.href = 'index.html'; }
}

function getUser() {
  try { return JSON.parse(localStorage.getItem('mm_user') || '{}'); }
  catch { return {}; }
}

/* ── Toast notifications ─────────────────────────────────────────── */
function showToast(msg, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success:'✅', error:'❌', info:'ℹ️', warning:'⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type} fade-in`;
  toast.innerHTML = `<span class="toast-icon">${icons[type]||'ℹ️'}</span><span class="toast-msg">${msg}</span>`;
  container.appendChild(toast);
  toast.onclick = () => toast.remove();
  setTimeout(() => toast.remove(), 4000);
}

/* ── Format helpers ──────────────────────────────────────────────── */
function fmtRupees(n) { return '₹' + Number(n).toLocaleString('en-IN', {minimumFractionDigits:2}); }
function fmtDate(d)   { return d ? new Date(d).toLocaleDateString('en-IN') : '—'; }
function todayISO()   { return new Date().toISOString().split('T')[0]; }
function currentMonth() { const d=new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`; }

/* ── Sidebar active link ─────────────────────────────────────────── */
function setActiveNav() {
  const page = location.pathname.split('/').pop();
  document.querySelectorAll('.nav-link').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === page);
  });
}

/* ── Sidebar toggle (mobile) ─────────────────────────────────────── */
function initSidebar() {
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar   = document.querySelector('.sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (!sidebar.contains(e.target) && !toggleBtn.contains(e.target))
        sidebar.classList.remove('open');
    });
  }
}

/* ── Inject user info into sidebar ──────────────────────────────── */
function populateSidebarUser() {
  const user = getUser();
  ['sidebar-username','sidebar-role'].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = id === 'sidebar-username' ? (user.username || 'Admin') : 'Administrator';
    }
  });
  const avatar = document.getElementById('sidebar-avatar');
  if (avatar) avatar.textContent = (user.username || 'A')[0].toUpperCase();

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      localStorage.removeItem('mm_token');
      localStorage.removeItem('mm_user');
      window.location.href = 'index.html';
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  setActiveNav();
  initSidebar();
  populateSidebarUser();
});

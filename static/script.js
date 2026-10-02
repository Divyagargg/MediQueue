let patients = [];

async function load() {
  const [p, s] = await Promise.all([fetch('/api/patients'), fetch('/api/stats')]);
  patients = await p.json();
  updateStats(await s.json());
  renderPatients();
}

function updateStats(s) {
  for (const [id, value] of Object.entries(s)) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }
}

function priorityRank(p) {
  return {Critical:1, High:2, Medium:3, Low:4, Normal:5}[p] || 6;
}

function renderPatients(list = null) {
  let data = list || [...patients];
  const sort = document.getElementById('sort').value;
  if (sort === 'priority') data.sort((a,b) => priorityRank(a.priority)-priorityRank(b.priority));
  if (sort === 'age') data.sort((a,b) => b.age-a.age);
  if (sort === 'name') data.sort((a,b) => a.name.localeCompare(b.name));
  if (sort === 'arrival') data.reverse();

  const rows = document.getElementById('patientRows');
  document.getElementById('empty').style.display = data.length ? 'none' : 'block';
  rows.innerHTML = data.map(p => `
    <tr>
      <td class="id">#${p.id}</td>
      <td><span class="patient-name">${escapeHtml(p.name)}</span><br><small>${p.age} yrs · ${p.gender}</small></td>
      <td>${escapeHtml(p.department)}</td>
      <td><span class="badge ${p.priority}">${p.priority}</span></td>
      <td><span class="badge ${p.status.replace(' ', 'In')}">${p.status}</span></td>
      <td>${p.arrival}</td>
      <td>${p.status !== 'Discharged' ? `<button class="action" onclick="discharge(${p.id})">Discharge</button>` : '—'}</td>
    </tr>`).join('');
}

async function addPatient(e) {
  e.preventDefault();
  const body = {
    name: name.value, age: age.value, gender: gender.value,
    department: department.value, priority: priority.value, symptoms: symptoms.value
  };
  const res = await fetch('/api/patients', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  const data = await res.json();
  if (!res.ok) return toast(data.error || 'Something went wrong');
  e.target.reset();
  formMsg.textContent = `Patient #${data.id} added successfully to the ${data.priority} queue.`;
  toast('Patient registered successfully');
  load();
}

async function callNext() {
  const res = await fetch('/api/next', {method:'POST'});
  const data = await res.json();
  const box = document.getElementById('nextResult');
  if (!res.ok) return toast(data.error);
  box.classList.remove('hidden');
  box.innerHTML = `<b>#${data.id} — ${escapeHtml(data.name)}</b><br>${data.department} · ${data.priority} priority`;
  toast(`Calling ${data.name}`);
  load();
}

async function discharge(id) {
  await fetch(`/api/discharge/${id}`, {method:'POST'});
  toast('Patient marked as discharged');
  load();
}

async function searchPatients() {
  const q = document.getElementById('search').value.trim();
  if (!q) return renderPatients();
  const res = await fetch('/api/search?q=' + encodeURIComponent(q));
  renderPatients(await res.json());
}

function scrollToRegister() {
  document.getElementById('register').scrollIntoView({behavior:'smooth'});
  setTimeout(() => document.getElementById('name').focus(), 500);
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg; t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
}
document.getElementById('patientForm').addEventListener('submit', addPatient);
load();

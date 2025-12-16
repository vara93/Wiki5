const state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user') || 'null'),
  companies: [],
  currentCompany: null,
  currentDc: null,
  tree: null,
  currentObjectId: null,
  currentTab: 'overview',
};

const treeEl = document.getElementById('tree');
const pageEl = document.getElementById('page');
const companyNameEl = document.getElementById('companyName');
const companyMenuList = document.getElementById('companyMenuList');
const switcherMenu = document.getElementById('switcherMenu');
const switcherBtn = document.getElementById('switcherBtn');
const menuClose = document.getElementById('menuClose');
const searchInput = document.getElementById('searchInput');
const userNameEl = document.getElementById('userName');
const userRoleEl = document.getElementById('userRole');
const loginBtn = document.getElementById('loginBtn');
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const editModal = document.getElementById('editModal');
const editArea = document.getElementById('editArea');
const editTarget = document.getElementById('editTarget');
const closeEdit = document.getElementById('closeEdit');
const saveEdit = document.getElementById('saveEdit');
const errorState = { timer: null };

function ensureBanner(){
  let bar = document.getElementById('errorBanner');
  if(!bar){
    bar = document.createElement('div');
    bar.id = 'errorBanner';
    bar.style.cssText = 'position:fixed;top:72px;left:50%;transform:translateX(-50%);z-index:3000;padding:10px 16px;border-radius:16px;background:rgba(255,99,71,0.15);border:1px solid rgba(255,99,71,0.5);color:#fff;backdrop-filter:blur(6px);box-shadow:0 10px 30px rgba(0,0,0,.35);display:none;max-width:90vw;text-align:center;font-weight:800;';
    document.body.appendChild(bar);
  }
  return bar;
}

function showError(msg){
  console.error(msg);
  const bar = ensureBanner();
  bar.textContent = msg;
  bar.style.display = 'block';
  clearTimeout(errorState.timer);
  errorState.timer = setTimeout(()=>bar.style.display='none', 5000);
}

function hideError(){
  const bar = document.getElementById('errorBanner');
  if(bar) bar.style.display = 'none';
  clearTimeout(errorState.timer);
}

function apiHeaders(json=true){
  const h = {};
  if(json) h['Content-Type'] = 'application/json';
  if(state.token) h['Authorization'] = 'Bearer ' + state.token;
  return h;
}

async function fetchJSON(url, opts={}){
  try{
    const res = await fetch(url, opts);
    if(!res.ok) throw new Error(`${res.status} ${await res.text()}`);
    const data = await res.json();
    hideError();
    return data;
  }catch(err){
    showError(`API error: ${url}`);
    throw err;
  }
}

function setUserInfo(){
  if(state.user){
    userNameEl.textContent = state.user.full_name || state.user.username;
    userRoleEl.textContent = state.user.role;
    loginBtn.textContent = 'Выйти';
  } else {
    userNameEl.textContent = 'Гость';
    userRoleEl.textContent = 'viewer';
    loginBtn.textContent = 'Войти';
  }
}

loginBtn.onclick = () => {
  if(state.user){
    state.user = null; state.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUserInfo();
  } else {
    loginModal.classList.add('open');
  }
};

loginForm.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(loginForm);
  try{
    const data = await fetchJSON('/api/auth/login', {method:'POST', body: new URLSearchParams({username: fd.get('username'), password: fd.get('password')})});
    state.token = data.access_token;
    state.user = {username: fd.get('username'), role: data.role, full_name: data.full_name};
    localStorage.setItem('token', state.token);
    localStorage.setItem('user', JSON.stringify(state.user));
    loginModal.classList.remove('open');
    setUserInfo();
  }catch(err){showError('Ошибка входа');}
});

loginModal.addEventListener('click', (e)=>{ if(e.target===loginModal) loginModal.classList.remove('open'); });

function esc(str){return (str||'').replace(/[&<>]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function dot(status){ if(status==='ok') return 'good'; if(status==='warn') return 'warn'; if(status==='bad') return 'bad'; return ''; }

async function loadTree(){
  try{
    const data = await fetchJSON('/api/tree');
    state.tree = data;
    state.companies = data.companies || [];
    state.currentCompany = state.currentCompany || state.companies[0] || null;
    state.currentDc = state.currentCompany?.dcs?.[0] || null;
    renderCompanySwitcher();
    renderTree();
  }catch(err){
    state.tree = {companies: []};
    state.companies = [];
    state.currentCompany = null;
    state.currentDc = null;
    renderCompanySwitcher();
    renderTree();
  }
}

function renderCompanySwitcher(){
  companyNameEl.textContent = state.currentCompany?.name || '—';
  companyMenuList.innerHTML = state.companies.map(c=>`<div class="menuItem ${state.currentCompany && c.id===state.currentCompany.id?'active':''}" data-id="${c.id}"><div class="menuDot"></div><div class="mName">${esc(c.name)}</div><div class="mMeta">DC: ${c.dcs?.[0]?.name||''}</div></div>`).join('');
  companyMenuList.querySelectorAll('.menuItem').forEach(el=>{
    el.onclick=()=>{
      const id=Number(el.dataset.id);
      state.currentCompany = state.companies.find(c=>c.id===id);
      state.currentDc = state.currentCompany?.dcs?.[0] || null;
      closeMenu();
      renderCompanySwitcher();
      renderTree();
      navigate('/');
    }
  });
}

function openMenu(){switcherMenu.classList.add('open');}
function closeMenu(){switcherMenu.classList.remove('open');}

switcherBtn.onclick=()=>{switcherMenu.classList.toggle('open');};
menuClose.onclick=closeMenu;
document.addEventListener('click',(e)=>{ if(!switcherMenu.contains(e.target) && !switcherBtn.contains(e.target)) closeMenu(); });

function renderTree(filter=''){
  const dc = state.currentDc;
  if(!dc){
    treeEl.innerHTML = '<div class="card">Нет данных (ожидаем API)</div>';
    return;
  }
  const f = filter.toLowerCase();
  const filterFn = (n)=>!f || `${n.name} ${n.ip||''}`.toLowerCase().includes(f);
  const renderGroup=(label,icon,key,items)=>{
    const inner = items.filter(filterFn).map(n=>`<div class="node small" data-open="${n.id}"><div class="icon"><div class="dot ${dot(n.status)}"></div></div><div class="label">${esc(n.name)}</div><div class="meta">${esc(n.ip||'')}</div></div>`).join('') || `<div class="node small"><div class="label" style="color:var(--muted)">пусто</div></div>`;
    return `<div class="node small" data-toggle="${key}"><div class="icon">${icon}</div><div class="label">${label}</div><div class="meta">▾</div></div><div class="children open" data-children="${key}">${inner}</div>`;
  };
  treeEl.innerHTML = `<div class="node" data-open="dashboard"><div class="icon">📦</div><div class="label">${esc(dc.name)}</div><div class="meta">DC</div></div><div class="children open">${renderGroup('IT-сервисы','🧩','svc',dc.services)}${renderGroup('Серверы','🖥️','srv',dc.servers)}${renderGroup('Сеть','🌐','net',dc.network)}</div>`;
  treeEl.querySelectorAll('[data-toggle]').forEach(el=>{el.onclick=()=>{const key=el.dataset.toggle;treeEl.querySelector(`[data-children="${key}"]`).classList.toggle('open');};});
  treeEl.querySelectorAll('.node[data-open]').forEach(el=>{el.onclick=()=>{const id=el.dataset.open; if(id==='dashboard'){navigate('/'); return;} navigate(`/object/${id}`);};});
}

  searchInput.addEventListener('input',()=>{renderTree(searchInput.value);});

function markdownToHtml(md){return DOMPurify.sanitize(marked.parse(md||''));}

async function loadObject(id){
  try{
    const data = await fetchJSON(`/api/objects/${id}`);
    state.currentObjectId = id;
    renderObjectPage(data);
  }catch(err){
    pageEl.innerHTML = '<div class="card">Не удалось загрузить объект</div>';
  }
}

function renderTabs(tabs){
  const tabEls = pageEl.querySelectorAll('.tab');
  tabEls.forEach(t=>t.onclick=()=>{const id=t.dataset.tab; state.currentTab=id; tabEls.forEach(x=>x.classList.remove('active')); t.classList.add('active'); pageEl.querySelectorAll('.tabPanel').forEach(p=>p.style.display=p.dataset.panel===id?'block':'none'); history.replaceState({},'',`?tab=${id}`);});
}

function renderObjectPage(detail){
  const obj = detail.object;
  const statusBadge = obj.status==='ok'?{k:'good',t:'🟢 ok'}:obj.status==='warn'?{k:'warn',t:'🟡 warn'}:{k:'bad',t:'🔴 issue'};
  const tabs = ['overview','links','arch','net','inc','docs'];
  const tabHtml = tabs.map(t=>`<div class="tab ${state.currentTab===t?'active':''}" data-tab="${t}">${t}</div>`).join('');
  const panels = tabs.map(t=>{
    const page = detail.pages.find(p=>p.section===t);
    const content = page?markdownToHtml(page.content_md):'<p>Нет данных</p>';
    const editBtn = canEdit()?`<div style="margin-bottom:10px"><button class="btn" data-edit="${page?.id||''}">Редактировать</button></div>`:'';
    if(t==='docs'){
      const docs = detail.documents.map(d=>`<div class="item"><div class="dot ${dot(obj.status)}"></div><div class="name">${esc(d.title)}</div><div class="sub">${d.kind==='file'?d.file_path:d.url||''}</div></div>`).join('');
      return `<div class="tabPanel" data-panel="${t}" style="display:${state.currentTab===t?'block':'none'}">${editBtn}<div class="card"><h3>Документы</h3><div class="list">${docs||'Нет документов'}</div><form id="docForm"><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><input style="flex:1" name="title" placeholder="Название" required /><input style="flex:1" name="url" placeholder="URL" /><select name="kind"><option value="link">Ссылка</option><option value="file">Файл</option></select><input type="file" name="file" /><button class="btn primary" type="submit">Добавить</button></div></form></div>${content}</div>`;
    }
    if(t==='links'){
      const rels = detail.relations.map(r=>`<div class="item" data-open="${r.dst_object_id}"><div class="dot"></div><div class="name">Relation ${r.relation_type}</div><div class="sub">${r.dst_object_id}</div></div>`).join('');
      return `<div class="tabPanel" data-panel="${t}" style="display:${state.currentTab===t?'block':'none'}">${editBtn}<div class="card"><h3>Связи</h3><div class="list">${rels||'Связей нет'}</div></div>${content}</div>`;
    }
    return `<div class="tabPanel" data-panel="${t}" style="display:${state.currentTab===t?'block':'none'}">${editBtn}<div class="card"><div class="markdown">${content}</div></div></div>`;
  }).join('');
  pageEl.innerHTML = `<div class="crumbs"><span>${esc(obj.name)}</span></div><div class="pageHead"><div class="pageTitle"><h1>${esc(obj.name)}</h1><div class="badges"><div class="badge ${statusBadge.k}">${statusBadge.t}</div><div class="badge">${obj.type}</div><div class="badge">${obj.ip||''}</div></div></div><div class="actions"><button class="btn" onclick="navigate('/')">Главная</button></div></div><div class="panel"><div class="tabs">${tabHtml}</div><div class="tabPanels">${panels}</div></div>`;
  renderTabs();
  pageEl.querySelectorAll('[data-edit]').forEach(btn=>{btn.onclick=()=>openEdit(detail.pages.find(p=>p.id==btn.dataset.edit));});
  pageEl.querySelectorAll('.item[data-open]').forEach(el=>{el.onclick=()=>navigate(`/object/${el.dataset.open}`);});
      const docForm = document.getElementById('docForm');
    if(docForm){docForm.onsubmit=async(e)=>{e.preventDefault(); if(!state.token){showError('Нужен логин'); return;} const fd=new FormData(docForm); try{const res=await fetch(`/api/objects/${obj.id}/documents`,{method:'POST',headers: state.token?{'Authorization':'Bearer '+state.token}:undefined,body:fd}); if(!res.ok) throw new Error(); await loadObject(obj.id);}catch(err){showError('Ошибка загрузки документа');}};}
  }

function canEdit(){return state.user && (state.user.role==='admin' || state.user.role==='editor');}

function openEdit(page){if(!page){alert('Страница не найдена'); return;} editTarget.textContent = `Секция: ${page.section}`; editArea.value = page.content_md; editModal.dataset.pageId = page.id; editModal.classList.add('open');}
closeEdit.onclick=()=>editModal.classList.remove('open');
editModal.addEventListener('click',(e)=>{if(e.target===editModal) editModal.classList.remove('open');});
  saveEdit.onclick=async ()=>{
  const id = editModal.dataset.pageId;
  try{
    const res = await fetch(`/api/pages/${id}`,{method:'PUT',headers: apiHeaders(),body: JSON.stringify({content_md: editArea.value})});
    if(!res.ok) throw new Error();
    editModal.classList.remove('open');
    if(state.currentObjectId) await loadObject(state.currentObjectId);
  }catch(err){showError('Не удалось сохранить');}
  };

function renderDashboard(){
  const comp = state.currentCompany || {name:'—', dcs:[{name:'—', services:[], servers:[], network:[]}]} ;
  const dc = state.currentDc || comp.dcs?.[0] || {name:'—', services:[], servers:[], network:[]};
  pageEl.innerHTML = `<div class="crumbs"><span>🏠 Главная</span></div><div class="pageHead"><div class="pageTitle"><h1>${esc(comp.name)}</h1><div class="badges"><div class="badge">ЦОД: ${esc(dc.name)}</div><div class="badge">Объекты: ${(dc.services?.length||0)+(dc.servers?.length||0)+(dc.network?.length||0)}</div></div></div><div class="actions"><button class="btn primary" onclick="navigate('/object/${dc.services?.[0]?.id||''}')">Открыть сервис</button></div></div><div class="grid"><div class="card"><h3>Модель</h3><p>Компания → ЦОД → Объекты. Разделы страниц: обзор, связи, архитектура, сеть, аварии, документы.</p></div><div class="card"><h3>Недавние изменения</h3><p class="pillBadge">Данные из БД</p></div></div>`;
}

function navigate(path){
  history.pushState({},'',path);
  router();
}

window.onpopstate=router;

function router(){
  const url = new URL(location.href);
  const path = url.pathname;
  state.currentTab = url.searchParams.get('tab') || 'overview';
  if(path==='/'){renderDashboard();highlight();return;}
  const m = path.match(/\/object\/(\d+)/);
  if(m){loadObject(m[1]);highlight(m[1]);return;}
  renderDashboard();
}

function highlight(id){
  treeEl.querySelectorAll('.node').forEach(n=>n.classList.remove('active'));
  if(!id){const dcNode=treeEl.querySelector('.node[data-open="dashboard"]'); dcNode?.classList.add('active'); return;}
  const node = treeEl.querySelector(`.node[data-open="${id}"]`);
  if(node){node.classList.add('active'); let p=node.parentElement; while(p && p!==treeEl){if(p.classList.contains('children')) p.classList.add('open'); p=p.parentElement;} node.scrollIntoView({block:'nearest'});} else {renderTree(''); highlight(id);} }

window.addEventListener('error', (event)=>{showError(`Runtime error: ${event.message}`);});
window.addEventListener('unhandledrejection', (event)=>{
  const reason = event.reason?.message || event.reason || 'unknown';
  showError(`Unhandled promise: ${reason}`);
});

window.addEventListener('DOMContentLoaded', async ()=>{
  setUserInfo();
  try{
    await loadTree();
  }catch(err){
    pageEl.innerHTML='<div class="card">Ошибка загрузки API</div>';
  }
  router();
});

window.navigate=navigate;

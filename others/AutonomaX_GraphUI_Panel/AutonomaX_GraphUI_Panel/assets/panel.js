
import { loadJSON, routePrompt } from './router.js';
let endpoints=null, overrides=null, baseURL=null, bearer=null, tenant=null;

async function initConfig(){
  overrides = await loadJSON('./data/overrides.json');
  endpoints = await loadJSON('./data/endpoints.json');
  baseURL = endpoints.base_url.replace(/\/$/,'');
  tenant = endpoints.tenant;
  bearer = (endpoints.auth && endpoints.auth.bearer_token) ? endpoints.auth.bearer_token : "";
}
function authHeaders(){ const h={"Content-Type":"application/json"}; if(bearer) h["Authorization"]="Bearer "+bearer; return h; }
async function apiPost(path, body){
  const r = await fetch(baseURL+path, {method:"POST", headers:authHeaders(), body:JSON.stringify(body)});
  const t = await r.text(); let data=null; try{ data = JSON.parse(t); } catch{ data = {raw:t}; }
  if(!r.ok) throw new Error(JSON.stringify(data)); return data;
}
export async function showPanel(d, graph){
  if(!endpoints) await initConfig();
  const panel = document.getElementById('panel'); panel.innerHTML='';
  const header = elt('div','item'); header.innerHTML = `<h1>${d.label}</h1>`; panel.appendChild(header);
  panel.appendChild(kv('ID', d.id)); panel.appendChild(kv('Type', d.type||'-'));
  if(d.collection) panel.appendChild(kv('Collection', d.collection));
  if(d.channel) panel.appendChild(kv('Channel', d.channel));
  if(Array.isArray(d.tags)&&d.tags.length) panel.appendChild(kv('Tags', d.tags.join(', ')));
  if((d.type||'')==='prompt'){
    const promptObj = { id:d.id, title:d.label, collection:d.collection||'', channel:d.channel||'', tags:d.tags||[] };
    const route = routePrompt(promptObj, overrides);
    const exec = elt('div','item');
    exec.innerHTML = `
      <div class="kv"><b>Suggested Agent</b><span>${(route && (route.agent||route.role)) || 'n/a'}</span></div>
      ${route && route.platform ? `<div class="kv"><b>Platform</b><span>${route.platform}</span></div>` : ''}
      <div style="margin-top:10px"></div>
      <label class="small">Inputs (JSON):</label>
      <textarea id="inputs_json" rows="6">{}</textarea>
      <div class="small" style="margin-top:6px">Examples: <code>data/sample_payloads.json</code></div>
      <div style="display:flex; gap:8px; margin-top:10px;">
        <button id="btnUseProduct" class="secondary">Use Sample Product</button>
        <button id="btnUseKPI" class="secondary">Use Sample KPI</button>
      </div>
      <div style="display:flex; gap:8px; margin-top:10px;">
        <button id="btnCreateProduct">POST /products</button>
        <button id="btnObserve">POST /observe</button>
      </div>
      <div style="display:flex; gap:8px; margin-top:10px;">
        <button id="btnPushShopify">Push → Shopify</button>
        <button id="btnPushEtsy">Push → Etsy</button>
      </div>
      <pre id="exec_out" class="small" style="margin-top:12px; background:#0b1020; padding:8px; border-radius:6px; white-space:pre-wrap"></pre>
    `;
    panel.appendChild(exec);
    const out = exec.querySelector('#exec_out');
    const sample = await loadJSON('./data/sample_payloads.json');
    exec.querySelector('#btnUseProduct').onclick = ()=>{
      const body = Object.assign({}, sample.product_min, {tenant: tenant});
      exec.querySelector('#inputs_json').value = JSON.stringify(body, null, 2);
    };
    exec.querySelector('#btnUseKPI').onclick = ()=>{
      const body = Object.assign({}, sample.observe_kpi, {tenant: tenant});
      exec.querySelector('#inputs_json').value = JSON.stringify(body, null, 2);
    };
    exec.querySelector('#btnCreateProduct').onclick = async ()=>{
      try{ const body = parseJSON(exec.querySelector('#inputs_json').value);
           const data = await apiPost('/products', body);
           out.textContent = 'OK: '+JSON.stringify(data, null, 2);
      }catch(e){ out.textContent = 'ERR: '+e.message; }
    };
    exec.querySelector('#btnObserve').onclick = async ()=>{
      try{ const body = parseJSON(exec.querySelector('#inputs_json').value);
           const data = await apiPost('/observe', body);
           out.textContent = 'OK: '+JSON.stringify(data, null, 2);
      }catch(e){ out.textContent = 'ERR: '+e.message; }
    };
    exec.querySelector('#btnPushShopify').onclick = async ()=>{
      try{ const body = {tenant, shop:endpoints.shopify.shop, access_token:endpoints.shopify.access_token, api_version:endpoints.shopify.api_version};
           const data = await apiPost('/channels/shopify/push', body);
           out.textContent = 'OK: '+JSON.stringify(data, null, 2);
      }catch(e){ out.textContent = 'ERR: '+e.message; }
    };
    exec.querySelector('#btnPushEtsy').onclick = async ()=>{
      try{ const body = {tenant, shop_id:endpoints.etsy.shop_id, access_token:endpoints.etsy.access_token, defaults:endpoints.etsy.defaults, simulate:endpoints.etsy.simulate};
           const data = await apiPost('/channels/etsy/push', body);
           out.textContent = 'OK: '+JSON.stringify(data, null, 2);
      }catch(e){ out.textContent = 'ERR: '+e.message; }
    };
  }
  const footer = elt('footer', null);
  footer.innerHTML = `<div class="small">Configure <code>data/endpoints.json</code>, paste Bearer token, then use buttons above.</div>`;
  panel.appendChild(footer);
}
function elt(tag, cls){ const e = document.createElement(tag); if(cls) e.className=cls; return e; }
function kv(k,v){ const e = elt('div','item kv'); e.innerHTML = `<b>${k}</b><span>${v}</span>`; return e; }
function parseJSON(txt){ try{ return JSON.parse(txt || '{}'); } catch(e){ throw new Error('Invalid JSON'); } }

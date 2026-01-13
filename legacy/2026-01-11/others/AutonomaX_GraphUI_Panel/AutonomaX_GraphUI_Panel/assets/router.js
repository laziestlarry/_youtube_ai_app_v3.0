
export async function loadJSON(path){ const r = await fetch(path); return await r.json(); }
export function matches(rule, p){
  const m = rule.match || {};
  if (m.collection && (p.collection||'').toLowerCase() !== String(m.collection).toLowerCase()) return false;
  if (m.channel && (p.channel||'').toLowerCase() !== String(m.channel).toLowerCase()) return false;
  if (m.tags_any){
    const tags = (p.tags||[]).map(t=>String(t).toLowerCase());
    const need = m.tags_any.map(x=>String(x).toLowerCase());
    if(!need.some(x=>tags.includes(x))) return false;
  }
  if (m.title_regex){
    try{ const re = new RegExp(m.title_regex, 'i'); if(!re.test(p.title||p.label||'')) return false; }
    catch(e){ console.warn('Bad regex in override', m.title_regex); return false; }
  }
  return true;
}
export function routePrompt(p, overrides){
  const rules = overrides.rules || [];
  const order = overrides.priority || [];
  const scored = rules.map(r=>{
    let score = 0; order.forEach((k,i)=>{ if((r.match||{})[k]!==undefined) score += (order.length-i); });
    return {r,score};
  }).sort((a,b)=>b.score-a.score);
  for(const {r} of scored){ if(matches(r,p)) return r.route; }
  return null;
}

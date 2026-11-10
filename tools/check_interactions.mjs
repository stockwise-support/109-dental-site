import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const script = fs.readFileSync(new URL('../js/main.js', import.meta.url), 'utf8');
function classes() {
  const values = new Set();
  return {add:x=>values.add(x),remove:x=>values.delete(x),contains:x=>values.has(x),toggle(x,force){const on=force??!values.has(x);on?values.add(x):values.delete(x);return on;}};
}
const events = {}, toggleEvents = {};
const nav = {classList:classes(),querySelectorAll:()=>[],contains:()=>false};
const toggle = {addEventListener:(key,fn)=>toggleEvents[key]=fn,setAttribute(){},contains:()=>false,focus(){}};
const fields = {"[name='_next']":{},"[name='page']":{}};
const body={classList:classes()};
const document={body,querySelectorAll:()=>[],addEventListener:(key,fn)=>events[key]=fn,querySelector(selector){
  return {'[data-nav]':nav,'[data-nav-toggle]':toggle,'[data-booking-form]':{querySelector:s=>fields[s]},'base[href]':{href:'https://109dental.ca/'}}[selector];
}};
vm.runInNewContext(script,{document,window:{location:new URL('https://109dental.ca/contact/?utm_term=private&reason=private#private')},Date});
assert.equal(fields["[name='page']"].value,'https://109dental.ca/contact/');
assert.equal(fields["[name='_next']"].value,'https://109dental.ca/thank-you/');
toggleEvents.click(); assert(body.classList.contains('nav-open'));
events.keydown({key:'Escape'}); assert(!body.classList.contains('nav-open')); assert(!nav.classList.contains('is-open'));
toggleEvents.click(); events.click({target:{}}); assert(!body.classList.contains('nav-open'));
console.log('PASS: Escape and outside-click restore scrolling; form page field excludes query and fragment.');

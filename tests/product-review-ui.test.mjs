import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import view from '../web/templates/ai_investment_planner.js';
const project=JSON.parse(fs.readFileSync(new URL('../dist/catalog.json',import.meta.url))).projects.find(p=>p.id==='ai_investment_planner');
test('independent review: expanded workflows render actual computed evidence',()=>{
 const html=view.result(project.examples[0].report);
 for(const label of ["Discounted funding alternative", "Evidence-bound funding stages", "Correlated benefit sensitivity and regret"])assert.ok(html.includes(label),label);
});
test('independent review: every scenario renders without mutating evidence',()=>{
 for(const example of project.examples){
  const report=structuredClone(example.report),before=JSON.stringify(report);
  assert.doesNotMatch(view.result(report),/\b(?:undefined|NaN)\b/);
  assert.equal(JSON.stringify(report),before);
 }
});
test('independent review: untrusted labels in expanded output are escaped',()=>{
 const report=structuredClone(project.examples[0].report);
 report.details.discounted_analysis.objective='<script>alert(1)</script>';
 const html=view.result(report);
 assert.doesNotMatch(html,/<script>/);
 assert.ok(html.includes('&lt;script&gt;'));
});

// Exercise only the isolated preview server; no live hardware requests.
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';

const pages = await (await fetch('http://127.0.0.1:9226/json')).json();
const prefix = 'themes-';
const page = pages.find(p => p.type === 'page');
const socket = new WebSocket(page.webSocketDebuggerUrl);
await new Promise(resolve => socket.addEventListener('open', resolve, { once: true }));
let sequence = 0;
const pending = new Map();
const exceptions = [];
socket.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails.text);
  if (message.id && pending.has(message.id)) {
    const item = pending.get(message.id); pending.delete(message.id);
    message.error ? item.reject(message.error) : item.resolve(message.result);
  }
});
function call(method, params = {}) {
  const id = ++sequence;
  return new Promise((resolve, reject) => { pending.set(id, { resolve, reject }); socket.send(JSON.stringify({ id, method, params })); });
}
async function evaluate(expression) {
  const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function until(expression) {
  for (let i = 0; i < 60; i++) {
    if (await evaluate(expression)) return;
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  throw new Error(`Timed out: ${expression}`);
}
async function screenshot(name) {
  const result = await call('Page.captureScreenshot', { format: 'png' });
  await writeFile(new URL(`./${prefix}${name}.png`, import.meta.url), Buffer.from(result.data, 'base64'));
}
async function state(value) {
  await fetch('http://127.0.0.1:8655/test-state', { method: 'POST', body: JSON.stringify(value) });
}
await call('Page.enable');
await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride', { width: 800, height: 480, deviceScaleFactor: 1, mobile: false });
await state({ print_calls: 0, fail_action: false, fail_print: false, offline: false, current_task: null, started_at: null });
await call('Page.navigate', { url: 'http://127.0.0.1:8655/display' });
await until('document.getElementById("connectionState")?.textContent === "STATUS: READY"');
await evaluate('document.fonts.ready');
assert.equal(await evaluate('document.getElementById("connectionState").title.includes("19 BTN")'), true);
assert.equal(await evaluate('document.getElementById("yesBtn").disabled'), true);
assert.equal(await evaluate('document.documentElement.scrollHeight'), 480);
assert.equal(await evaluate('document.querySelector(".logo").naturalWidth > 0'), true);
assert.equal(await evaluate('document.querySelector("h1").textContent'), 'Macrodata Refinement');
assert.equal(await evaluate('document.getElementById("numberField").hidden'), true);
assert.equal(await evaluate('document.getElementById("progressSummary").hidden'), true);
assert.equal(await evaluate('Array.from(document.querySelectorAll("body,button,a,img")).every(e => getComputedStyle(e).cursor === "none")'), true);
const bounds = await evaluate('Array.from(document.querySelectorAll("button")).map(b => ({x:b.getBoundingClientRect().x, y:b.getBoundingClientRect().y, h:b.getBoundingClientRect().height, bottom:b.getBoundingClientRect().bottom}))');
assert(bounds.every(b => b.h >= 55 && b.bottom < 480));
await screenshot('standby');

await evaluate('document.getElementById("newTaskBtn").click(); document.getElementById("newTaskBtn").click();');
await until('document.getElementById("connectionState").textContent === "STATUS: REFINING"');
assert.equal((await (await fetch('http://127.0.0.1:8655/test-state')).json()).print_calls, 1, 'Double tap must request one ticket');
assert.equal(await evaluate('document.getElementById("taskTimer").hidden'), false);
assert.equal(await evaluate('document.getElementById("taskTimer").scrollHeight <= document.getElementById("taskTimer").clientHeight'), true, 'Both timers must fit without scrolling');
assert.equal(await evaluate('document.getElementById("numberField").hidden'), false);
await until('document.getElementById("numberCanvas").width > 300');
assert.equal(await evaluate('document.getElementById("taskDisplay").scrollHeight <= document.getElementById("taskDisplay").clientHeight'), true, 'Assignment text should fit beside the animation');
await screenshot('assignment');

const start = await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at');
await evaluate('document.querySelector(".theme-link").click()');
await until('document.querySelector("h1")?.textContent === "Task Refinement" && document.getElementById("connectionState").textContent === "STATUS: REFINING"');
await evaluate('document.fonts.ready');
assert(Math.abs(await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at') - start) < 1000, 'Switching layouts preserves the session start');
assert.equal(await evaluate('Array.from(document.querySelectorAll("body,button,a,img")).every(e => getComputedStyle(e).cursor === "none")'), true);
assert.equal((await (await fetch('http://127.0.0.1:8655/test-state')).json()).print_calls, 1, 'Switching layouts never prints');
await screenshot('optional-assignment');
await evaluate('document.querySelector(".theme-link").click()');
await until('document.querySelector("h1")?.textContent === "Macrodata Refinement" && document.getElementById("connectionState").textContent === "STATUS: REFINING"');
assert(Math.abs(await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at') - start) < 1000);

const pixels = () => evaluate('document.getElementById("numberCanvas").toDataURL()');
const animated = await pixels();
await new Promise(resolve => setTimeout(resolve, 450));
assert.notEqual(await pixels(), animated, 'Numbers animate during a focus session');
await call('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });
await new Promise(resolve => setTimeout(resolve, 100));
const still = await pixels();
await new Promise(resolve => setTimeout(resolve, 450));
assert.equal(await pixels(), still, 'Reduced motion keeps numbers still');
await call('Emulation.setEmulatedMedia', { features: [] });

await evaluate('window.__testNow = JSON.parse(sessionStorage.getItem("lumon-task")).started_at + 90000; Date.now = () => window.__testNow;');
await until('document.getElementById("sessionProgress").textContent === "10% Elapsed"');
assert.equal(await evaluate('document.getElementById("estimatedTimeDisplay").textContent'), '13:30');
await screenshot('progress');
await evaluate('window.__testNow += 15 * 60000;');
await until('document.getElementById("sessionProgress").textContent === "100% Elapsed"');
assert.equal(await evaluate('document.getElementById("estimatedTimeDisplay").textContent'), '00:00');
const finished = await pixels();
await new Promise(resolve => setTimeout(resolve, 450));
assert.equal(await pixels(), finished, 'Animation pauses when the timer expires');
assert.equal(await evaluate('document.getElementById("yesBtn").disabled'), false, 'Elapsed timer never auto-completes a task');

await state({ fail_action: true });
await evaluate('document.getElementById("yesBtn").click()');
await until('document.getElementById("taskDescription").textContent.includes("update could not be confirmed")');
assert.equal(await evaluate('document.getElementById("yesBtn").disabled'), false, 'Failed completion must remain retryable');
assert.equal(await evaluate('document.getElementById("taskTimer").hidden'), false);
await evaluate('document.getElementById("noBtn").click()');
await until('document.getElementById("connectionState").textContent === "STATUS: REFINING"');
assert.equal(await evaluate('document.getElementById("noBtn").disabled'), false);

await state({ fail_action: false });
await evaluate('document.getElementById("yesBtn").click()');
await until('document.getElementById("taskTitle").textContent === "Refinement recorded"');
assert.equal(await evaluate('document.getElementById("taskTimer").hidden'), true);
assert.equal(await evaluate('document.getElementById("yesBtn").disabled'), true);
assert.equal(await evaluate('document.getElementById("sessionProgress").textContent'), 'Awaiting task');
assert.equal(await evaluate('document.getElementById("numberField").hidden'), true);
assert.equal(await evaluate('document.getElementById("progressSummary").hidden'), true);
await state({ fail_print: true });
await evaluate('document.getElementById("newTaskBtn").click()');
await until('document.getElementById("taskDescription").textContent.includes("No eligible task")');
assert.equal(await evaluate('document.getElementById("newTaskBtn").disabled'), false);
assert.equal(await evaluate('document.getElementById("connectionState").textContent'), 'STATUS: READY');

await state({ fail_print: 503 });
await evaluate('document.getElementById("newTaskBtn").click()');
await until('document.getElementById("taskDescription").textContent.includes("Trello is unavailable. No ticket was printed.")');

await state({ offline: true });
await call('Page.reload');
await until('document.getElementById("connectionState")?.textContent === "STATUS: OFFLINE"');
assert.equal(await evaluate('document.getElementById("connectionState").title.includes("19 BTN")'), false);
await screenshot('offline');
assert.deepEqual(exceptions, [], 'No browser exceptions');
const report = { version: 'Classic default, optional MDR', viewport: '800x480', touch_target_height: 55, cursor_hidden_in_both_layouts: true, layout_switch_preserves_task_and_timer_without_printing: true, double_tap_print_calls: 1, elapsed_progress_tracks_focus_timer: true, numbers_animate_during_focus: true, animation_pauses_at_timer_end_and_for_reduced_motion: true, elapsed_timer_does_not_auto_complete: true, failed_complete_and_skip_keep_assignment: true, success_completion: true, no_suitable_task_distinct_from_offline: true, api_outage_does_not_claim_ticket_printed: true, offline_clears_counts: true, browser_exceptions: exceptions };
await writeFile(new URL('./themes-ui-check.json', import.meta.url), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report));
socket.close();

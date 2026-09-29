// Test the picker only against synthetic tasks; never use the live printer.
import assert from 'node:assert/strict';
import { writeFile } from 'node:fs/promises';

const pages = await (await fetch('http://127.0.0.1:9226/json')).json();
const socket = new WebSocket(pages.find(page => page.type === 'page').webSocketDebuggerUrl);
await new Promise(resolve => socket.addEventListener('open', resolve, { once: true }));
let sequence = 0;
const pending = new Map();
const exceptions = [];
socket.addEventListener('message', event => {
  const message = JSON.parse(event.data);
  if (message.method === 'Runtime.exceptionThrown') exceptions.push(message.params.exceptionDetails.text);
  if (pending.has(message.id)) {
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
  await writeFile(new URL(`./manage-${name}.png`, import.meta.url), Buffer.from(result.data, 'base64'));
}
async function state(value) {
  return (await fetch('http://127.0.0.1:8655/test-state', { method: 'POST', body: JSON.stringify(value) })).json();
}
const click = id => evaluate(`document.getElementById('${id}').click()`);
await call('Page.enable');
await call('Runtime.enable');
await call('Emulation.setDeviceMetricsOverride', { width: 800, height: 480, deviceScaleFactor: 1, mobile: false });
for (const theme of ['classic', 'mdr']) {
  await state({ print_calls: 0, fail_action: false, fail_print: false, offline: false, current_task: null,
    started_at: null, fail_tasks: false, empty_tasks: false, list_calls: 0, last_print_body: null });
  await call('Page.navigate', { url: `http://127.0.0.1:8655/display?theme=${theme}` });
  await until('document.getElementById("connectionState")?.textContent === "STATUS: READY"');
  await evaluate('document.fonts.ready');
  assert.equal(await evaluate('document.getElementById("manageBtn").hidden'), false);
  assert.equal(await evaluate('document.getElementById("yesBtn").hidden && document.getElementById("noBtn").hidden'), true);
  await screenshot(`${theme}-home`);
  await click('manageBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: BROWSING"');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 9);
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '1/2 · 15 TASKS');
  assert.equal(await evaluate('document.getElementById("pickerPrevious").disabled'), true);
  const bounds = await evaluate(`Array.from(document.querySelectorAll('.task-card')).map(b => {
    const r=b.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,scroll:b.scrollWidth,client:b.clientWidth}; })`);
  assert.equal(new Set(bounds.map(b => b.x)).size, 3);
  assert.equal(new Set(bounds.map(b => b.y)).size, 3);
  assert(bounds.every(b => b.h >= 55 && b.x >= 0 && b.right <= 800 && b.bottom < 390 && b.scroll === b.client));
  assert.equal(await evaluate('document.documentElement.scrollHeight'), 480);
  assert.equal(await evaluate('Array.from(document.querySelectorAll("button")).every(b => getComputedStyle(b).cursor === "none")'), true);
  await screenshot(`${theme}-grid`);
  await click('pickerNext');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 6);
  assert.equal(await evaluate('document.getElementById("pickerNext").disabled'), true);
  assert.equal(await evaluate('document.querySelectorAll(".task-card img").length'), 0, 'Card titles are text, never HTML');
  await screenshot(`${theme}-page2`);
  assert.equal((await state({})).print_calls, 0, 'Browsing and pagination cannot print');
  await evaluate('document.querySelectorAll(".task-card")[5].click()');
  assert.equal(await evaluate('document.getElementById("taskTitle").textContent'), 'A_very_long_unbroken_task_title_that_must_wrap_without_expanding_the_card');
  assert.equal((await state({})).print_calls, 0, 'Inspecting a card cannot print');
  await click('pickerBack');
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '2/2 · 15 TASKS', 'Back preserves the browsing page');
  await evaluate('document.querySelector(".task-card").click()');
  await screenshot(`${theme}-detail`);
  await evaluate('document.getElementById("pickerStart").click();document.getElementById("pickerStart").click()');
  await until('document.getElementById("connectionState").textContent === "STATUS: REFINING"');
  let after = await state({});
  assert.equal(after.print_calls, 1, 'Double tap prints only one selected ticket');
  assert.deepEqual(after.last_print_body, { task_id: 'manual-9' });
  assert.equal(await evaluate('document.getElementById("taskTitle").textContent'), 'Check the printer paper');
  assert.equal(await evaluate('document.getElementById("manageBtn").hidden'), true);
  assert.equal(await evaluate('!document.getElementById("yesBtn").hidden && !document.getElementById("taskTimer").hidden'), true);
  const start = await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at');
  await call('Page.reload');
  await until('document.getElementById("connectionState")?.textContent === "STATUS: REFINING"');
  assert(Math.abs(await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at') - start) < 1000);
  assert.equal((await state({})).print_calls, 1, 'Restoring a manual assignment never reprints');
  await click('yesBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: READY"');
  await state({ fail_tasks: true });
  await click('manageBtn');
  await until('!document.getElementById("pickerRetry").disabled');
  assert.equal(await evaluate('document.getElementById("pickerNotice").textContent.includes("Unable to load tasks")'), true);
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 0);
  await screenshot(`${theme}-offline`);
  await state({ fail_tasks: false, empty_tasks: true });
  await click('pickerRetry');
  await until('document.getElementById("pickerNotice").textContent.includes("No open tasks")');
  assert.equal(await evaluate('document.getElementById("pickerRetry").textContent'), 'REFRESH');
  await state({ empty_tasks: false });
  await click('pickerRetry');
  await until('document.querySelectorAll(".task-card").length === 9');
  await evaluate('document.querySelector(".task-card").click()');
  await state({ fail_print: true });
  await click('pickerStart');
  await until('document.getElementById("pickerNotice").textContent.includes("no longer available")');
  assert.equal(await evaluate('document.getElementById("pickerStart").hidden'), true);
  assert.equal((await state({})).current_task, null);
  await state({ fail_print: false });
  await click('pickerRetry');
  await until('document.querySelectorAll(".task-card").length === 9');
  await evaluate('document.querySelector(".task-card").click()');
  await state({ fail_print: 503 });
  await click('pickerStart');
  await until('document.getElementById("taskDescription").textContent.includes("No ticket was printed")');
  assert.equal(await evaluate('document.getElementById("pickerStart").disabled'), false, 'Manual failure remains retryable');
  await state({ fail_print: false });
  await click('pickerBack');
  await click('pickerBack');
  await click('newTaskBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: REFINING"');
  assert.deepEqual((await state({})).last_print_body, {}, 'New Task still uses automatic selection');
}
assert.deepEqual(exceptions, []);
const report = { viewport: '800x480', themes: ['classic', 'mdr'], grid: '3x3',
  browsing_never_prints: true, full_title_before_printing: true, double_tap_protected: true,
  manual_restore_preserves_timer: true, empty_offline_stale_and_retry_checked: true,
  titles_are_plain_text: true, automatic_selection_preserved: true, browser_exceptions: exceptions };
await writeFile(new URL('./manage-ui-check.json', import.meta.url), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
socket.close();

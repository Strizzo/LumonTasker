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
    started_at: null, fail_tasks: false, empty_tasks: false, list_calls: 0, last_print_body: null, task_filter: null, focus_minutes: 15 });
  await call('Page.navigate', { url: `http://127.0.0.1:8655/display?theme=${theme}` });
  await until('document.getElementById("connectionState")?.textContent === "STATUS: READY"');
  await evaluate('document.fonts.ready');
  assert.equal(await evaluate('document.getElementById("manageBtn").hidden'), false);
  assert.equal(await evaluate('document.getElementById("yesBtn").hidden && document.getElementById("noBtn").hidden'), true);
  await screenshot(`${theme}-home`);
  await click('manageBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: BROWSING"');
  assert.equal(await evaluate('document.querySelector(".masthead").getBoundingClientRect().height'), 0, 'Browsing hides the logo and station header');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 9);
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '1/2 · 12 CARDS');
  assert.equal(await evaluate('document.getElementById("pickerTotal").textContent'), 'TOTAL FOCUS: 2h 45m', 'All 11 regular tasks, including DOING and the next page, count; the 19 BTN tasks do not');
  assert.equal(await evaluate('document.getElementById("pickerTotal").hidden'), false);
  assert.equal(await evaluate('document.getElementById("pickerPrevious").disabled'), true);
  const bounds = await evaluate(`Array.from(document.querySelectorAll('.task-card')).map(b => {
    const r=b.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,scroll:b.scrollWidth,client:b.clientWidth}; })`);
  assert.equal(new Set(bounds.map(b => b.x)).size, 3);
  assert.equal(new Set(bounds.map(b => b.y)).size, 3);
  assert(bounds.every(b => b.h >= 75 && b.x >= 0 && b.right <= 800 && b.bottom < 390 && b.scroll === b.client), 'The reclaimed header space increases every card to at least 75px');
  assert.equal(await evaluate('document.documentElement.scrollHeight'), 480);
  assert.equal(await evaluate('Array.from(document.querySelectorAll("button")).every(b => getComputedStyle(b).cursor === "none")'), true);
  await screenshot(`${theme}-grid`);
  await click('pickerNext');
  assert.equal(await evaluate('document.getElementById("pickerTotal").textContent'), 'TOTAL FOCUS: 2h 45m', 'Changing page preserves the full-queue total');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 3);
  assert.equal(await evaluate('document.getElementById("pickerNext").disabled'), true);
  assert.equal(await evaluate('document.querySelectorAll("[data-group=BTN]").length'), 1);
  assert.equal(await evaluate('document.querySelector("[data-group=BTN] .task-card-source").textContent'), '19 TASKS →');
  await screenshot(`${theme}-page2`);
  await evaluate('document.querySelector("[data-group=BTN]").click()');
  assert.equal(await evaluate('document.getElementById("pickerHeading").textContent'), 'Better Than Nothing');
  assert.equal(await evaluate('document.querySelector(".masthead").getBoundingClientRect().height'), 0, 'The nested grid also uses the extra space');
  assert.equal(await evaluate('document.getElementById("pickerTotal").hidden'), true);
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '1/3 · 19 TASKS');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 9);
  assert.equal(await evaluate('document.getElementById("pickerStart").hidden'), true, 'A group is not a printable task');
  assert.equal(await evaluate('document.querySelectorAll(".task-card img").length'), 0, 'Card titles are text, never HTML');
  await screenshot(`${theme}-btn-grid`);
  await click('pickerNext');
  await click('pickerNext');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 1);
  assert.equal(await evaluate('document.getElementById("pickerNext").disabled'), true);
  await click('pickerPrevious');
  await evaluate('document.querySelector(".task-card").click()');
  await click('pickerBack');
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '2/3 · 19 TASKS', 'Detail returns to the same nested page');
  await click('pickerPrevious');
  assert.equal((await state({})).print_calls, 0, 'Browsing and pagination cannot print');
  assert.equal((await state({})).list_calls, 1, 'Opening the group needs no extra request');
  await evaluate('document.querySelectorAll(".task-card")[3].click()');
  assert.equal(await evaluate('document.querySelector(".masthead").getBoundingClientRect().height > 0'), true, 'Header returns for task details');
  assert.equal(await evaluate('document.getElementById("taskTitle").textContent'), 'A_very_long_unbroken_task_title_that_must_wrap_without_expanding_the_card');
  assert.equal((await state({})).print_calls, 0, 'Inspecting a card cannot print');
  await click('pickerBack');
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '1/3 · 19 TASKS');
  await click('pickerBack');
  assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '2/2 · 12 CARDS', 'Back restores the parent page');
  assert.equal(await evaluate('document.getElementById("pickerTotal").textContent'), 'TOTAL FOCUS: 2h 45m');
  await evaluate('document.querySelector("[data-group=BTN]").click()');
  await evaluate('document.querySelector(".task-card").click()');
  await screenshot(`${theme}-detail`);
  await evaluate('document.getElementById("pickerStart").click();document.getElementById("pickerStart").click()');
  await until('document.getElementById("connectionState").textContent === "STATUS: REFINING"');
  let after = await state({});
  assert.equal(after.print_calls, 1, 'Double tap prints only one selected ticket');
  assert.deepEqual(after.last_print_body, { task_id: 'manual-11' });
  assert.equal(after.current_task.source_list, 'BTN', 'Nested selection retains reusable-task semantics');
  assert.equal(await evaluate('document.getElementById("taskTitle").textContent'), 'Clean the kitchen');
  assert.equal(await evaluate('document.getElementById("manageBtn").hidden'), true);
  assert.equal(await evaluate('!document.getElementById("yesBtn").hidden && !document.getElementById("noBtn").hidden'), true);
  assert.equal(await evaluate('document.getElementById("taskTimer")'), null);
  assert.equal(await evaluate('document.getElementById("sessionProgress")'), null);
  assert.equal(await evaluate('document.getElementById("taskDescription").textContent'), 'One task at a time.');
  await screenshot(`${theme}-active`);
  const start = await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at');
  await call('Page.reload');
  await until('document.getElementById("connectionState")?.textContent === "STATUS: REFINING"');
  assert(Math.abs(await evaluate('JSON.parse(sessionStorage.getItem("lumon-task")).started_at') - start) < 1000);
  assert.equal((await state({})).print_calls, 1, 'Restoring a manual assignment never reprints');
  assert.equal(await evaluate('document.getElementById("taskDescription").textContent'), 'One task at a time.', 'Saved focus boilerplate stays hidden after reload');
  await click('yesBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: READY"');
  await state({ fail_tasks: true });
  await click('manageBtn');
  await until('!document.getElementById("pickerRetry").disabled');
  assert.equal(await evaluate('document.getElementById("pickerNotice").textContent.includes("Unable to load tasks")'), true);
  assert.equal(await evaluate('document.getElementById("pickerTotal").hidden'), true, 'Offline must not show a stale or zero total');
  assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), 0);
  await screenshot(`${theme}-offline`);
  await state({ fail_tasks: false, empty_tasks: true });
  await click('pickerRetry');
  await until('document.getElementById("pickerNotice").textContent.includes("No open tasks")');
  assert.equal(await evaluate('document.getElementById("pickerRetry").textContent'), 'REFRESH');
  assert.equal(await evaluate('document.getElementById("pickerTotal").textContent'), 'TOTAL FOCUS: 0m');
  await state({ empty_tasks: false });
  await click('pickerRetry');
  await until('document.querySelectorAll(".task-card").length === 9');
  await evaluate('document.querySelector(".task-card").click()');
  await state({ fail_print: true });
  await click('pickerStart');
  await until('document.getElementById("pickerNotice").textContent.includes("no longer available")');
  assert.equal(await evaluate('document.getElementById("pickerTotal").hidden'), true, 'Stale-card error hides the old total');
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
  for (const filter of ['btn_only', 'without_btn', 'single_todo']) {
    await state({ task_filter: filter });
    await click('manageBtn');
    await until('document.getElementById("connectionState").textContent === "STATUS: BROWSING"');
    assert.equal(await evaluate('document.getElementById("pickerTotal").textContent'), filter === 'btn_only' ? 'TOTAL FOCUS: 0m' : filter === 'single_todo' ? 'TOTAL FOCUS: 15m' : 'TOTAL FOCUS: 2h 45m');
    if (filter === 'without_btn') {
      await click('pickerNext');
      assert.equal(await evaluate('document.querySelectorAll("[data-group=BTN]").length'), 0);
      assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '2/2 · 11 CARDS');
    } else {
      assert.equal(await evaluate('document.querySelectorAll(".task-card").length'), filter === 'btn_only' ? 1 : 2);
      assert.equal(await evaluate('document.querySelectorAll("[data-group=BTN]").length'), 1);
      if (filter === 'single_todo') await screenshot(`${theme}-grouped-main`);
      await evaluate('document.querySelector("[data-group=BTN]").click()');
      assert.equal(await evaluate('document.getElementById("pickerPage").textContent'), '1/3 · 19 TASKS');
      await click('pickerBack');
    }
    await click('pickerBack');
  }
  await state({ task_filter: null });
  await state({ focus_minutes: 30 });
  await click('manageBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: BROWSING"');
  assert.equal(await evaluate('document.getElementById("pickerTotal").textContent'), 'TOTAL FOCUS: 5h 30m', 'Use configured duration, not hard-coded 15');
  await click('pickerBack');
  await state({ focus_minutes: null });
  await click('manageBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: BROWSING"');
  assert.equal(await evaluate('document.getElementById("pickerTotal").hidden'), true, 'Missing duration must not invent an estimate');
  await click('pickerBack');
  await state({ focus_minutes: 15 });
  await click('newTaskBtn');
  await until('document.getElementById("connectionState").textContent === "STATUS: REFINING"');
  assert.deepEqual((await state({})).last_print_body, {}, 'New Task still uses automatic selection');
}
assert.deepEqual(exceptions, []);
const report = { viewport: '800x480', themes: ['classic', 'mdr'], grid: '3x3',
  btn_group_is_one_card: true, nested_pagination_and_back_restore_parent: true,
  total_focus_includes_all_regular_pages_excludes_btn: true, total_uses_server_duration: true,
  total_hidden_in_nested_grid_and_on_errors: true,
  only_btn_no_btn_and_single_todo_checked: true, nested_selection_retains_btn_source: true,
  browsing_never_prints: true, full_title_before_printing: true, double_tap_protected: true,
  manual_restore_preserves_assignment: true, empty_offline_stale_and_retry_checked: true,
  task_screen_has_no_fixed_focus_countdown_or_progress: true, grid_header_hidden_and_cards_at_least_75px: true,
  titles_are_plain_text: true, automatic_selection_preserved: true, browser_exceptions: exceptions };
await writeFile(new URL('./manage-ui-check.json', import.meta.url), JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
socket.close();

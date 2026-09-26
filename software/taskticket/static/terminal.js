'use strict';
(() => {
  const el = id => document.getElementById(id);
  const buttons = [el('newTaskBtn'), el('yesBtn'), el('noBtn')];
  let currentTask = null;
  let busy = false;
  let timer = null;
  let startedAt = 0;
  let estimatedSeconds = 0;
  let challengeSeconds = 0;
  let online = null;
  let timezone = 'Europe/Luxembourg';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const numberCanvas = el('numberCanvas');
  const numberContext = numberCanvas.getContext('2d');
  let numberInterval = null;
  let numberSeed = '';
  let numberCells = [];
  let numberTime = 0;

  function saveSession() {
    try {
      if (currentTask) sessionStorage.setItem('lumon-task', JSON.stringify({ task: currentTask, started_at: startedAt }));
      else sessionStorage.removeItem('lumon-task');
    } catch (_) { /* The server can also restore the current assignment. */ }
  }

  function drawNumbers() {
    if (!numberContext || el('numberField').hidden) return;
    const width = numberCanvas.clientWidth;
    const height = numberCanvas.clientHeight;
    if (!width || !height) return;
    const scale = Math.min(window.devicePixelRatio || 1, 1.5);
    if (numberCanvas.width !== Math.round(width * scale) || numberCanvas.height !== Math.round(height * scale)) {
      numberCanvas.width = Math.round(width * scale);
      numberCanvas.height = Math.round(height * scale);
    }
    const columns = Math.max(6, Math.floor(width / 33));
    const rows = 3;
    if (numberCells.length !== columns * rows) {
      let seed = 1;
      for (const character of numberSeed) seed = (seed * 31 + character.charCodeAt(0)) >>> 0;
      const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
      numberCells = Array.from({ length: columns * rows }, () => ({ digit: Math.floor(random() * 10), phase: random() * Math.PI * 2 }));
    }
    const style = getComputedStyle(document.body);
    const moving = !reducedMotion.matches && estimatedSeconds > 0 && Date.now() - startedAt < estimatedSeconds * 1000;
    if (moving) numberTime = performance.now() / 6000;
    numberContext.setTransform(scale, 0, 0, scale, 0, 0);
    numberContext.clearRect(0, 0, width, height);
    numberContext.fillStyle = style.getPropertyValue('--ink').trim();
    numberContext.textAlign = 'center';
    numberContext.textBaseline = 'middle';
    numberCells.forEach((cell, index) => {
      const phase = reducedMotion.matches ? 0 : numberTime + cell.phase;
      const highlighted = index % 23 < 3;
      const drift = reducedMotion.matches ? 0 : Math.sin(phase) * 1.8;
      numberContext.globalAlpha = highlighted ? .72 : .3 + Math.sin(phase) * .08;
      numberContext.font = `${highlighted ? 17 : 14}px ${style.fontFamily}`;
      numberContext.fillText(String(cell.digit), (index % columns + .5) * width / columns + drift, (Math.floor(index / columns) + .5) * height / rows + drift);
    });
    numberContext.globalAlpha = 1;
  }

  function pauseNumbers() {
    if (numberInterval !== null) clearInterval(numberInterval);
    numberInterval = null;
  }

  function resumeNumbers() {
    pauseNumbers();
    if (!currentTask || el('numberField').hidden) return;
    drawNumbers();
    if (!reducedMotion.matches && !document.hidden && Date.now() - startedAt < estimatedSeconds * 1000) {
      numberInterval = setInterval(drawNumbers, 150);
    }
  }

  function updateControls() {
    buttons[0].disabled = busy;
    buttons[1].disabled = busy || currentTask === null;
    buttons[2].disabled = busy || currentTask === null;
    document.querySelector('.theme-link').setAttribute('aria-disabled', String(busy));
    el('connectionState').textContent = 'STATUS: ' + (busy ? 'WORKING' : online === false ? 'OFFLINE' : online === null ? 'CHECKING' : currentTask ? 'REFINING' : 'READY');
    el('connectionState').classList.toggle('unavailable', online === false);
  }

  function render(title, description) {
    el('taskTitle').textContent = title;
    el('taskDescription').textContent = description;
    el('taskDisplay').scrollTop = 0;
  }

  function stopTimer() {
    if (timer !== null) clearInterval(timer);
    timer = null;
    el('taskTimer').hidden = true;
    if (el('progressSummary')) el('progressSummary').hidden = true;
    pauseNumbers();
    el('numberField').hidden = true;
    el('sessionProgress').textContent = 'Awaiting task';
    el('focusProgress').style.width = '0%';
    document.body.classList.remove('time-warning', 'time-danger');
  }

  function formatTime(seconds) {
    const value = Math.max(0, Math.ceil(seconds));
    return `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(value % 60).padStart(2, '0')}`;
  }

  function updateTimer() {
    const elapsed = (Date.now() - startedAt) / 1000;
    const percent = Math.min(100, Math.max(0, Math.floor(elapsed / estimatedSeconds * 100)));
    el('sessionProgress').textContent = `${percent}% Elapsed`;
    el('focusProgress').style.width = `${percent}%`;
    el('estimatedTimeDisplay').textContent = formatTime(estimatedSeconds - elapsed);
    el('challengeTimeDisplay').textContent = formatTime(challengeSeconds - elapsed);
    document.body.classList.toggle('time-warning', elapsed >= estimatedSeconds);
    document.body.classList.toggle('time-danger', challengeSeconds > 0 && elapsed >= challengeSeconds);
    if (percent >= 100) pauseNumbers();
  }

  function showTask(task, start = Date.now()) {
    const estimate = Number.parseFloat(task.estimated_time);
    const challenge = Number.parseFloat(task.challenge_time);
    estimatedSeconds = Number.isFinite(estimate) && estimate > 0 ? estimate * 60 : 15 * 60;
    challengeSeconds = Number.isFinite(challenge) && challenge > 0 ? challenge * 60 : 0;
    render(task.ticket_title || task.title || 'Your assignment', task.motivation || 'Please proceed with your important work.');
    el('taskTimer').hidden = false;
    if (el('progressSummary')) el('progressSummary').hidden = false;
    el('challengeRow').hidden = challengeSeconds === 0;
    startedAt = Number.isFinite(start) ? Math.min(start, Date.now()) : Date.now();
    saveSession();
    updateTimer();
    timer = setInterval(updateTimer, 1000);
    numberSeed = task.task_id || task.ticket_title || '';
    numberCells = [];
    numberTime = 0;
    el('numberField').hidden = false;
    resumeNumbers();
  }

  async function request(path, body) {
    // Do not abort print requests: a timed-out request could still print and
    // retrying it would risk issuing a second physical ticket.
    const response = await fetch(path, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    });
    const result = await response.json();
    if (!response.ok || !result.success) {
      const error = new Error(result.message || 'The mainframe could not process this request.');
      error.status = response.status;
      throw error;
    }
    return result;
  }

  async function newTask() {
    if (busy) return;
    const previousTask = currentTask;
    busy = true;
    updateControls();
    render('Retrieving assignment', 'Please wait. Your ticket will print when ready.');
    try {
      const result = await request('/print_task');
      stopTimer();
      currentTask = result.task;
      showTask(currentTask);
    } catch (error) {
      currentTask = previousTask;
      render('System notice', error.status === 404 ? 'No eligible task is available. Try again later.' : error.status === 503 ? 'Trello is unavailable. No ticket was printed.' : 'Unable to retrieve an assignment. Check the connection before retrying; a ticket may already have printed.');
    } finally {
      busy = false;
      updateControls();
      refreshStatus();
    }
  }

  async function finishTask(action) {
    if (busy || !currentTask) return;
    busy = true;
    updateControls();
    try {
      await request(action === 'complete' ? '/complete_task' : '/skip_task', {
        task_id: currentTask.task_id, source_list: currentTask.source_list
      });
      stopTimer();
      currentTask = null;
      saveSession();
      if (action === 'complete') {
        render('Refinement recorded', 'Your assignment has been completed.\nThank you for your service to Lumon.');
      } else {
        render('Assignment deferred', 'This task will be held for seven days.\nSelect New Task to continue your work.');
      }
    } catch (error) {
      // Keep the current task and timer so failed actions can be retried.
      render('System notice', 'The assignment remains open here. Its update could not be confirmed; check Trello before retrying.');
    } finally {
      busy = false;
      updateControls();
      refreshStatus();
    }
  }

  async function refreshStatus() {
    const connection = el('connectionState');
    try {
      const response = await fetch('/terminal_status', { cache: 'no-store' });
      if (!response.ok) throw new Error('Status unavailable');
      const status = await response.json();
      if (status.timezone) timezone = status.timezone;
      online = status.ok === true;
      connection.title = online ? `Trello online: ${status.counts.todo} TODO, ${status.counts.doing} DOING, ${status.counts.btn} BTN` : 'Trello unavailable';
    } catch (error) {
      online = false;
      connection.title = 'Connection status unavailable';
    }
    updateControls();
  }

  function updateClock() {
    const now = new Date();
    el('dateTime').textContent = now.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: timezone }) + '  ' + now.toLocaleTimeString('en-GB', { timeZone: timezone });
    el('dateTime').dateTime = now.toISOString();
  }

  async function restoreTask() {
    busy = true;
    updateControls();
    try {
      const response = await fetch('/current_task', { cache: 'no-store' });
      if (!response.ok) throw new Error('Assignment restore unavailable');
      const session = await response.json();
      if (session.task) {
        currentTask = session.task;
        showTask(currentTask, Number(session.started_at));
      } else {
        currentTask = null;
        saveSession();
      }
    } catch (_) {
      try {
        const session = JSON.parse(sessionStorage.getItem('lumon-task') || 'null');
        if (session?.task && Date.now() - session.started_at < 12 * 60 * 60 * 1000) {
          currentTask = session.task;
          showTask(currentTask, Number(session.started_at));
        }
      } catch (_) { /* Keep the welcome screen if no saved assignment exists. */ }
    } finally {
      busy = false;
      updateControls();
    }
  }

  buttons[0].addEventListener('click', newTask);
  buttons[1].addEventListener('click', () => finishTask('complete'));
  buttons[2].addEventListener('click', () => finishTask('skip'));
  document.querySelector('.theme-link').addEventListener('click', event => {
    if (busy) event.preventDefault();
  });
  document.addEventListener('keydown', event => {
    if (event.repeat || event.ctrlKey || event.metaKey || event.altKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    const index = { n: 0, c: 1, s: 2, y: 1, x: 2 }[event.key.toLowerCase()];
    if (index !== undefined) { event.preventDefault(); buttons[index].click(); }
  });
  document.addEventListener('visibilitychange', () => document.hidden ? pauseNumbers() : resumeNumbers());
  reducedMotion.addEventListener('change', resumeNumbers);
  window.addEventListener('resize', drawNumbers);
  updateClock();
  updateControls();
  refreshStatus();
  restoreTask();
  setInterval(updateClock, 1000);
  setInterval(refreshStatus, 60000);
})();

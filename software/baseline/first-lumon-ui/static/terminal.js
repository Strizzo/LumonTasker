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
  let completed = 0;
  let timezone = 'Europe/Luxembourg';

  function updateControls() {
    buttons[0].disabled = busy;
    buttons[1].disabled = busy || currentTask === null;
    buttons[2].disabled = busy || currentTask === null;
    el('systemStatus').textContent = busy ? 'PROCESSING' : currentTask ? 'REFINING' : 'STANDBY';
  }

  function render(title, description, eyebrow = 'REFINEMENT DESK') {
    el('taskTitle').textContent = title;
    el('taskDescription').textContent = description;
    el('taskEyebrow').textContent = eyebrow;
    el('taskPrompt').firstChild.textContent = currentTask ? '> REFINEMENT IN PROGRESS' : '> AWAITING REFINEMENT';
    el('taskDisplay').scrollTop = 0;
  }

  function stopTimer() {
    if (timer !== null) clearInterval(timer);
    timer = null;
    el('taskTimer').hidden = true;
    document.body.classList.remove('time-warning', 'time-danger');
  }

  function formatTime(seconds) {
    const value = Math.max(0, Math.ceil(seconds));
    return `${String(Math.floor(value / 60)).padStart(2, '0')}:${String(value % 60).padStart(2, '0')}`;
  }

  function updateTimer() {
    const elapsed = (Date.now() - startedAt) / 1000;
    const percent = Math.min(100, Math.floor(elapsed / estimatedSeconds * 100));
    el('estimatedTimeDisplay').textContent = formatTime(estimatedSeconds - elapsed);
    el('timeProgress').style.width = `${percent}%`;
    el('timerCaption').textContent = `${percent}% ELAPSED`;
    el('challengeTimeDisplay').textContent = formatTime(challengeSeconds - elapsed);
    document.body.classList.toggle('time-warning', elapsed >= estimatedSeconds);
    document.body.classList.toggle('time-danger', challengeSeconds > 0 && elapsed >= challengeSeconds);
  }

  function showTask(task) {
    const estimate = Number.parseFloat(task.estimated_time);
    const challenge = Number.parseFloat(task.challenge_time);
    estimatedSeconds = Number.isFinite(estimate) && estimate > 0 ? estimate * 60 : 15 * 60;
    challengeSeconds = Number.isFinite(challenge) && challenge > 0 ? challenge * 60 : 0;
    render(task.ticket_title || task.title || 'Your assignment', task.motivation || 'Please proceed with your important work.', `ASSIGNMENT / ${task.source_list || 'TODO'}${task.selection_method ? ' / ' + task.selection_method.toUpperCase() : ''}`);
    el('taskTimer').hidden = false;
    el('challengeRow').hidden = challengeSeconds === 0;
    startedAt = Date.now();
    updateTimer();
    timer = setInterval(updateTimer, 1000);
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
    render('Retrieving your assignment…', 'Consulting the mainframe. Your ticket will print when ready.', 'TASK ALLOCATION');
    try {
      const result = await request('/print_task');
      stopTimer();
      currentTask = result.task;
      showTask(currentTask);
    } catch (error) {
      currentTask = previousTask;
      render('Mainframe notice', error.status === 404 ? 'No suitable assignment was selected. The Trello queue and task-selection service may need checking.' : 'Unable to retrieve an assignment. Check the connection before retrying; a ticket may already have printed.', 'ALLOCATION INTERRUPTED');
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
      if (action === 'complete') {
        completed++;
        el('completedCount').textContent = completed;
        render('Refinement recorded.', 'Your assignment has been completed.\nThank you for your service to Lumon.', 'ASSIGNMENT COMPLETE');
      } else {
        render('Assignment deferred.', 'This task will be held for seven days.\nSelect New Task to continue your work.', 'ASSIGNMENT SKIPPED');
      }
    } catch (error) {
      // Keep the current task and timer so failed actions can be retried.
      render('Mainframe notice', 'The assignment remains open here. Its update could not be confirmed; check Trello before retrying.', 'UPDATE NOT CONFIRMED');
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
      if (status.selection_mode) el('assignmentLabel').textContent = status.selection_mode;
      connection.classList.toggle('online', status.ok === true);
      connection.classList.toggle('unavailable', status.ok !== true);
      connection.textContent = status.ok ? 'TRELLO ONLINE' : 'TRELLO UNAVAILABLE';
      for (const [id, key] of [['todoCount', 'todo'], ['doingCount', 'doing'], ['btnCount', 'btn']]) {
        el(id).textContent = status.ok ? (status.counts[key] ?? '—') : '—';
      }
    } catch (error) {
      connection.classList.remove('online');
      connection.classList.add('unavailable');
      connection.textContent = 'STATUS UNAVAILABLE';
      for (const id of ['todoCount', 'doingCount', 'btnCount']) el(id).textContent = '—';
    }
  }

  function updateClock() {
    const now = new Date();
    el('dateTime').textContent = now.toLocaleDateString('en-GB', { day: '2-digit', month: '2-digit', year: 'numeric', timeZone: timezone }) + '  ' + now.toLocaleTimeString('en-GB', { timeZone: timezone });
    el('dateTime').dateTime = now.toISOString();
  }

  buttons[0].addEventListener('click', newTask);
  buttons[1].addEventListener('click', () => finishTask('complete'));
  buttons[2].addEventListener('click', () => finishTask('skip'));
  document.addEventListener('keydown', event => {
    if (event.repeat || event.ctrlKey || event.metaKey || event.altKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
    const index = { n: 0, y: 1, x: 2 }[event.key.toLowerCase()];
    if (index !== undefined) { event.preventDefault(); buttons[index].click(); }
  });
  updateClock();
  updateControls();
  refreshStatus();
  setInterval(updateClock, 1000);
  setInterval(refreshStatus, 60000);
})();

document.addEventListener("DOMContentLoaded", () => {
  const btnGenerarTablas = document.getElementById("btnGenerarTablas");
  const btnParsear = document.getElementById("btnParsear");
  const grammarInput = document.getElementById("grammarInput");
  const inputCadena = document.getElementById("inputCadena");
  
  const leftTabBtns = document.querySelectorAll('#left-panel .tab-btn');
  const parseTabBtn = document.getElementById("parse-tab-btn");
  
  const rightTabBtns = document.querySelectorAll('#right-panel .tab-btn');
  const traceTabBtn = document.getElementById("trace-tab-btn");
  
  const toggleBtns = document.querySelectorAll('.toggle-btn');
  
  const actionGotoContainer = document.getElementById("action-goto-container");
  const dfaDiagramContainer = document.getElementById("dfa-diagram-container");
  const traceContainer = document.getElementById("trace-container");
  const combinedTable = document.getElementById("combined-table");
  const dfaDiagram = document.getElementById("dfa-diagram");
  const currentTraceTable = document.getElementById("current-trace-table");
  
  const prevTraceBtn = document.getElementById("prev-trace");
  const nextTraceBtn = document.getElementById("next-trace");
  const traceCounter = document.getElementById("trace-counter");

  let currentTablesData = null;
  let allTraces = [];
  let currentTraceIndex = 0;

  function initializeApp() {
    updateNotification("Esperando acción... 🌸", "waiting");
    
    showEmptyTables();
    showEmptyDiagram();
    showEmptyTrace();
    
    setupTraceNavigation();
    setupNotificationClose();
    setupLeftTabs();
    setupRightTabs();
    setupViewToggle();
  }

  function setupLeftTabs() {
    leftTabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        
        leftTabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('#left-panel .tab-pane').forEach(pane => pane.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');
      });
    });
  }

  function setupRightTabs() {
    rightTabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.getAttribute('data-tab');
        
        rightTabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('#right-panel .tab-pane').forEach(pane => pane.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');
      });
    });
  }

  function setupViewToggle() {
    toggleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.getAttribute('data-view');
        
        toggleBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        if (view === 'table') {
          actionGotoContainer.style.display = 'block';
          dfaDiagramContainer.style.display = 'none';
        } else {
          actionGotoContainer.style.display = 'none';
          dfaDiagramContainer.style.display = 'block';
          if (currentTablesData && currentTablesData.dfa) {
            createVisualDFADiagram(currentTablesData.dfa);
          } else {
            showEmptyDiagram();
          }
        }
      });
    });
  }

  function showEmptyTables() {
    combinedTable.innerHTML = `
      <thead>
        <tr>
          <th rowspan="2" class="state-cell">Estado</th>
          <th colspan="1" class="combined-header">ACTION</th>
          <th colspan="1" class="combined-header">GOTO</th>
        </tr>
        <tr class="subheader-row">
          <th>Terminales</th>
          <th>No Terminales</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td colspan="3" style="padding: 40px; text-align: center; color: #7b52ab;">
            Genera las tablas LR(1) para ver la información aquí 🌸
          </td>
        </tr>
      </tbody>
    `;
  }

  function showEmptyDiagram() {
    dfaDiagram.innerHTML = `
      <div style="text-align: center; color: #7b52ab; padding: 40px;">
        <p>Genera las tablas LR(1) para ver el diagrama DFA aquí 🌸</p>
        <p style="font-size: 12px; margin-top: 10px;">Usa el botón "Generar Tablas LR(1)" primero</p>
      </div>
    `;
  }

  function showEmptyTrace() {
    currentTraceTable.innerHTML = `
      <thead>
        <tr>
          <th>Pila</th>
          <th>Entrada</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td colspan="3" style="padding: 40px; text-align: center; color: #7b52ab;">
            Parsea una cadena para ver la traza aquí 🌸
          </td>
        </tr>
      </tbody>
    `;
  }

  function setupTraceNavigation() {
    prevTraceBtn.addEventListener("click", () => {
      if (currentTraceIndex > 0) {
        currentTraceIndex--;
        showCurrentTrace();
      }
    });

    nextTraceBtn.addEventListener("click", () => {
      if (currentTraceIndex < allTraces.length - 1) {
        currentTraceIndex++;
        showCurrentTrace();
      }
    });
  }

  function updateNotification(message, type = "waiting") {
    const popup = document.getElementById("notification-popup");
    const popupMessage = document.getElementById("popup-message");
    
    popup.classList.remove("notification-visible", "notification-slide-in");
    popup.classList.add("notification-slide-out");
    
    setTimeout(() => {
      popupMessage.textContent = message;
      popup.className = "notification-popup-" + type;
      popup.classList.add("notification-visible", "notification-slide-in");
      popup.classList.remove("notification-hidden");
    }, 300);
  }

  function setupNotificationClose() {
    const closeBtn = document.querySelector(".close-btn");
    const popup = document.getElementById("notification-popup");
    
    closeBtn.addEventListener("click", () => {
      popup.classList.remove("notification-visible", "notification-slide-in");
      popup.classList.add("notification-slide-out");
      
      setTimeout(() => {
        popup.classList.add("notification-hidden");
      }, 300);
    });
  }

  function autoHideNotification() {
    setTimeout(() => {
      const popup = document.getElementById("notification-popup");
      if (popup.classList.contains("notification-visible")) {
        popup.classList.remove("notification-visible", "notification-slide-in");
        popup.classList.add("notification-slide-out");
        
        setTimeout(() => {
          popup.classList.add("notification-hidden");
        }, 300);
      }
    }, 5000);
  }

  btnGenerarTablas.addEventListener("click", async () => {
    const grammar = grammarInput.value.trim();

    if (!grammar) {
      updateNotification("Por favor ingresa una gramática 🌸", "error");
      autoHideNotification();
      return;
    }

    try {
      updateNotification("Generando tablas LR(1)... ⏳", "waiting");
      
      const response = await fetch("/api/generate-tables", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ grammar }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Error del servidor");
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      currentTablesData = data;
      mostrarTablaCombinada(data);
      parseTabBtn.style.display = 'block';
      traceTabBtn.style.display = 'block';
      
      updateNotification("✨ Tablas generadas exitosamente!", "success");
      autoHideNotification();
      
    } catch (error) {
      console.error("Error:", error);
      updateNotification(`❌ Error: ${error.message}`, "error");
      autoHideNotification();
    }
  });

  btnParsear.addEventListener("click", async () => {
    const input = inputCadena.value.trim();
    
    if (!currentTablesData) {
      updateNotification("Primero genera las tablas LR(1) 🌸", "error");
      autoHideNotification();
      return;
    }

    if (!input) {
      updateNotification("Por favor ingresa una cadena para parsear 🌸", "error");
      autoHideNotification();
      return;
    }

    try {
      updateNotification("Parseando cadena... ⏳", "waiting");
      
      const response = await fetch("/api/parse-string", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          grammar: grammarInput.value.trim(),
          input: input 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Error del servidor");
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      allTraces.push({
        data: data,
        input: input,
        timestamp: new Date().toLocaleTimeString()
      });
      
      currentTraceIndex = allTraces.length - 1;
      mostrarResultadoParseo(data);
      
      rightTabBtns.forEach(b => b.classList.remove('active'));
      document.querySelectorAll('#right-panel .tab-pane').forEach(pane => pane.classList.remove('active'));
      traceTabBtn.classList.add('active');
      document.getElementById('trace-tab').classList.add('active');
      
    } catch (error) {
      console.error("Error:", error);
      updateNotification(`❌ Error: ${error.message}`, "error");
      autoHideNotification();
    }
  });

  function mostrarTablaCombinada(data) {
    if (!data.action || !data.goto) return;

    const terminals = data.terminals || [];
    const nonterminals = data.nonterminals || [];
    
    const allStates = new Set([
      ...Object.keys(data.action),
      ...Object.keys(data.goto)
    ]);
    const states = Array.from(allStates).sort((a, b) => parseInt(a) - parseInt(b));

    let html = `
      <thead>
        <tr>
          <th rowspan="2" class="state-cell">Estado</th>
          <th colspan="${terminals.length}" class="combined-header">ACTION</th>
          <th colspan="${nonterminals.length}" class="combined-header">GOTO</th>
        </tr>
        <tr class="subheader-row">
    `;

    terminals.forEach(terminal => {
      html += `<th>${terminal}</th>`;
    });

    nonterminals.forEach(nonterminal => {
      html += `<th>${nonterminal}</th>`;
    });

    html += `</tr></thead><tbody>`;

    states.forEach(state => {
      html += `<tr><td class="state-cell">${state}</td>`;
      
      terminals.forEach(terminal => {
        const action = data.action[state]?.[terminal];
        html += `<td class="${getActionCellClass(action)}">${formatActionValue(action)}</td>`;
      });

      nonterminals.forEach(nonterminal => {
        const goto = data.goto[state]?.[nonterminal];
        html += `<td class="${goto !== undefined ? 'goto' : ''}">${goto !== undefined ? goto : ''}</td>`;
      });

      html += `</tr>`;
    });

    html += `</tbody>`;
    combinedTable.innerHTML = html;
  }

  function createVisualDFADiagram(dfaData) {
    const diagramContainer = document.getElementById('dfa-diagram');
    diagramContainer.innerHTML = '';
    
    if (!dfaData || !dfaData.states || Object.keys(dfaData.states).length === 0) {
      diagramContainer.innerHTML = `
        <div style="text-align: center; color: #7b52ab; padding: 40px;">
          <p>No hay datos del DFA disponibles para mostrar el diagrama 🌸</p>
          <p style="font-size: 12px; margin-top: 10px;">El DFA debe generarse desde el backend</p>
        </div>
      `;
      return;
    }

    const svgLayer = document.createElement('div');
    svgLayer.className = 'dfa-arrows-layer';
    svgLayer.innerHTML = `
      <svg width="100%" height="100%">
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                  refX="9" refY="3.5" orient="auto">
            <polygon points="0 0, 10 3.5, 0 7" fill="#7b52ab"/>
          </marker>
        </defs>
      </svg>
    `;
    diagramContainer.appendChild(svgLayer);
    
    const positions = [
      {x: 100, y: 100}, {x: 400, y: 100}, {x: 100, y: 300}, 
      {x: 400, y: 300}, {x: 250, y: 200}, {x: 550, y: 200},
      {x: 250, y: 400}, {x: 550, y: 400}, {x: 700, y: 250}
    ];
    
    Object.entries(dfaData.states).forEach(([stateId, stateData], index) => {
      const node = document.createElement('div');
      node.className = `dfa-node ${isAcceptState(stateData.items) ? 'accept-state' : ''} ${stateId === '0' ? 'start-state' : ''}`;
      node.style.left = `${positions[index % positions.length].x}px`;
      node.style.top = `${positions[index % positions.length].y}px`;
      
      const items = stateData.items || [];
      node.innerHTML = `
        <div class="node-header">Estado ${stateId}</div>
        <div class="node-content">
          ${items.map(item => `<div class="node-item">${item}</div>`).join('')}
        </div>
      `;
      
      diagramContainer.appendChild(node);
    });

    drawTransitions(dfaData.transitions, positions);
    
    const controls = document.createElement('div');
    controls.className = 'dfa-controls';
    controls.innerHTML = `
      <button class="control-btn" onclick="resetDiagram()">Reset</button>
      <button class="control-btn" onclick="zoomIn()">+</button>
      <button class="control-btn" onclick="zoomOut()">-</button>
    `;
    diagramContainer.appendChild(controls);
    
    window.resetDiagram = () => createVisualDFADiagram(dfaData);
    window.zoomIn = () => console.log("Zoom in");
    window.zoomOut = () => console.log("Zoom out");
  }

  function isAcceptState(items) {
    return items.some(item => item.includes('→') && item.includes('•') && item.includes('$'));
  }

  function drawTransitions(transitions, positions) {
    const svg = document.querySelector('.dfa-arrows-layer svg');
    
    transitions.forEach((transition, index) => {
      const fromState = parseInt(transition.from);
      const toState = parseInt(transition.to);
      const label = transition.label;
      
      const fromPos = positions[fromState % positions.length];
      const toPos = positions[toState % positions.length];
      
      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', fromPos.x + 100);
      line.setAttribute('y1', fromPos.y + 50);
      line.setAttribute('x2', toPos.x + 100);
      line.setAttribute('y2', toPos.y + 50);
      line.setAttribute('stroke', '#7b52ab');
      line.setAttribute('stroke-width', '2');
      line.setAttribute('marker-end', 'url(#arrowhead)');
      
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      const midX = (fromPos.x + toPos.x) / 2 + 100;
      const midY = (fromPos.y + toPos.y) / 2 + 50;
      text.setAttribute('x', midX);
      text.setAttribute('y', midY - 10);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('fill', '#ec407a');
      text.setAttribute('font-size', '12');
      text.setAttribute('font-weight', 'bold');
      text.textContent = label;
      
      svg.appendChild(line);
      svg.appendChild(text);
    });
  }

  function getActionCellClass(action) {
    if (!action) return '';
    if (action[0] === "d") return "shift";
    if (action[0] === "r") return "reduce";
    if (action[0] === "acc") return "accept";
    return '';
  }

  function formatActionValue(action) {
    if (!action) return '';
    if (action[0] === "d") return `d${action[1]}`;
    if (action[0] === "r") {
      const [left, right] = action[1];
      const rhs = right.length > 0 ? right.join(" ") : "ε";
      return `r(${left}→${rhs})`;
    }
    if (action[0] === "acc") return "acc";
    return '';
  }

  function mostrarResultadoParseo(data) {
    if (data.result === "accept") {
      updateNotification("✅ Cadena ACEPTADA", "success");
    } else {
      updateNotification("❌ Cadena RECHAZADA", "error");
    }
    autoHideNotification();
    showCurrentTrace();
  }

  function showCurrentTrace() {
    if (allTraces.length === 0) {
      showEmptyTrace();
      return;
    }

    const currentTrace = allTraces[currentTraceIndex];
    const traceData = currentTrace.data.trace || [];

    let html = `
      <thead>
        <tr>
          <th>Pila</th>
          <th>Entrada</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>
    `;

    if (traceData.length === 0) {
      html += `
        <tr>
          <td colspan="3" style="padding: 40px; text-align: center; color: #7b52ab;">
            No hay datos de traza disponibles
          </td>
        </tr>
      `;
    } else {
      traceData.forEach(step => {
        html += `
          <tr>
            <td>${step.stack || ''}</td>
            <td>${step.input || ''}</td>
            <td class="action-cell">${step.action || ''}</td>
          </tr>
        `;
      });
    }

    html += `</tbody>`;
    currentTraceTable.innerHTML = html;
    updateTraceNavigation();
  }

  function updateTraceNavigation() {
    traceCounter.textContent = `${currentTraceIndex + 1}/${allTraces.length}`;
    prevTraceBtn.disabled = currentTraceIndex === 0;
    nextTraceBtn.disabled = currentTraceIndex === allTraces.length - 1;
  }

  initializeApp();
});
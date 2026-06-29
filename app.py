from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import calendar
import re

app = Flask(__name__)

VERSION = "6.0.0"  # Salto de versión mayor por integración de la Suite Holográfica de Juegos

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

EVENTOS_ESPACIALES = {
    5: ["Alineación orbital Satélite Kepler-12", "Descarga de telemetría de Marte"],
    12: ["Lanzamiento del cohete Falcon-X v5.1.0", "Apertura de escudo térmico"],
    18: ["Auditoría de Escudos Defensivos - Parche de software cuántico"],
    25: ["Paso del asteroide AX-2026 y recolección de espectro en AWS (Alpha-Wave System)"]
}

ESTILOS_CSS = """
body {
    background-color: var(--bs-body-bg);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    transition: background-color 0.3s, color 0.3s;
}
.gradient-header {
    background: linear-gradient(135deg, #020617 0%, #1e1b4b 100%);
    color: white;
    border-bottom: 2px solid #3b82f6;
}
.card {
    border: 1px solid var(--bs-border-color);
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    transition: all 0.3s;
}
.btn-nav {
    background-color: var(--bs-tertiary-bg);
    border: 1px solid var(--bs-border-color);
    color: var(--bs-body-color);
}
.btn-nav:hover { background-color: #3b82f6; color: white; border-color: #3b82f6; }

.btn-hoy {
    background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
}
[data-bs-theme="dark"] .btn-hoy {
    background-color: #1e3a8a; color: #60a5fa; border: 1px solid #1d4ed8;
}
.btn-hoy:hover { background-color: #3b82f6; color: white; }

.titulo-mes { font-size: 1.5rem; font-weight: 700; color: #3b82f6; text-transform: capitalize; }

.table th { color: #64748b; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
.table td { font-weight: 600; color: var(--bs-body-color); width: 45px; height: 50px; cursor: pointer; border-radius: 8px; position: relative; text-align: center; vertical-align: middle; }
.table td:not(.nonday):hover { background-color: var(--bs-secondary-bg-subtle); }
.nonday { color: #cbd5e1 !important; cursor: default !important; }
[data-bs-theme="dark"] .nonday { color: #334155 !important; }

.tiene-tarea::after {
    content: ''; position: absolute; bottom: 4px; left: 50%; transform: translateX(-50%);
    width: 6px; height: 6px; background-color: #06b6d4; border-radius: 50%;
}

.terminal-logs {
    background-color: #020617; font-family: 'Courier New', Courier, monospace; font-size: 0.85rem;
    border-radius: 8px; padding: 15px; max-height: 200px; overflow-y: auto;
    border: 1px solid #1e293b;
}
.log-info { color: #38bdf8; }
.log-success { color: #34d399; }
.log-error { color: #f87171; }

.btn-theme-toggle {
    background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255,255,255,0.2); color: white;
    padding: 8px 12px; border-radius: 50rem; font-weight: 500; transition: all 0.2s;
}
.btn-theme-toggle:hover { background: rgba(255, 255, 255, 0.2); }

.reloj-contenedor { background-color: var(--bs-light-bg-subtle); border: 1px solid var(--bs-border-color-translucent); }

/* --- ESTILOS DE LA SUITE DE JUEGOS --- */
#arcadeCanvas {
    background-color: #020617;
    border: 2px solid #1e293b;
    border-radius: 8px;
    display: block;
    margin: 0 auto;
}
.score-board {
    font-family: 'Courier New', monospace;
    font-size: 1.1rem;
    color: #38bdf8;
}
.juego-contenedor {
    display: none;
}
.juego-contenedor.active {
    display: block;
}
/* Tableros HTML para Tres en Raya y Conecta 4 */
.ttt-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    max-width: 200px;
    margin: 0 auto;
}
.ttt-cell {
    aspect-ratio: 1;
    background: #0f172a;
    border: 2px solid #3b82f6;
    border-radius: 8px;
    font-size: 1.5rem;
    font-weight: bold;
    color: #f8fafc;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}
.ttt-cell:hover { background: #1e293b; }

.c4-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 4px;
    max-width: 260px;
    margin: 0 auto;
    background: #1e3a8a;
    padding: 8px;
    border-radius: 8px;
}
.c4-cell {
    aspect-ratio: 1;
    background: #020617;
    border-radius: 50%;
    cursor: pointer;
}
.c4-cell.p1 { background: #ef4444; }
.c4-cell.p2 { background: #eab308; }
"""

PLANTILLA_HTML = """
<!DOCTYPE html>
<html lang="es" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cosmos Control Center - Angelo Vera</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>{{ estilos_css | safe }}</style>
</head>
<body>

    <div class="gradient-header py-4 mb-4 shadow-sm">
        <div class="container d-flex flex-column flex-sm-row justify-content-between align-items-center gap-3">
            <div>
                <h1 class="h3 mb-0 fw-bold"><i class="bi bi-rocket-takeoff me-2 text-info"></i>Cosmos Space Intelligence</h1>
                <small class="opacity-75">Estado del Sistema: <span class="badge bg-success">ESTABLE (ONLINE)</span></small>
            </div>
            <div class="d-flex align-items-center flex-wrap justify-content-center gap-3">
                <button class="btn-theme-toggle shadow-sm" id="themeToggler" onclick="cambiarModo()">
                    <i class="bi bi-sun-fill me-2" id="themeIcon"></i><span id="themeText">Modo Claro</span>
                </button>
                <span class="badge bg-dark text-info px-3 py-2 rounded-pill border border-secondary shadow-sm fs-7">
                    <i class="bi bi-person-bounding-box me-2"></i>Comandante: Angelo Vera - 5to A
                </span>
                <span class="badge bg-white text-dark px-3 py-2 rounded-pill fw-semibold shadow-sm">Quantum-v{{ version }}</span>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row g-4">
            
            <div class="col-12 col-lg-4 d-flex flex-column gap-4">
                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #e0f2fe; color: #0369a1;"><i class="bi bi-hourglass-split fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Tiempo Estelar de Misión</h5>
                    </div>
                    <div class="rounded-3 p-3 text-center my-2 reloj-contenedor">
                        <h2 class="fw-bold mb-0" id="reloj-pc" style="color: #3b82f6; letter-spacing: -1px;">00:00:00</h2>
                        <small class="text-muted fw-semibold" id="fecha-pc">Cargando fecha estelar...</small>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="d-flex align-items-center">
                            <div class="rounded-3 p-2 me-2" style="background-color: #dcfce7; color: #15803d;"><i class="bi bi-controller fs-5"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary fs-6">Centro de Recreación</h5>
                        </div>
                        <span class="score-board fw-bold small" id="globalScore">SCORE: 0</span>
                    </div>

                    <select class="form-select form-select-sm mb-3" id="gameSelector" onchange="cambiarJuego(this.value)">
                        <option value="snake">Quantum Snake (Culebrita)</option>
                        <option value="naves">Space Defender (Navecitas)</option>
                        <option value="ttt">Hyper Tic-Tac-Toe (3 en Raya)</option>
                        <option value="c4">Orbital Connect 4 (Conecta 4)</option>
                    </select>

                    <div id="canvasContainer" class="position-relative text-center mx-auto" style="width: 280px; height: 200px;">
                        <canvas id="arcadeCanvas" width="280" height="200" class="w-100 h-100"></canvas>
                        
                        <div id="tttContainer" class="juego-contenedor position-absolute top-50 start-50 translate-middle w-100">
                            <div class="ttt-grid" id="tttGrid"></div>
                        </div>

                        <div id="c4Container" class="juego-contenedor position-absolute top-50 start-50 translate-middle w-100">
                            <div class="c4-grid" id="c4Grid"></div>
                        </div>
                    </div>

                    <div class="text-center mt-3">
                        <button class="btn btn-outline-info btn-sm px-3" onclick="reiniciarJuegoActual()"><i class="bi bi-arrow-clockwise"></i> Reiniciar Matriz</button>
                    </div>
                </div>
            </div>

            <div class="col-12 col-lg-8">
                <div class="card p-4 shadow-sm" id="calendar-card">
                    <div class="d-flex flex-wrap justify-content-between align-items-center gap-2 mb-3">
                        <div class="d-flex gap-1">
                            <a href="/?year={{ prev_ano_solo }}&month={{ mes_vista }}" class="btn btn-nav btn-sm shadow-sm">« Año</a>
                            <a href="/?year={{ prev_ano }}&month={{ prev_mes }}" class="btn btn-nav btn-sm shadow-sm">‹ Mes</a>
                        </div>
                        <span class="titulo-mes">{{ nombre_mes_vista }} {{ ano_vista }}</span>
                        <div class="d-flex gap-1">
                            <a href="/?year={{ next_ano }}&month={{ next_mes }}" class="btn btn-nav btn-sm shadow-sm">Mes ›</a>
                            <a href="/?year={{ next_ano_solo }}&month={{ mes_vista }}" class="btn btn-nav btn-sm shadow-sm">Año »</a>
                        </div>
                    </div>

                    <div class="text-center mb-3">
                        <a href="/" class="btn btn-hoy btn-sm fw-bold px-4 shadow-sm"><i class="bi bi-globe2 me-1"></i> Retornar al Mes Estelar Actual</a>
                    </div>

                    <div class="table-responsive">
                        {{ calendario_html | safe }}
                    </div>

                    <div class="mt-3 p-3 bg-body-tertiary rounded-3 border">
                        <h6 class="fw-bold mb-2 text-primary"><i class="bi bi-info-circle me-2"></i>Misiones Programadas para el Día:</h6>
                        <ul id="lista-tareas" class="mb-0 small text-muted">
                            <li>Haz clic en los días marcados con el indicador azul inferior para ver los eventos estelares registrados.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card p-4 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold text-secondary mb-0"><i class="bi bi-terminal-dash me-2"></i>Canal de Datos del Deep Space (Telemetría)</h5>
                        <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('terminal').innerHTML=''"><i class="bi bi-trash3"></i> Limpiar Telemetría</button>
                    </div>
                    <div class="terminal-logs" id="terminal">
                        <span class="log-info">[COSMOS CORE] Inicializando suite multi-simulación cuántica... OK</span><br>
                        <span class="log-success">[SUCCESS] Sistemas listos para operaciones de recreación del comandante Angelo Vera.</span><br>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="container text-center text-muted small my-5 py-3 border-top opacity-50">
        Agencia de Inteligencia Cosmos &bull; Comandante Angelo Vera &bull; Año Estelar 2026
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // --- SISTEMA GENERAL ---
        const htmlElement = document.documentElement;
        const term = document.getElementById('terminal');

        function cambiarModo() {
            const nuevoTema = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
            htmlElement.setAttribute('data-bs-theme', nuevoTema);
            document.getElementById('themeIcon').className = nuevoTema === 'dark' ? 'bi bi-sun-fill me-2' : 'bi bi-moon-stars-fill me-2';
            document.getElementById('themeText').innerText = nuevoTema === 'dark' ? 'Modo Claro' : 'Modo Oscuro';
        }

        function actualizarReloj() {
            const ahora = new Date();
            document.getElementById('reloj-pc').innerText = ahora.toLocaleTimeString('es-ES', { hour12: false });
            let fecha = ahora.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            document.getElementById('fecha-pc').innerText = "Fecha de la Tierra: " + fecha.charAt(0).toUpperCase() + fecha.slice(1);
        }
        setInterval(actualizarReloj, 1000); actualizarReloj();

        function logTerminal(msg, tipo='info') {
            const colores = { info: 'log-info', success: 'log-success', error: 'log-error' };
            term.innerHTML += `<span class="${colores[tipo]}">[${new Date().toLocaleTimeString()}] ${msg}</span><br>`;
            term.scrollTop = term.scrollHeight;
        }

        function verTareas(dia, mes, ano) {
            logTerminal(`[TELEMETRÍA] Consultando coordenadas orbitales para el día ${dia}/${mes}/${ano}...`);
            fetch(`/api/eventos?day=${dia}`)
                .then(res => res.json())
                .then(data => {
                    const lista = document.getElementById('lista-tareas');
                    lista.innerHTML = "";
                    if(data.eventos.length === 0) {
                        lista.innerHTML = "<li>No hay misiones programadas para esta fecha estelar.</li>";
                        logTerminal(`[MONITOR] Cuadrante despejado el día ${dia}.`);
                    } else {
                        data.eventos.forEach(evt => {
                            lista.innerHTML += `<li class="fw-bold text-info">${evt}</li>`;
                            logTerminal(`[EVENTO] Detectado: ${evt}`, 'success');
                        });
                    }
                });
        }

        // --- ENGINE DE LA SUITE DE JUEGOS ---
        const canvas = document.getElementById("arcadeCanvas");
        const ctx = canvas.getContext("2d");
        let juegoActual = "snake";
        let loopPrincipal;

        // Variables de Control Global
        let score = 0;
        const scale = 10;

        function cambiarJuego(tipo) {
            juegoActual = tipo;
            clearInterval(loopPrincipal);
            document.getElementById("tttContainer").classList.remove("active");
            document.getElementById("c4Container").classList.remove("active");
            canvas.style.display = "block";

            logTerminal(`[SISTEMA] Cargando módulo holográfico: ${tipo.toUpperCase()}`);
            reiniciarJuegoActual();
        }

        function reiniciarJuegoActual() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            score = 0;
            actScore();
            if (juegoActual === "snake") initSnake();
            else if (juegoActual === "naves") initNaves();
            else if (juegoActual === "ttt") initTTT();
            else if (juegoActual === "c4") initC4();
        }

        function actScore() {
            document.getElementById("globalScore").innerText = "SCORE: " + score;
        }

        // --- INTERCEPCIÓN DE TECLADO ---
        document.addEventListener("keydown", function(e) {
            if([32, 37, 38, 39, 40].includes(e.keyCode)) e.preventDefault();
            if (juegoActual === "snake") controlSnake(e.keyCode);
            if (juegoActual === "naves") controlNaves(e.keyCode);
        });

        // ==========================================
        // MÓDULO 1: QUANTUM SNAKE
        // ==========================================
        let snake, snakeFood, snakeDir;
        function initSnake() {
            snake = [{x: 50, y: 50}];
            snakeDir = "RIGHT";
            genSnakeFood();
            loopPrincipal = setInterval(loopSnake, 90);
        }
        function genSnakeFood() {
            snakeFood = {
                x: Math.floor(Math.random() * (canvas.width/scale)) * scale,
                y: Math.floor(Math.random() * (canvas.height/scale)) * scale
            };
        }
        function controlSnake(key) {
            if (key == 37 && snakeDir != "RIGHT") snakeDir = "LEFT";
            if (key == 38 && snakeDir != "DOWN") snakeDir = "UP";
            if (key == 39 && snakeDir != "LEFT") snakeDir = "RIGHT";
            if (key == 40 && snakeDir != "UP") snakeDir = "DOWN";
        }
        function loopSnake() {
            ctx.fillStyle = "#020617"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Dibujar comida
            ctx.fillStyle = "#34d399"; ctx.fillRect(snakeFood.x, snakeFood.y, scale, scale);
            
            // Avanzar Cabeza
            let headX = snake[0].x; let headY = snake[0].y;
            if(snakeDir === "LEFT") headX -= scale; if(snakeDir === "UP") headY -= scale;
            if(snakeDir === "RIGHT") headX += scale; if(snakeDir === "DOWN") headY += scale;

            let newHead = {x: headX, y: headY};
            if(headX < 0 || headY < 0 || headX >= canvas.width || headY >= canvas.height || snake.some(s => s.x === newHead.x && s.y === newHead.y)) {
                clearInterval(loopPrincipal);
                logTerminal("[SNAKE] Red cuántica colapsada. Juego Terminado.", "error");
                return;
            }

            snake.unshift(newHead);
            if(headX === snakeFood.x && headY === snakeFood.y) { score++; actScore(); genSnakeFood(); } else { snake.pop(); }

            ctx.fillStyle = "#22d3ee";
            snake.forEach(s => ctx.fillRect(s.x, s.y, scale, scale));
        }

        // ==========================================
        // MÓDULO 2: SPACE DEFENDER (NAVECITAS)
        // ==========================================
        let naveX, proyectiles, asteroides;
        function initNaves() {
            naveX = canvas.width / 2;
            proyectiles = [];
            asteroides = [];
            loopPrincipal = setInterval(loopNaves, 40);
        }
        function controlNaves(key) {
            if(key == 37 && naveX > 10) naveX -= 15;
            if(key == 39 && naveX < canvas.width - 20) naveX += 15;
            if(key == 32) proyectiles.push({x: naveX + 5, y: canvas.height - 20});
        }
        function loopNaves() {
            ctx.fillStyle = "#020617"; ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Dibujar nave
            ctx.fillStyle = "#a855f7"; ctx.fillRect(naveX, canvas.height - 15, 15, 10);

            // Spawn Asteroides
            if(Math.random() < 0.07) asteroides.push({x: Math.random()*(canvas.width-10), y: 0});

            // Actualizar Balas
            ctx.fillStyle = "#38bdf8";
            proyectiles.forEach((p, pi) => {
                p.y -= 6; ctx.fillRect(p.x, p.y, 3, 7);
                if(p.y < 0) proyectiles.splice(pi, 1);
            });

            // Actualizar Asteroides
            ctx.fillStyle = "#ef4444";
            asteroides.forEach((ast, ai) => {
                ast.y += 3; ctx.fillRect(ast.x, ast.y, 10, 10);
                if(ast.y > canvas.height) { clearInterval(loopPrincipal); logTerminal("[DEFENDER] Escudos vulnerados. Base destruida.", "error"); }
                
                // Colisiones
                proyectiles.forEach((p, pi) => {
                    if(p.x >= ast.x && p.x <= ast.x + 10 && p.y >= ast.y && p.y <= ast.y + 10) {
                        asteroides.splice(ai, 1); proyectiles.splice(pi, 1);
                        score++; actScore();
                    }
                });
            });
        }

        // ==========================================
        // MÓDULO 3: HYPER TIC-TAC-TOE (3 EN RAYA)
        // ==========================================
        let tttBoard, turnoTTT;
        function initTTT() {
            canvas.style.display = "none";
            const container = document.getElementById("tttContainer");
            container.classList.add("active");
            const grid = document.getElementById("tttGrid");
            grid.innerHTML = "";
            tttBoard = Array(9).fill(null);
            turnoTTT = "X";
            
            for(let i=0; i<9; i++) {
                let cell = document.createElement("div");
                cell.className = "ttt-cell";
                cell.dataset.id = i;
                cell.addEventListener("click", clickTTT);
                grid.appendChild(cell);
            }
        }
        function clickTTT(e) {
            let id = e.target.dataset.id;
            if(tttBoard[id] || verificarGanadorTTT()) return;

            tttBoard[id] = turnoTTT;
            e.target.innerText = turnoTTT;
            e.target.style.color = turnoTTT === "X" ? "#38bdf8" : "#ec4899";

            if(verificarGanadorTTT()) {
                logTerminal(`[3 EN RAYA] Victoria del nodo espacial: ${turnoTTT}`, "success");
                score += 10; actScore();
                return;
            }
            turnoTTT = turnoTTT === "X" ? "O" : "X";
        }
        function verificarGanadorTTT() {
            const combinaciones = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
            return combinaciones.some(c => tttBoard[c[0]] && tttBoard[c[0]] === tttBoard[c[1]] && tttBoard[c[0]] === tttBoard[c[2]]);
        }

        // ==========================================
        // MÓDULO 4: ORBITAL CONNECT 4 (CONECTA 4)
        // ==========================================
        let c4Board, turnoC4;
        function initC4() {
            canvas.style.display = "none";
            document.getElementById("c4Container").classList.add("active");
            const grid = document.getElementById("c4Grid");
            grid.innerHTML = "";
            c4Board = Array(6).fill(null).map(() => Array(7).fill(0));
            turnoC4 = 1;

            for(let r=0; r<6; r++) {
                for(let c=0; c<7; c++) {
                    let cell = document.createElement("div");
                    cell.className = "c4-cell";
                    cell.id = `c4-${r}-${c}`;
                    cell.addEventListener("click", () => clickC4(c));
                    grid.appendChild(cell);
                }
            }
        }
        function clickC4(col) {
            for(let r=5; r>=0; r--) {
                if(c4Board[r][col] === 0) {
                    c4Board[r][col] = turnoC4;
                    let cell = document.getElementById(`c4-${r}-${col}`);
                    cell.classList.add(turnoC4 === 1 ? 'p1' : 'p2');
                    
                    if(verificarC4(r, col)) {
                        logTerminal(`[CONECTA 4] Flota ${turnoC4 === 1 ? 'ROJA' : 'AMARILLA'} asegura el cuadrante.`, "success");
                        score += 20; actScore();
                        return;
                    }
                    turnoC4 = turnoC4 === 1 ? 2 : 1;
                    return;
                }
            }
        }
        function verificarC4(r, c) {
            let p = c4Board[r][c];
            // Validación simplificada de filas/columnas en entorno local
            let h=0, v=0;
            for(let i=0; i<7; i++) { h = (c4Board[r][i] === p) ? h+1 : 0; if(h>=4) return true; }
            for(let i=0; i<6; i++) { v = (c4Board[i][c] === p) ? v+1 : 0; if(v>=4) return true; }
            return false;
        }

        // Arranque inicial automático
        cambiarJuego("snake");
    </script>
</body>
</html>
"""

class CalendarioEspacial(calendar.HTMLCalendar):
    def __init__(self, eventos, mes_vista, ano_vista):
        super().__init__(calendar.MONDAY)
        self.eventos = eventos
        self.mes_vista = mes_vista
        self.ano_vista = ano_vista

    def formatday(self, day, weekday):
        if day == 0: return '<td class="nonday">&nbsp;</td>'
        clase_css = "tiene-tarea" if day in self.eventos else ""
        return f'<td class="{clase_css}" onclick="verTareas({day}, {self.mes_vista}, {self.ano_vista})">{day}</td>'

    def formatweek(self, theweek):
        s = ''.join(self.formatday(d, wd) for (d, wd) in theweek)
        return f'<tr>{s}</tr>'

    def formatmonth(self, Bureau, month, withyear=True):
        v = []
        a = v.append
        a('<table class="table table-bordered border-secondary table-sm align-middle text-center mb-0">')
        a('<thead><tr><th scope="col">Lun</th><th scope="col">Mar</th><th scope="col">Mié</th><th scope="col">Jue</th><th scope="col">Vie</th><th scope="col">Sáb</th><th scope="col">Dom</th></tr></thead>')
        a('<tbody>')
        for subclass in self.monthdays2calendar(Bureau, month):
            a(self.formatweek(subclass))
        a('</tbody></table>')
        return ''.join(v)

@app.route('/')
def home():
    hoy = datetime.now()
    mes_vista = request.args.get('month', default=hoy.month, type=int)
    ano_vista = request.args.get('year', default=hoy.year, type=int)
    
    if mes_vista < 1 or mes_vista > 12: mes_vista = hoy.month
    nombre_mes_vista = MESES_ES[mes_vista]

    prev_mes = mes_vista - 1 if mes_vista > 1 else 12
    prev_ano = ano_vista if mes_vista > 1 else ano_vista - 1
    next_mes = mes_vista + 1 if mes_vista < 12 else 1
    next_ano = ano_vista if mes_vista < 12 else ano_vista + 1

    eventos_mes = EVENTOS_ESPACIALES if mes_vista == 5 else {}

    cal = CalendarioEspacial(eventos_mes, mes_vista, ano_vista)
    calendario_html = cal.formatmonth(ano_vista, mes_vista)

    return render_template_string(
        PLANTILLA_HTML,
        estilos_css=ESTILOS_CSS,
        version=VERSION,
        hoy=hoy,
        calendario_html=calendario_html,
        nombre_mes_vista=nombre_mes_vista,
        mes_vista=mes_vista,
        ano_vista=ano_vista,
        prev_mes=prev_mes,
        prev_ano=prev_ano,
        next_mes=next_mes,
        next_ano=next_ano,
        prev_ano_solo=ano_vista - 1,
        next_ano_solo=ano_vista + 1
    )

@app.route('/api/eventos')
def api_eventos():
    day = request.args.get('day', default=0, type=int)
    eventos = EVENTOS_ESPACIALES.get(day, [])
    return jsonify({"day": day, "eventos": eventos})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
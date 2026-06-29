from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import calendar
import random
import re

app = Flask(__name__)

VERSION = "5.1.0"  # Versión de la IA de navegación cuántica

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Transformado: Tareas DevOps -> Eventos Astronómicos / Órbitas de Misiones
EVENTOS_ESPACIALES = {
    5: ["Alineaciónnn orbital Satélite Kepler-12", "Descarga de telemetría de Marte"],
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
.log-error { color: #f87171; animation: blinker 1.5s linear infinite; }
.log-alert { color: #fbbf24; font-weight: bold; }
.log-deploy { color: #ec4899; }
.log-training { color: #a855f7; }

@keyframes blinker { 50% { opacity: 0.5; } }

.btn-theme-toggle {
    background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255,255,255,0.2); color: white;
    padding: 8px 12px; border-radius: 50rem; font-weight: 500; transition: all 0.2s;
}
.btn-theme-toggle:hover { background: rgba(255, 255, 255, 0.2); }

.reloj-contenedor { background-color: var(--bs-light-bg-subtle); border: 1px solid var(--bs-border-color-translucent); }

.pulse-danger {
    animation: pulse-bg 1s infinite alternate;
}
@keyframes pulse-bg {
    0% { background-color: rgba(239, 68, 68, 0.1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
    100% { background-color: rgba(239, 68, 68, 0.25); box-shadow: 0 0 10px 4px rgba(239, 68, 68, 0.2); }
}

.video-responsive {
    position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 12px;
}
.video-responsive iframe {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;
}
"""

PLANTILLA_HTML = """
<!DOCTYPE html>
<html lang="es" data-bs-theme="light">
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
                <small class="opacity-75">Estado de la Red: <span id="status-global-badge" class="badge bg-success">ESTABLE (ONLINE)</span></small>
            </div>
            <div class="d-flex align-items-center flex-wrap justify-content-center gap-3">
                <button class="btn-theme-toggle shadow-sm" id="themeToggler" onclick="cambiarModo()">
                    <i class="bi bi-moon-stars-fill me-2" id="themeIcon"></i><span id="themeText">Modo Oscuro</span>
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

                <div class="card p-4 shadow-sm" id="recursos-card">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="recursos-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #f0fdf4; color: #166534;"><i class="bi bi-shield-shaded fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Reactores Cuánticos</h5>
                        </div>
                        <div class="form-check form-switch" title="Simular Ataque de Radiación Solar / Alerta Roja">
                            <input class="form-check-input" type="checkbox" id="panicSwitch" onchange="alternarPanico()">
                            <label class="form-check-label text-danger small fw-bold" for="panicSwitch"><i class="bi bi-exclamation-octagon-fill"></i></label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1"><span>Temperatura del Núcleo</span><span id="cpu-txt">18%</span></div>
                        <div class="progress" style="height: 8px;"><div id="cpu-bar" class="progress-bar bg-info" style="width: 18%"></div></div>
                    </div>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1"><span>Energía de los Escudos</span><span id="ram-txt">42%</span></div>
                        <div class="progress" style="height: 8px;"><div id="ram-bar" class="progress-bar bg-primary" style="width: 42%"></div></div>
                    </div>
                    <hr class="opacity-25">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="small text-muted fw-semibold">Navegación Ininterrumpida:</span>
                        <span id="uptime-contador" class="badge bg-success-subtle text-success fw-bold p-2 fs-7">142 Días Luz</span>
                    </div>
                </div>

                <div class="card p-4 shadow-sm" id="alarm-card">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="alarm-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #fff7ed; color: #c2410c;"><i class="bi bi-broadcast-pin fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Umbral de Radiación Alfa</h5>
                        </div>
                        <span id="alarm-status-badge" class="badge bg-secondary">Seguro</span>
                    </div>
                    
                    <label for="cpuThreshold" class="form-label small fw-bold text-muted">Disparar Alerta Roja si la radiación supera el:</label>
                    <div class="d-flex align-items-center gap-3 mb-3">
                        <input type="range" class="form-range" id="cpuThreshold" min="50" max="95" value="80" oninput="actualizarThresholdTexto(this.value)">
                        <span id="threshold-val" class="fw-bold text-primary fs-5" style="min-width: 45px;">80%</span>
                    </div>

                    <div class="form-check form-check-inline small">
                        <input class="form-check-input" type="checkbox" id="muteSound" checked>
                        <label class="form-check-label text-muted" for="muteSound"><i class="bi bi-volume-mute"></i> Silenciar alarma sónica</label>
                    </div>
                </div>

            </div>

            <div class="col-12 col-lg-8 d-flex flex-column gap-4">
                
                <div class="card p-4 shadow-sm" id="calendar-card"
                     data-today-day="{{ hoy.day }}" data-today-month="{{ hoy.month }}" data-today-year="{{ hoy.year }}"
                     data-view-month="{{ mes_vista }}" data-view-year="{{ ano_vista }}">
                    
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
                            <li>Haz clic en los días marcados con azul celeste para ver los eventos estelares y órbitas satelitales registradas.</li>
                        </ul>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
                        <div class="d-flex align-items-center">
                            <div class="rounded-3 p-2 me-3" style="background-color: #fdf2f8; color: #be185d;"><i class="bi bi-patch-check fs-4"></i></div>
                            <div>
                                <h5 class="mb-0 fw-bold text-secondary">Salto al Hiperespacio / Relanzamiento de Sonda</h5>
                                <small class="text-muted">Destino fijado: <code class="text-pink">Gliese-581g (Sonda Exploradora)</code></small>
                            </div>
                        </div>
                        <button class="btn btn-pink text-white fw-bold px-3 shadow-sm" style="background-color: #ec4899; border: none;" id="btnDeploy" onclick="iniciarDespliegue()">
                            <i class="bi bi-send-fill me-1"></i> Iniciar Salto
                        </button>
                    </div>

                    <div id="deploy-process-box" class="p-3 bg-body-tertiary rounded-3 border" style="display:none;">
                        <div class="d-flex justify-content-between small fw-bold mb-2">
                            <span id="deploy-step-text" class="text-pink">Cargando motores de plasma...</span>
                            <span id="deploy-pct-text">0%</span>
                        </div>
                        <div class="progress" style="height: 10px;">
                            <div id="deploy-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated bg-pink" style="width: 0%; background-color: #ec4899;"></div>
                        </div>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #ffe4e6; color: #f43f5e;"><i class="bi bi-disc fs-4"></i></div>
                        <div>
                            <h5 class="mb-0 fw-bold text-secondary">Frecuencias del Cosmos & Música Terrícola</h5>
                            <small class="text-muted">Banda sonora seleccionada para los astronautas de la estación espacial</small>
                        </div>
                    </div>
                    
                    <div class="d-flex flex-wrap gap-2 mb-3" id="video-button-group">
                        <button class="btn btn-outline-danger btn-sm active fw-semibold" id="btn-vid1" onclick="cambiarVideo('Aztra - El Mañana', 'Muestra artística del emblemático tema musical \\'El Mañana\\' interpretado por la icónica banda de rock/metal nacional ecuatoriana Aztra.', '🎸 Rock/Metal EC', 'https://www.youtube.com/embed/PhkfHrljRiQ', 'btn-vid1')">
                            <i class="bi bi-music-note-beamed me-1"></i> Aztra - El Mañana
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid2" onclick="cambiarVideo('Aztra - Eres', 'Potente balada rock e himno de la agrupación ecuatoriana Aztra, destacando la riqueza instrumental de la música de nuestra tierra.', '🎸 Rock/Metal EC', 'https://www.youtube.com/embed/NhdxusBZlZA', 'btn-vid2')">
                            <i class="bi bi-music-note-beamed me-1"></i> Aztra - Eres
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid3" onclick="cambiarVideo('WarCry - La vida en un beso', 'Espectacular pieza musical de Power Metal interpretada por la legendaria banda española WarCry.', '⚔️ Power Metal ES', 'https://www.youtube.com/embed/GEFjJr1lK6c', 'btn-vid3')">
                            <i class="bi bi-music-note-beamed me-1"></i> WarCry - La vida en un beso
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid4" onclick="cambiarVideo('Boddega - Mi recuerdo, un cigarrillo', 'Clásica y nostálgica balada de rock nacional ecuatoriano interpretada por el legendario grupo Boddega.', '🎙️ Rock Clásico EC', 'https://www.youtube.com/embed/gXZ3J5XeOXw', 'btn-vid4')">
                            <i class="bi bi-music-note-beamed me-1"></i> Boddega - Mi recuerdo, un cigarrillo
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid5" onclick="cambiarVideo('Mago de Oz - Fiesta Pagana', 'Icónico tema musical que combina Folk y Heavy Metal de la destacada banda de rock en español Mago de Oz.', 'violin Folk Metal ES', 'https://www.youtube.com/embed/jdeq6lJXpj0', 'btn-vid5')">
                            <i class="bi bi-music-note-beamed me-1"></i> Mago de Oz - Fiesta Pagana
                        </button>
                    </div>

                    <div class="row g-3">
                        <div class="col-12 col-md-7">
                            <div class="video-responsive border shadow-sm">
                                <iframe id="yt-player" src="https://www.youtube.com/embed/PhkfHrljRiQ" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                            </div>
                        </div>
                        <div class="col-12 col-md-5 d-flex flex-column justify-content-center p-3 bg-body-tertiary rounded-3 border">
                            <span class="badge bg-danger-subtle text-danger align-self-start mb-2" id="vid-tag">🎸 Rock/Metal EC</span>
                            <h6 class="fw-bold mb-1 text-body" id="vid-title">Aztra - El Mañana</h6>
                            <p class="text-muted small mb-0" id="vid-desc">Muestra artística del emblemático tema musical 'El Mañana' interpretado por la icónica banda de rock/metal nacional ecuatoriana Aztra.</p>
                        </div>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #fae8ff; color: #a21caf;"><i class="bi bi-radar fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Localizador Doppler Planetario</h5>
                    </div>
                    <div class="row g-2 align-items-center">
                        <div class="col-12 col-sm-8">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text bg-body-tertiary"><i class="bi bi-pin-map"></i></span>
                                <input type="text" id="pingHost" class="form-control" value="Sector-Sector-Alpha-9">
                                <button class="btn btn-primary" type="button" id="btnPing" onclick="ejecutarPing()">Rastrear Sonda</button>
                            </div>
                        </div>
                        <div class="col-12 col-sm-4">
                            <div id="pingResult" class="small fw-semibold text-muted ps-2" style="display: none;">
                                Latencia: <span id="pingValue" class="text-success">--</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <div class="row mt-4">
            <div class="col-12">
                <div class="card p-4 shadow-sm">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="fw-bold text-secondary mb-0"><i class="bi bi-terminal-dash me-2"></i>Canal de Datos del Deep Space (Logs de IA)</h5>
                        <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('terminal').innerHTML=''"><i class="bi bi-trash3"></i> Limpiar Telemetría</button>
                    </div>
                    <div class="terminal-logs" id="terminal">
                        <span class="log-info">[COSMOS CORE] Inicializando inteligencia artificial de mapeo estelar... OK</span><br>
                        <span class="log-success">[SUCCESS] Enlace cuántico establecido con la estación base terrícola.</span><br>
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
        let modoPanico = false;
        let alarmThreshold = 80;
        let audioCtx = null;

        const htmlElement = document.documentElement;
        const themeIcon = document.getElementById('themeIcon');
        const themeText = document.getElementById('themeText');
        const temaGuardado = localStorage.getItem('theme') || 'light';
        aplicarTema(temaGuardado);

        function cambiarModo() {
            const nuevoTema = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
            aplicarTema(nuevoTema);
            localStorage.setItem('theme', nuevoTema);
        }

        function aplicarTema(tema) {
            htmlElement.setAttribute('data-bs-theme', tema);
            if (tema === 'dark') {
                themeIcon.className = 'bi bi-sun-fill me-2'; themeText.innerText = 'Modo Claro';
            } else {
                themeIcon.className = 'bi bi-moon-stars-fill me-2'; themeText.innerText = 'Modo Oscuro';
            }
        }

        function actualizarReloj() {
            const ahora = new Date();
            document.getElementById('reloj-pc').innerText = SecurityEscape(ahora.toLocaleTimeString('es-ES', { hour12: false }));
            let fecha = ahora.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            document.getElementById('fecha-pc').innerText = "Fecha de la Tierra: " + fecha.charAt(0).toUpperCase() + fecha.slice(1);
        }
        function SecurityEscape(str) { return str.replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
        setInterval(actualizarReloj, 1000); actualizarReloj();

        function playBeep() {
            if (document.getElementById('muteSound').checked) return;
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(580, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.2);
            } catch(e) {}
        }

        function actualizarThresholdTexto(valor) {
            alarmThreshold = parseInt(valor);
            document.getElementById('threshold-val').innerText = valor + '%';
        }

        function cambiarVideo(titulo, descripcion, tag, url, btnId) {
            document.getElementById('yt-player').src = url;
            document.getElementById('vid-title').innerText = titulo;
            document.getElementById('vid-desc').innerText = descripcion;
            document.getElementById('vid-tag').innerText = tag;
            
            document.querySelectorAll('#video-button-group .btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.getElementById(btnId).classList.add('active');

            const term = document.getElementById('terminal');
            term.innerHTML += `<span class="log-training">[${new Date().toLocaleTimeString()}] [AUDIO] Sintonizando canal de audio espacial: ${SecurityEscape(titulo)}... OK</span><br>`;
            term.scrollTop = term.scrollHeight;
        }

        // Simulación de fluctuación espacial (Temperatura del reactor vs Escudos)
        setInterval(() => {
            let cpu, ram;
            const term = document.getElementById('terminal');
            
            if (!modoPanico) {
                cpu = Math.floor(Math.random() * (42 - 15) + 15);
                ram = Math.floor(Math.random() * (85 - 70) + 70); // Los escudos están altos por defecto
                if (Math.random() > 0.8) {
                    const mensajes = ["Ondas gravitacionales estables", "Sonda Voyager enviando paquetes", "No se detectan amenazas alienígenas en el cuadrante"];
                    term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [MONITOR] ${mensajes[Math.floor(Math.random()*mensajes.length)]}.</span><br>`;
                }
            } else {
                cpu = Math.floor(Math.random() * (100 - 92) + 92); // Sube la temperatura críticamente
                ram = Math.floor(Math.random() * (20 - 5) + 5);   // Caen los escudos
                const errores = ["ALERTA EN EL SISTEMA: Tormenta Solar de clase X impactando la nave", "CRITICAL: Brecha en el escudo térmico principal"];
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [ALERT] ${errores[Math.floor(Math.random()*errores.length)]}.</span><br>`;
            }

            document.getElementById('cpu-txt').innerText = cpu + '°C';
            document.getElementById('cpu-bar').style.width = cpu + '%';
            document.getElementById('ram-txt').innerText = ram + '%';
            document.getElementById('ram-bar').style.width = ram + '%';
            
            if(cpu > 80) { document.getElementById('cpu-bar').className = "progress-bar bg-danger"; }
            else { document.getElementById('cpu-bar').className = "progress-bar bg-info"; }

            const alarmCard = document.getElementById('alarm-card');
            const alarmBadge = document.getElementById('alarm-status-badge');
            if (cpu >= alarmThreshold) {
                alarmCard.classList.add('pulse-danger');
                alarmBadge.className = "badge bg-danger animate-pulse";
                alarmBadge.innerText = "¡ALERTA ROJA!";
                playBeep();
            } else {
                alarmCard.classList.remove('pulse-danger');
                alarmBadge.className = "badge bg-secondary";
                alarmBadge.innerText = "Seguro";
            }
            term.scrollTop = term.scrollHeight;
        }, 2500);

        function alternarPanico() {
            modoPanico = document.getElementById('panicSwitch').checked;
            const badge = document.getElementById('status-global-badge');
            const uptime = document.getElementById('uptime-contador');
            const iconBg = document.getElementById('recursos-icon-bg');

            if (modoPanico) {
                badge.className = "badge bg-danger animate-pulse"; badge.innerText = "¡SISTEMA EN RIESGO COLECTIVO!";
                uptime.className = "badge bg-danger-subtle text-danger fw-bold p-2 fs-7"; uptime.innerText = "0 Días Luz (CRÍTICO)";
                iconBg.style.backgroundColor = "#fee2e2"; iconBg.style.color = "#ef4444";
            } else {
                badge.className = "badge bg-success"; badge.innerText = "ESTABLE (ONLINE)";
                uptime.className = "badge bg-success-subtle text-success fw-bold p-2 fs-7"; uptime.innerText = "142 Días Luz";
                iconBg.style.backgroundColor = "#f0fdf4"; iconBg.style.color = "#166534";
            }
        }

        // Secuencia completa del Salto Hyperespacial
        function iniciarDespliegue() {
            const btn = document.getElementById('btnDeploy');
            const box = document.getElementById('deploy-process-box');
            const bar = document.getElementById('deploy-progress-bar');
            const stepTxt = document.getElementById('deploy-step-text');
            const pctTxt = document.getElementById('deploy-pct-text');
            const term = document.getElementById('terminal');

            if (modoPanico) {
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [WARP] Salto denegado. Estabilice los reactores antes de curvar el espacio-tiempo.</span><br>`;
                term.scrollTop = term.scrollHeight;
                alert("¡Salto abortado! La radiación o temperatura del núcleo es extremadamente inestable.");
                return;
            }

            btn.disabled = true;
            box.style.display = "block";
            let progreso = 0;
            
            term.innerHTML += `<span class="log-deploy">[${new Date().toLocaleTimeString()}] [WARP] Iniciando algoritmo de curvatura espacial Alcubierre...</span><br>`;

            let intervalo = setInterval(() => {
                progreso += 5;
                bar.style.width = progreso + "%";
                pctTxt.innerText = progreso + "%";

                if (progreso < 30) {
                    stepTxt.innerText = "Inyectando antimateria...";
                } else if (progreso < 60) {
                    stepTxt.innerText = "Alineando coordenadas galácticas con AWS...";
                    if(progreso === 45) {
                        term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [WARP] Distorsión del espacio detectada con éxito.</span><br>`;
                    }
                } else if (progreso < 90) {
                    stepTxt.innerText = "Abriendo portal de gusano Einstein-Rosen...";
                } else if (progreso < 100) {
                    stepTxt.innerText = "Finalizando salto...";
                } else {
                    clearInterval(intervalo);
                    stepTxt.innerText = "Sonda/Nave enviada con éxito.";
                    btn.disabled = false;
                    term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [SUCCESS] ¡Salto completado! Confirmación de llegada recibida desde Gliese-581g.</span><br>`;
                    term.scrollTop = term.scrollHeight;
                }
                term.scrollTop = term.scrollHeight;
            }, 200);
        }

        // Función del Radar Planetario
        function ejecutarPing() {
            const host = document.getElementById('pingHost').value;
            const btn = document.getElementById('btnPing');
            const resDiv = document.getElementById('pingResult');
            const valSpan = document.getElementById('pingValue');
            const term = document.getElementById('terminal');

            btn.disabled = true;
            resDiv.style.display = "inline-block";
            valSpan.className = "text-warning";
            valSpan.innerText = "Calculando...";

            term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [RADAR] Enviando ráfaga de taquiones hacia ${SecurityEscape(host)}...</span><br>`;
            term.scrollTop = term.scrollHeight;

            setTimeout(() => {
                fetch(`/api/ping?host=${encodeURIComponent(host)}`)
                    .then(r => r.json())
                    .then(data => {
                        btn.disabled = false;
                        if (data.status === "ok") {
                            valSpan.className = "text-success";
                            valSpan.innerText = data.ms;
                            term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [RADAR] Sonda localizada. Eco Doppler retornado en ${data.ms}.</span><br>`;
                        } else {
                            valSpan.className = "text-danger";
                            valSpan.innerText = "PERDIDO";
                            term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [RADAR] Error. Sin eco de respuesta de ${SecurityEscape(host)}. Objeto bloqueado u oculto.</span><br>`;
                        }
                        term.scrollTop = term.scrollHeight;
                    })
                    .catch(() => {
                        btn.disabled = false;
                        valSpan.className = "text-danger";
                        valSpan.innerText = "ERROR";
                    });
            }, 1200);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    year_param = request.args.get('year')
    month_param = request.args.get('month')

    ahora = datetime.now()
    
    try:
        ano_vista = int(year_param) if year_param else ahora.year
        mes_vista = int(month_param) if month_param else ahora.month
        if mes_vista < 1 or mes_vista > 12: raise ValueError
    except ValueError:
        ano_vista = ahora.year
        mes_vista = ahora.month

    # Cálculos de navegación del calendario
    if mes_vista == 1:
        prev_mes = 12
        prev_ano = ano_vista - 1
    else:
        prev_mes = mes_vista - 1
        prev_ano = ano_vista

    if mes_vista == 12:
        next_mes = 1
        next_ano = ano_vista + 1
    else:
        next_mes = mes_vista + 1
        next_ano = ano_vista

    prev_ano_solo = ano_vista - 1
    next_ano_solo = ano_vista + 1

    nombre_mes_vista = MESES_ES.get(mes_vista, "Desconocido")

    # Inyección de eventos espaciales en la cuadrícula de HTML usando calendar
    cal = calendar.Calendar(firstweekday=6) # Domingo como inicio de semana
    semanas = cal.monthdayscalendar(ano_vista, mes_vista)

    cal_html = '<table class="table table-bordered table-sm align-middle mb-0"><thead><tr>'
    for d in ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]:
        cal_html += f'<th class="text-center">{d}</th>'
    cal_html += '</tr></thead><tbody>'

    for semana in semanas:
        cal_html += '<tr>'
        for dia in  semana:
            if dia == 0:
                cal_html += '<td class="nonday">-</td>'
            else:
                clases = []
                # Si el mes y el año coinciden con el de los eventos simulados
                if dia in EVENTOS_ESPACIALES:
                    clases.append("tiene-tarea")
                
                # Resaltar el día de la Tierra actual si coincide en el calendario
                if dia == ahora.day and mes_vista == ahora.month and ano_vista == ahora.year:
                    clases.append("bg-primary-subtle text-primary border border-primary-subtle")

                clase_str = " ".join(clases) if clases else ""
                
                # Al hacer clic llama a un handler JS
                onclick_attr = f'onclick="seleccionarDia({dia})"'
                cal_html += f'<td class="{clase_str}" {onclick_attr} id="celda-dia-{dia}">{dia}</td>'
        cal_html += '</tr>'
    cal_html += '</tbody></table>'

    # Script añadido dinámicamente para enlazar los eventos astronómicos en Frontend
    js_inject = f"""
    <script>
    const EVENTOS_BACKEND = {str(EVENTOS_ESPACIALES)};
    function seleccionarDia(dia) {{
        // Remover estilos de selección previa
        document.querySelectorAll('.table td').forEach(td => td.classList.remove('bg-info-subtle', 'border-info'));
        
        const celda = document.getElementById('celda-dia-' + dia);
        if(celda) celda.classList.add('bg-info-subtle', 'border-info');

        const lista = document.getElementById('lista-tareas');
        lista.innerHTML = '';
        
        if (EVENTOS_BACKEND[dia]) {{
            EVENTOS_BACKEND[dia].forEach(ev => {{
                lista.innerHTML += `<li><i class="bi bi-rocket me-2 text-info"></i><b>${{ev}}</b></li>`;
            }});
        }} else {{
            lista.innerHTML = `<li>No hay anomalías cósmicas ni órbitas programadas para el día ${{dia}}. Todo despejado.</li>`;
        }}
    }}
    </script>
    """
    cal_html += js_inject

    return render_template_string(
        PLANTILLA_HTML,
        estilos_css=ESTILOS_CSS,
        version=VERSION,
        hoy=ahora,
        mes_vista=mes_vista,
        ano_vista=ano_vista,
        nombre_mes_vista=nombre_mes_vista,
        calendario_html=cal_html,
        prev_mes=prev_mes, prev_ano=prev_ano,
        next_mes=next_mes, next_ano=next_ano,
        prev_ano_solo=prev_ano_solo, next_ano_solo=next_ano_solo
    )

@app.route('/api/ping')
def api_ping():
    host = request.args.get('host', '')
    # Sanitización básica del input simulado
    host_clean = re.sub(r'[^a-zA-Z0-9\.\-_]', '', host)
    
    if not host_clean:
        return jsonify({"status": "error"})
        
    # Simulación exitosa o fallo aleatorio
    if random.random() > 0.15:
        ms_aleatorio = f"{random.randint(4, 180)} UA/ms" # Unidades Astronómicas por milisegundo
        return jsonify({"status": "ok", "ms": ms_aleatorio})
    else:
        return jsonify({"status": "fail"})

if __name__ == '__main__':
    # Se ejecuta en modo debug local
    app.run(debug=True)
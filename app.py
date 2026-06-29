from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import calendar
import random
import re

app = Flask(__name__)

VERSION = "2.4.0"  # Incrementamos versión menor por añadir nueva característica/video

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

TAREAS_DEVOPS = {
    5: ["Mantenimiento programado de Base de Datos", "Backup semanal"],
    12: ["Despliegue a Producción v2.4.0"],
    18: ["Auditoría de Seguridad - Parche de contenedores Docker"],
    25: ["Revisión de logs y optimización de índices en AWS"]
}

ESTILOS_CSS = """
body {
    background-color: var(--bs-body-bg);
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    transition: background-color 0.3s, color 0.3s;
}
.gradient-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    color: white;
}
.card {
    border: none;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
    transition: all 0.3s;
}
.btn-nav {
    background-color: var(--bs-tertiary-bg);
    border: 1px solid var(--bs-border-color);
    color: var(--bs-body-color);
    transition: all 0.2s;
}
.btn-nav:hover { background-color: #6366f1; color: white; border-color: #6366f1; }

.btn-hoy {
    background-color: #ecfdf5; color: #059669; border: 1px solid #a7f3d0;
}
[data-bs-theme="dark"] .btn-hoy {
    background-color: #064e3b; color: #34d399; border: 1px solid #047857;
}
.btn-hoy:hover { background-color: #059669; color: white; }

.titulo-mes { font-size: 1.5rem; font-weight: 700; color: #4f46e5; text-transform: capitalize; }
[data-bs-theme="dark"] .titulo-mes { color: #818cf8; }

.table th { color: #94a3b8; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; }
.table td { font-weight: 600; color: var(--bs-body-color); width: 45px; height: 50px; cursor: pointer; border-radius: 8px; position: relative; text-align: center; vertical-align: middle; }
.table td:not(.nonday):hover { background-color: var(--bs-secondary-bg-subtle); }
.nonday { color: #cbd5e1 !important; cursor: default !important; }
[data-bs-theme="dark"] .nonday { color: #475569 !important; }

.tiene-tarea::after {
    content: ''; position: absolute; bottom: 4px; left: 50%; transform: translateX(-50%);
    width: 6px; height: 6px; background-color: #f59e0b; border-radius: 50%;
}

.terminal-logs {
    background-color: #0f172a; font-family: 'Courier New', Courier, monospace; font-size: 0.85rem;
    border-radius: 8px; padding: 15px; max-height: 200px; overflow-y: auto;
}
.log-info { color: #38bdf8; }
.log-success { color: #34d399; }
.log-error { color: #f87171; animation: blinker 1.5s linear infinite; }
.log-alert { color: #fbbf24; font-weight: bold; }
.log-deploy { color: #a855f7; }
.log-training { color: #22d3ee; }

@keyframes blinker { 50% { opacity: 0.5; } }

.btn-theme-toggle {
    background: rgba(255, 255, 255, 0.15); border: none; color: white;
    padding: 8px 12px; border-radius: 50rem; font-weight: 500; transition: all 0.2s;
}
.btn-theme-toggle:hover { background: rgba(255, 255, 255, 0.3); }

.reloj-contenedor { background-color: var(--bs-light-bg-subtle); border: 1px solid var(--bs-border-color-translucent); }

.pulse-danger {
    animation: pulse-bg 1s infinite alternate;
}
@keyframes pulse-bg {
    0% { background-color: rgba(239, 68, 68, 0.1); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
    100% { background-color: rgba(239, 68, 68, 0.25); box-shadow: 0 0 10px 4px rgba(239, 68, 68, 0.2); }
}

.video-responsive {
    position: relative;
    padding-bottom: 56.25%;
    height: 0;
    overflow: hidden;
    border-radius: 12px;
}
.video-responsive iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: none;
}
"""

PLANTILLA_HTML = """
<!DOCTYPE html>
<html lang="es" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Pro Panel - Angelo Vera</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>{{ estilos_css | safe }}</style>
</head>
<body>

    <div class="gradient-header py-4 mb-4 shadow-sm">
        <div class="container d-flex flex-column flex-sm-row justify-content-between align-items-center gap-3">
            <div>
                <h1 class="h3 mb-0 fw-bold"><i class="bi bi-shield-lock me-2 text-info"></i>DevOps Control Center</h1>
                <small class="opacity-75">Estado General: <span id="status-global-badge" class="badge bg-success">ONLINE</span></small>
            </div>
            <div class="d-flex align-items-center flex-wrap justify-content-center gap-3">
                <button class="btn-theme-toggle shadow-sm" id="themeToggler" onclick="cambiarModo()">
                    <i class="bi bi-moon-stars-fill me-2" id="themeIcon"></i><span id="themeText">Modo Oscuro</span>
                </button>
                <span class="badge bg-dark text-info px-3 py-2 rounded-pill border border-secondary shadow-sm fs-7">
                    <i class="bi bi-code-slash me-2"></i>Angelo Vera - 5to A
                </span>
                <span class="badge bg-white text-dark px-3 py-2 rounded-pill fw-semibold shadow-sm">v{{ version }}</span>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row g-4">
            
            <div class="col-12 col-lg-4 d-flex flex-column gap-4">
                
                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #e0e7ff; color: #4f46e5;"><i class="bi bi-clock-history fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Monitor de Tiempo</h5>
                    </div>
                    <div class="rounded-3 p-3 text-center my-2 reloj-contenedor">
                        <h2 class="fw-bold mb-0" id="reloj-pc" style="color: #6366f1; letter-spacing: -1px;">00:00:00</h2>
                        <small class="text-muted fw-semibold" id="fecha-pc">Cargando...</small>
                    </div>
                </div>

                <div class="card p-4 shadow-sm" id="recursos-card">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="recursos-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #e0f2fe; color: #0284c7;"><i class="bi bi-cpu fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Telemetría</h5>
                        </div>
                        <div class="form-check form-switch" title="Simular colapso del sistema">
                            <input class="form-check-input" type="checkbox" id="panicSwitch" onchange="alternarPanico()">
                            <label class="form-check-label text-danger small fw-bold" for="panicSwitch"><i class="bi bi-exclamation-triangle"></i></label>
                        </div>
                    </div>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1"><span>Carga CPU</span><span id="cpu-txt">18%</span></div>
                        <div class="progress" style="height: 8px;"><div id="cpu-bar" class="progress-bar bg-info" style="width: 18%"></div></div>
                    </div>
                    <div class="mb-3">
                        <div class="d-flex justify-content-between small fw-bold mb-1"><span>Uso Memoria RAM</span><span id="ram-txt">42%</span></div>
                        <div class="progress" style="height: 8px;"><div id="ram-bar" class="progress-bar bg-primary" style="width: 42%"></div></div>
                    </div>
                    <hr class="opacity-25">
                    <div class="d-flex justify-content-between align-items-center">
                        <span class="small text-muted fw-semibold">Tiempo Continuo sin Fallos:</span>
                        <span id="uptime-contador" class="badge bg-success-subtle text-success fw-bold p-2 fs-7">142 Días</span>
                    </div>
                </div>

                <div class="card p-4 shadow-sm" id="alarm-card">
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <div class="d-flex align-items-center">
                            <div id="alarm-icon-bg" class="rounded-3 p-2 me-3" style="background-color: #fee2e2; color: #dc2626;"><i class="bi bi-bell fs-4"></i></div>
                            <h5 class="mb-0 fw-bold text-secondary">Umbral de Alarma</h5>
                        </div>
                        <span id="alarm-status-badge" class="badge bg-secondary">Inactiva</span>
                    </div>
                    
                    <label for="cpuThreshold" class="form-label small fw-bold text-muted">Disparar alarma si la CPU supera el:</label>
                    <div class="d-flex align-items-center gap-3 mb-3">
                        <input type="range" class="form-range" id="cpuThreshold" min="50" max="95" value="80" oninput="actualizarThresholdTexto(this.value)">
                        <span id="threshold-val" class="fw-bold text-primary fs-5" style="min-width: 45px;">80%</span>
                    </div>

                    <div class="form-check form-check-inline small">
                        <input class="form-check-input" type="checkbox" id="muteSound" checked>
                        <label class="form-check-label text-muted" for="muteSound"><i class="bi bi-volume-mute"></i> Silenciar pitido sonoro</label>
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
                        <a href="/" class="btn btn-hoy btn-sm fw-bold px-4 shadow-sm"><i class="bi bi-calendar2-check me-1"></i> Ir al Mes Actual</a>
                    </div>

                    <div class="table-responsive">
                        {{ calendario_html | safe }}
                    </div>

                    <div class="mt-3 p-3 bg-body-tertiary rounded-3 border">
                        <h6 class="fw-bold mb-2 text-primary"><i class="bi bi-info-circle me-2"></i>Tareas del Día Seleccionado:</h6>
                        <ul id="lista-tareas" class="mb-0 small text-muted">
                            <li>Haz clic en cualquier día del calendario (los días con marcas naranjas indican mantenimientos programados).</li>
                        </ul>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex flex-column flex-sm-row justify-content-between align-items-start align-items-sm-center gap-2 mb-3">
                        <div class="d-flex align-items-center">
                            <div class="rounded-3 p-2 me-3" style="background-color: #f3e8ff; color: #a855f7;"><i class="bi bi-rocket-takeoff fs-4"></i></div>
                            <div>
                                <h5 class="mb-0 fw-bold text-secondary">Pipeline de Integración Continuo (CI/CD)</h5>
                                <small class="text-muted">Rama activa: <code class="text-purple">main</code></small>
                            </div>
                        </div>
                        <button class="btn btn-purple text-white fw-bold px-3 shadow-sm" style="background-color: #a855f7;" id="btnDeploy" onclick="iniciarDespliegue()">
                            <i class="bi bi-play-fill me-1"></i> Deploy Code
                        </button>
                    </div>

                    <div id="deploy-process-box" class="p-3 bg-body-tertiary rounded-3 border" style="display:none;">
                        <div class="d-flex justify-content-between small fw-bold mb-2">
                            <span id="deploy-step-text" class="text-purple">Preparando...</span>
                            <span id="deploy-pct-text">0%</span>
                        </div>
                        <div class="progress" style="height: 10px;">
                            <div id="deploy-progress-bar" class="progress-bar progress-bar-striped progress-bar-animated bg-purple" style="width: 0%; background-color: #a855f7;"></div>
                        </div>
                    </div>
                </div>

                <div class="card p-4 shadow-sm">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #ffe4e6; color: #f43f5e;"><i class="bi bi-youtube fs-4"></i></div>
                        <div>
                            <h5 class="mb-0 fw-bold text-secondary">Centro de Capacitación & Cultura</h5>
                            <small class="text-muted">Muestra de música y arte nacional e internacional</small>
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
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid5" onclick="cambiarVideo('Mago de Oz - Fiesta Pagana', 'Icónico tema musical que combina Folk y Heavy Metal de la destacada banda de rock en español Mago de Oz.', '🎻 Folk Metal ES', 'https://www.youtube.com/embed/jdeq6lJXpj0', 'btn-vid5')">
                            <i class="bi bi-music-note-beamed me-1"></i> Mago de Oz - Fiesta Pagana
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid6" onclick="cambiarVideo('Saratoga - Si Amaneciera', 'Una de las baladas de Heavy Metal más profundas y aclamadas de la escena española interpretada por Saratoga.', '⚡ Heavy Metal ES', 'https://www.youtube.com/embed/cspyJunYonI', 'btn-vid6')">
                            <i class="bi bi-music-note-beamed me-1"></i> Saratoga - Si Amaneciera
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid7" onclick="cambiarVideo('Kraken - Vestido de Cristal', 'Clásico fundamental del rock progresivo y el hard rock hispanoamericano a cargo de la legendaria banda colombiana Kraken.', '🛡️ Rock Progresivo CO', 'https://www.youtube.com/embed/VRxF8H-x_J0', 'btn-vid7')">
                            <i class="bi bi-music-note-beamed me-1"></i> Kraken - Vestido de Cristal
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid8" onclick="cambiarVideo('Rata Blanca - Mujer Amante', 'Gran himno del Rock clásico y Power Metal latinoamericano, una obra maestra de los argentinos Rata Blanca.', '🦅 Hard Rock AR', 'https://www.youtube.com/embed/IGEskjk2hCo', 'btn-vid8')">
                            <i class="bi bi-music-note-beamed me-1"></i> Rata Blanca - Mujer Amante
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid9" onclick="cambiarVideo('Rata Blanca - Maldita Bruja', 'Gran éxito rítmico extraído del disco El camino del fuego de los argentinos Rata Blanca, con potentes riffs de guitarra.', '⚡ Hard Rock AR', 'https://www.youtube.com/embed/1-iE6tpgYmo', 'btn-vid9')">
                            <i class="bi bi-music-note-beamed me-1"></i> Rata Blanca - Maldita Bruja
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid10" onclick="cambiarVideo('Ángeles del Infierno - Al Otro Lado del Silencio', 'Emotiva y legendaria balada de Heavy Metal clásico directo desde España por Ángeles del Infierno.', '🔥 Heavy Metal ES', 'https://www.youtube.com/embed/51cZsDsVOqc', 'btn-vid10')">
                            <i class="bi bi-music-note-beamed me-1"></i> Ángeles del Infierno - Al Otro Lado
                        </button>
                        <button class="btn btn-outline-danger btn-sm fw-semibold" id="btn-vid11" onclick="cambiarVideo('Moderatto - Mil Demonios', 'Potente y melódica canción de la banda mexicana Moderatto, destacando su enérgico estilo Glam Rock.', '🤘 Glam Rock MX', 'https://www.youtube.com/embed/U1IilAPFpAQ', 'btn-vid11')">
                            <i class="bi bi-music-note-beamed me-1"></i> Moderatto - Mil Demonios
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
                        <div class="rounded-3 p-2 me-3" style="background-color: #fef3c7; color: #d97706;"><i class="bi bi-hdd-network fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Herramientas de Red</h5>
                    </div>
                    <div class="row g-2 align-items-center">
                        <div class="col-12 col-sm-8">
                            <div class="input-group input-group-sm">
                                <span class="input-group-text bg-body-tertiary"><i class="bi bi-globe"></i></span>
                                <input type="text" id="pingHost" class="form-control" value="192.168.1.1">
                                <button class="btn btn-primary" type="button" id="btnPing" onclick="ejecutarPing()">Ping</button>
                            </div>
                        </div>
                        <div class="col-12 col-sm-4">
                            <div id="pingResult" class="small fw-semibold text-muted ps-2" style="display: none;">
                                Rsp: <span id="pingValue" class="text-success">--</span>
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
                        <h5 class="fw-bold text-secondary mb-0"><i class="bi bi-terminal me-2"></i>Consola de Logs en Vivo</h5>
                        <button class="btn btn-outline-secondary btn-sm" onclick="document.getElementById('terminal').innerHTML=''"><i class="bi bi-trash3"></i> Limpiar</button>
                    </div>
                    <div class="terminal-logs" id="terminal">
                        <span class="log-info">[SYSTEM] Inicializando entorno DevOps... OK</span><br>
                        <span class="log-success">[SUCCESS] Kernel mapeado y enlazado a Flask core correctamente.</span><br>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <footer class="container text-center text-muted small my-5 py-3 border-top opacity-50">
        Infraestructura DevOps de Prácticas &bull; Angelo Vera &bull; 2026
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
            document.getElementById('fecha-pc').innerText = fecha.charAt(0).toUpperCase() + fecha.slice(1);
        }
        function SecurityEscape(str) { return str.replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
        setInterval(actualizarReloj, 1000); actualizarReloj();

        function playBeep() {
            if (document.getElementById('muteSound').checked) return;
            try {
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                let osc = audioCtx.createOscillator();
                let gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.15);
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
            term.innerHTML += `<span class="log-training">[${new Date().toLocaleTimeString()}] [TRAINING] Cargando contenido multimedia: ${SecurityEscape(titulo)}... OK</span><br>`;
            term.scrollTop = term.scrollHeight;
        }

        setInterval(() => {
            let cpu, ram;
            const term = document.getElementById('terminal');
            
            if (!modoPanico) {
                cpu = Math.floor(Math.random() * (45 - 12) + 12);
                ram = Math.floor(Math.random() * (60 - 35) + 35);
                if (Math.random() > 0.82) {
                    const mensajes = ["Sincronización NTP Exitosa", "Estructura de Red saludable", "Conexiones balanceadas"];
                    term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [INFO] ${mensajes[Math.floor(Math.random()*mensajes.length)]}.</span><br>`;
                }
            } else {
                cpu = Math.floor(Math.random() * (100 - 94) + 94);
                ram = Math.floor(Math.random() * (99 - 91) + 91);
                const errores = ["CRITICAL: DB Connection Timeout!", "ERROR: Puerto 443 saturado - DDOS detectado"];
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [CRITICAL] ${errores[Math.floor(Math.random()*errores.length)]}.</span><br>`;
            }

            document.getElementById('cpu-txt').innerText = cpu + '%';
            document.getElementById('cpu-bar').style.width = cpu + '%';
            document.getElementById('ram-txt').innerText = ram + '%';
            document.getElementById('ram-bar').style.width = ram + '%';
            
            if(cpu > 85) { document.getElementById('cpu-bar').className = "progress-bar bg-danger"; }
            else { document.getElementById('cpu-bar').className = "progress-bar bg-info"; }

            const alarmCard = document.getElementById('alarm-card');
            const alarmBadge = document.getElementById('alarm-status-badge');
            if (cpu >= alarmThreshold) {
                alarmCard.classList.add('pulse-danger');
                alarmBadge.className = "badge bg-danger animate-pulse";
                alarmBadge.innerText = "¡DISPARADA!";
                playBeep();
            } else {
                alarmCard.classList.remove('pulse-danger');
                alarmBadge.className = "badge bg-secondary";
                alarmBadge.innerText = "Inactiva";
            }
            term.scrollTop = term.scrollHeight;
        }, 2500);

        function alternarPanico() {
            modoPanico = document.getElementById('panicSwitch').checked;
            const badge = document.getElementById('status-global-badge');
            const uptime = document.getElementById('uptime-contador');
            const iconBg = document.getElementById('recursos-icon-bg');

            if (modoPanico) {
                badge.className = "badge bg-danger animate-pulse"; badge.innerText = "CRITICAL FAILURE";
                uptime.className = "badge bg-danger-subtle text-danger fw-bold p-2 fs-7"; uptime.innerText = "0 Días (CAÍDO)";
                iconBg.style.backgroundColor = "#fee2e2"; iconBg.style.color = "#ef4444";
            } else {
                badge.className = "badge bg-success"; badge.innerText = "ONLINE";
                uptime.className = "badge bg-success-subtle text-success fw-bold p-2 fs-7"; uptime.innerText = "142 Días";
                iconBg.style.backgroundColor = "#e0f2fe"; iconBg.style.color = "#0284c7";
            }
        }

        // CONTINUACIÓN DE LA FUNCIÓN PIPELINE CI/CD COMPLETADA
        function iniciarDespliegue() {
            const btn = document.getElementById('btnDeploy');
            const box = document.getElementById('deploy-process-box');
            const bar = document.getElementById('deploy-progress-bar');
            const stepTxt = document.getElementById('deploy-step-text');
            const pctTxt = document.getElementById('deploy-pct-text');
            const term = document.getElementById('terminal');

            if (modoPanico) {
                term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [DEPLOY] [ERROR] Despliegue cancelado automáticamente. En el servidor actual se reportan fallas críticas.</span><br>`;
                term.scrollTop = term.scrollHeight;
                alert("¡Error en el Pipeline! No se puede actualizar el sistema mientras el servidor esté caído.");
                return;
            }

            btn.disabled = true;
            box.style.display = "block";
            let progreso = 0;
            
            term.innerHTML += `<span class="log-deploy">[${new Date().toLocaleTimeString()}] [CI/CD] Triggering new production deployment (commit #A7X92)...</span><br>`;

            let intervalo = setInterval(() => {
                progreso += 5;
                bar.style.width = progreso + "%";
                pctTxt.innerText = progreso + "%";

                if (progreso < 35) {
                    stepTxt.innerText = "🔨 Stage 1: Compilando paquetes de código...";
                } else if (progreso < 70) {
                    stepTxt.innerText = "🧪 Stage 2: Corriendo Pruebas Unitarias e Integración...";
                } else if (progreso < 95) {
                    stepTxt.innerText = "📦 Stage 3: Generando Docker Image & Push a Registry...";
                } else {
                    stepTxt.innerText = "🚀 Stage 4: Despliegue Exitoso en Cluster K8s!";
                }

                if (progreso >= 100) {
                    clearInterval(intervalo);
                    setTimeout(() => {
                        btn.disabled = false;
                        box.style.display = "none";
                        bar.style.width = "0%";
                        term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [SUCCESS] Deployment Pipeline finalizado con éxito (v${VERSION}).</span><br>`;
                        term.scrollTop = term.scrollHeight;
                    }, 1000);
                }
            }, 2500 / 20);
        }

        // FUNCIÓN DINÁMICA DE INTERFAZ PARA EJECUTAR PING
        function ejecutarPing() {
            const host = document.getElementById('pingHost').value;
            const resBox = document.getElementById('pingResult');
            const resVal = document.getElementById('pingValue');
            const btn = document.getElementById('btnPing');
            const term = document.getElementById('terminal');

            if(!host.trim()) return;

            btn.disabled = true;
            resBox.style.display = "inline-block";
            resVal.className = "text-warning";
            resVal.innerText = "Procesando...";

            fetch(`/api/ping?host=${encodeURIComponent(host)}`)
                .then(r => r.json())
                .then(data => {
                    btn.disabled = false;
                    if(data.status === "success") {
                        resVal.className = "text-success";
                        resVal.innerText = data.latencia;
                        term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [NET] PING a ${SecurityEscape(host)} exitoso: ${data.latencia}</span><br>`;
                    } else {
                        resVal.className = "text-danger";
                        resVal.innerText = "Error";
                        term.innerHTML += `<span class="log-error">[${new Date().toLocaleTimeString()}] [NET] PING a ${SecurityEscape(host)} fallido o inválido.</span><br>`;
                    }
                    term.scrollTop = term.scrollHeight;
                })
                .catch(() => {
                    btn.disabled = false;
                    resVal.className = "text-danger";
                    resVal.innerText = "Timeout";
                });
        }

        // ESCUCHA DE CLICS EN EL CALENDARIO PARA MOSTRAR TAREAS
        document.addEventListener('DOMContentLoaded', () => {
            const cCard = document.getElementById('calendar-card');
            const viewMonth = cCard.getAttribute('data-view-month');
            const viewYear = cCard.getAttribute('data-view-year');

            document.querySelectorAll('.table td:not(.nonday)').forEach(td => {
                td.addEventListener('click', () => {
                    const dia = td.innerText.trim().split('\\n')[0];
                    fetch(`/api/tareas?year=${viewYear}&month=${viewMonth}&day=${dia}`)
                        .then(r => r.json())
                        .then(data => {
                            const lista = document.getElementById('lista-tareas');
                            lista.innerHTML = "";
                            if(data.tareas && data.tareas.length > 0) {
                                data.tareas.forEach(t => {
                                    lista.innerHTML += `<li><strong class="text-warning">[Mantenimiento]</strong> ${SecurityEscape(t)}</li>`;
                                });
                            } else {
                                lista.innerHTML = `<li>No hay tareas críticas programadas para el día ${dia} de ${SecurityEscape(data.nombre_mes)}.</li>`;
                            }
                        });
                });
            });
        });
    </script>
</body>
</html>
"""

class CustomHTMLCalendar(calendar.HTMLCalendar):
    def __init__(self, tareas, hoy, mes_v, ano_v):
        super().__init__(calendar.MONDAY)
        self.tareas = tareas
        self.hoy = hoy
        self.mes_v = mes_v
        self.ano_v = ano_v

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="nonday">&nbsp;</td>'
        
        clases = []
        # Comprobar si el día de la cuadrícula renderizada coincide con el día de hoy real
        if day == self.hoy.day and self.mes_v == self.hoy.month and self.ano_v == self.hoy.year:
            clases.append("bg-success-subtle text-success border border-success-subtle rounded-3")
        
        if day in self.tareas:
            clases.append("tiene-tarea")
            
        clase_str = " ".join(clases) if clases else ""
        return f'<td class="{clase_str}">{day}</td>'

    def formatmonthtable(self, theyear, themonth, withyear=True):
        v = []
        a = v.append
        a('<table class="table table-bordered table-sm align-middle mb-0">')
        a('\\n')
        a(self.formatweekheader())
        a('\\n')
        for week in self.monthdays2calendar(theyear, themonth):
            a(self.formatweek(week))
            a('\\n')
        a('</table>')
        a('\\n')
        return ''.join(v)


@app.route('/')
def index():
    hoy = datetime.now()
    
    # Manejo dinámico de navegación de fechas mediante query strings
    ano_vista = request.args.get('year', default=hoy.year, type=int)
    mes_vista = request.args.get('month', default=hoy.month, type=int)
    
    if mes_vista < 1:
        mes_vista = 12
        ano_vista -= 1
    elif mes_vista > 12:
        mes_vista = 1
        ano_vista += 1

    # Parámetros para los botones de navegación
    prev_mes = mes_vista - 1
    prev_ano = ano_vista
    if prev_mes < 1:
        prev_mes = 12
        prev_ano -= 1
        
    next_mes = mes_vista + 1
    next_ano = ano_vista
    if next_mes > 12:
        next_mes = 1
        next_ano += 1

    nombre_mes_vista = MESES_ES.get(mes_vista, "Desconocido")
    
    # Instanciar calendario personalizado pasándole las tareas mapeadas
    cal_obj = CustomHTMLCalendar(TAREAS_DEVOPS if mes_vista == 6 else {}, hoy, mes_vista, ano_vista)
    calendario_html = cal_obj.formatmonthtable(ano_vista, mes_vista)

    return render_template_string(
        PLANTILLA_HTML,
        estilos_css=ESTILOS_CSS,
        version=VERSION,
        calendario_html=calendario_html,
        nombre_mes_vista=nombre_mes_vista,
        ano_vista=ano_vista,
        mes_vista=mes_vista,
        hoy=hoy,
        prev_mes=prev_mes,
        prev_ano=prev_ano,
        next_mes=next_mes,
        next_ano=next_ano,
        prev_ano_solo=ano_vista - 1,
        next_ano_solo=ano_vista + 1
    )


@app.route('/api/tareas')
def api_tareas():
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    day = request.args.get('day', type=int)
    
    # Simulación de backend: Solo cargamos tareas fijas si visualizan junio (mes 6)
    tareas = []
    if month == 6 and day in TAREAS_DEVOPS:
        tareas = TAREAS_DEVOPS[day]
        
    return jsonify({
        "day": day,
        "month": month,
        "nombre_mes": MESES_ES.get(month, "este mes"),
        "tareas": tareas
    })


@app.route('/api/ping')
def api_ping():
    host = request.args.get('host', default='')
    # Sanitizar de forma básica la entrada para simular buenas prácticas DevOps
    if not host or not re.match(r"^[a-zA-Z0-9.-]+$", host):
        return jsonify({"status": "error", "message": "Host inválido"}), 400
        
    # Simular una respuesta de latencia de red de infraestructura
    latencia_simulada = f"{random.randint(4, 45)} ms"
    return jsonify({
        "status": "success",
        "host": host,
        "latencia": latencia_simulada
    })


if __name__ == '__main__':
    # host='0.0.0.0' expone la app de manera correcta para contenedores Docker
    app.run(debug=True, host='0.0.0.0', port=5000)
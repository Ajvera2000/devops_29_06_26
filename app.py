from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import calendar
import re

app = Flask(__name__)

VERSION = "5.1.0"  # Versión de la IA de navegación cuántica

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

# Eventos Astronómicos / Órbitas de Misiones
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
            
            <div class="col-12 col-lg-4">
                <div class="card p-4 shadow-sm h-100 justify-content-center">
                    <div class="d-flex align-items-center mb-3">
                        <div class="rounded-3 p-2 me-3" style="background-color: #e0f2fe; color: #0369a1;"><i class="bi bi-hourglass-split fs-4"></i></div>
                        <h5 class="mb-0 fw-bold text-secondary">Tiempo Estelar de Misión</h5>
                    </div>
                    <div class="rounded-3 p-3 text-center my-2 reloj-contenedor">
                        <h2 class="fw-bold mb-0" id="reloj-pc" style="color: #3b82f6; letter-spacing: -1px;">00:00:00</h2>
                        <small class="text-muted fw-semibold" id="fecha-pc">Cargando fecha estelar...</small>
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
        const htmlElement = document.documentElement;
        const themeIcon = document.getElementById('themeIcon');
        const themeText = document.getElementById('themeText');

        function cambiarModo() {
            const nuevoTema = htmlElement.getAttribute('data-bs-theme') === 'light' ? 'dark' : 'light';
            aplicarTema(nuevoTema);
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
            document.getElementById('reloj-pc').innerText = ahora.toLocaleTimeString('es-ES', { hour12: false });
            let fecha = ahora.toLocaleDateString('es-ES', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
            document.getElementById('fecha-pc').innerText = "Fecha de la Tierra: " + fecha.charAt(0).toUpperCase() + fecha.slice(1);
        }
        setInterval(actualizarReloj, 1000); actualizarReloj();

        // Carga dinámica de Eventos Espaciales mediante la API interna
        function verTareas(dia, mes, ano) {
            const term = document.getElementById('terminal');
            term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [TELEMETRÍA] Consultando coordenadas orbitales para el día ${dia}/${mes}/${ano}...</span><br>`;
            
            fetch(`/api/eventos?day=${dia}`)
                .then(res => res.json())
                .then(data => {
                    const lista = document.getElementById('lista-tareas');
                    lista.innerHTML = "";
                    if(data.eventos.length === 0) {
                        lista.innerHTML = "<li>No hay misiones programadas para esta fecha estelar.</li>";
                        term.innerHTML += `<span class="log-info">[${new Date().toLocaleTimeString()}] [MONITOR] Cuadrante despejado el día ${dia}.</span><br>`;
                    } else {
                        data.eventos.forEach(evt => {
                            lista.innerHTML += `<li class="fw-bold text-info">${evt}</li>`;
                            term.innerHTML += `<span class="log-success">[${new Date().toLocaleTimeString()}] [EVENTO] Detectado: ${evt}</span><br>`;
                        });
                    }
                    term.scrollTop = term.scrollHeight;
                });
        }
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
        if day == 0:
            return '<td class="nonday">&nbsp;</td>'
        
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
    
    if mes_vista < 1 or mes_vista > 12:
        mes_vista = hoy.month

    nombre_mes_vista = MESES_ES[mes_vista]

    # Lógica de navegación de meses y años
    prev_mes = mes_vista - 1 if mes_vista > 1 else 12
    prev_ano = ano_vista if mes_vista > 1 else ano_vista - 1
    next_mes = mes_vista + 1 if mes_vista < 12 else 1
    next_ano = ano_vista if mes_vista < 12 else ano_vista + 1

    prev_ano_solo = ano_vista - 1
    next_ano_solo = ano_vista + 1

    # Inyectar eventos solo si coincide con el mes de Mayo para demostración
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
        prev_ano_solo=prev_ano_solo,
        next_ano_solo=next_ano_solo
    )

@app.route('/api/eventos')
def api_eventos():
    day = request.args.get('day', default=0, type=int)
    # Simula la obtención de eventos del diccionario estelar
    eventos = EVENTOS_ESPACIALES.get(day, [])
    return jsonify({"day": day, "eventos": eventos})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
UI_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Clinical Architect | Precision Curator</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"/>
    <style>
        :root {
            --primary: #00d2ff;
            --secondary: #3a7bd5;
            --accent: #00ff88;
            --danger: #ff4b2b;
            --sidebar-bg: rgba(10, 20, 30, 0.95);
            --glass: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.05);
            --text-main: #f8fafc;
            --text-dim: #94a3b8;
            --bg-mesh: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
                      radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
                      radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
            
            --radius-md: 12px;
            --radius-xl: 24px;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background-color: #020617;
            background-image: var(--bg-mesh);
            background-attachment: fixed;
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            -webkit-font-smoothing: antialiased;
            display: flex;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* --- Sidebar Navigation (The Deep Space) --- */
        .sidebar {
            width: 280px;
            background: var(--sidebar-bg);
            backdrop-filter: blur(30px);
            border-right: 1px solid var(--glass-border);
            display: flex;
            flex-direction: column;
            padding: 40px 24px;
            height: 100vh;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 60px;
        }

        .logo-icon {
            width: 38px;
            height: 38px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 1.1rem;
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.3);
        }

        .logo-text h2 {
            font-size: 1.2rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-label {
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #475569;
            margin-bottom: 24px;
            display: block;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px;
            border-radius: var(--radius-md);
            color: var(--text-dim);
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 5px;
        }

        .nav-item:hover {
            color: #fff;
            background: rgba(255,255,255,0.05);
            transform: translateX(5px);
        }

        .system-status {
            margin-top: auto;
            background: rgba(255,255,255,0.02);
            padding: 24px;
            border-radius: var(--radius-xl);
            border: 1px solid var(--glass-border);
        }

        .status-pulse {
            width: 8px;
            height: 8px;
            background: var(--accent);
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            box-shadow: 0 0 10px var(--accent);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.7; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.7; }
        }

        /* --- Main Workspace (Clinical Ether) --- */
        .workspace {
            flex: 1;
            padding: 40px 60px;
            max-width: calc(100vw - 280px);
            margin: 0;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }

        header {
            margin-bottom: 40px;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 600;
            letter-spacing: -0.02em;
            margin-bottom: 10px;
            background: linear-gradient(to bottom, #fff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            color: var(--text-dim);
            font-size: 1.1rem;
            max-width: 700px;
            line-height: 1.6;
        }

        /* --- High-End AI Curator Bar --- */
        .input-curator {
            position: relative;
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(20px);
            border-radius: var(--radius-xl);
            padding: 8px;
            display: flex;
            align-items: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            margin-bottom: 60px;
            border: 1px solid rgba(255,255,255,0.08);
            transition: all 0.3s ease;
            width: 100%;
        }

        .input-curator:focus-within {
            border-color: var(--primary);
            box-shadow: 0 20px 50px rgba(0, 210, 255, 0.15);
        }

        .clinical-input {
            flex: 1;
            background: transparent;
            border: none;
            padding: 18px 30px;
            font-size: 1.2rem;
            font-family: 'Inter', sans-serif;
            color: #fff;
            outline: none;
        }

        .clinical-input::placeholder { color: #475569; }

        .btn-analyze {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #fff;
            border: none;
            padding: 14px 40px;
            border-radius: 16px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(0, 210, 255, 0.2);
        }

        .btn-analyze:hover {
            transform: translateY(-2px);
            filter: brightness(1.1);
            box-shadow: 0 10px 25px rgba(0, 210, 255, 0.3);
        }

        /* --- Analysis Output Layer --- */
        .intelligence-output {
            display: none;
            flex-direction: column;
            gap: 40px;
        }

        .glass-card {
            background: var(--glass);
            backdrop-filter: blur(15px);
            padding: 40px;
            border-radius: var(--radius-xl);
            border: 1px solid var(--glass-border);
            position: relative;
            overflow: hidden;
        }

        .glass-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: linear-gradient(to bottom, var(--primary), transparent);
        }

        .section-label {
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            color: var(--primary);
            margin-bottom: 20px;
            display: block;
        }

        #analysis-text {
            font-size: 1.35rem;
            line-height: 1.6;
            color: #fff;
            margin-bottom: 35px;
            font-weight: 400;
        }

        /* SQL Surgical Precision */
        .sql-architect {
            background: rgba(0,0,0,0.4);
            padding: 25px;
            border-radius: 16px;
            color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.95rem;
            line-height: 1.6;
            position: relative;
            border: 1px solid rgba(0, 255, 136, 0.1);
        }

        .copy-sql {
            position: absolute;
            top: 15px;
            right: 15px;
            background: rgba(255,255,255,0.05);
            color: var(--text-dim);
            border: none;
            padding: 5px 12px;
            font-size: 0.7rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .copy-sql:hover { background: rgba(255,255,255,0.1); color: #fff; }

        /* Grid Architecture */
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 30px;
            align-items: start;
            width: 100%;
        }

        .grid-panel {
            background: var(--glass);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: var(--radius-xl);
            border: 1px solid var(--glass-border);
            min-width: 0; /* Critical: Prevent grid blowout */
        }

        /* Tabular Precision */
        .table-wrap {
            max-height: 500px;
            overflow: auto;
            border-radius: 12px;
            background: rgba(0,0,0,0.2);
            scrollbar-width: thin;
            scrollbar-color: var(--primary) transparent;
        }

        .table-wrap::-webkit-scrollbar { width: 6px; }
        .table-wrap::-webkit-scrollbar-thumb { background: var(--primary); border-radius: 10px; }

        table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }

        th {
            text-align: left;
            padding: 15px 20px;
            color: var(--text-dim);
            font-weight: 600;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            font-size: 0.8rem;
            text-transform: uppercase;
        }

        td {
            padding: 14px 20px;
            color: #fff;
            border-bottom: 1px solid rgba(255,255,255,0.02);
        }

        tr:hover td {
            background: rgba(255,255,255,0.03);
        }

        /* --- Special Effects --- */
        .loader {
            display: none;
            position: fixed;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            z-index: 1000;
        }

        .spinner {
            width: 60px; height: 60px;
            border: 3px solid rgba(0, 210, 255, 0.1);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            animation: spin 1s cubic-bezier(0.4, 0, 0.2, 1) infinite;
            filter: drop-shadow(0 0 10px var(--primary));
        }

        @keyframes spin { 100% { transform: rotate(360deg); } }

        /* Mobile Scale */
        @media (max-width: 1200px) {
            .data-grid { grid-template-columns: 1fr; }
            .sidebar { width: 80px; padding: 40px 15px; }
            .sidebar .logo-text, .sidebar .nav-label, .sidebar .nav-item span, .sidebar .system-status { display: none; }
            .sidebar .logo-area { justify-content: center; margin-bottom: 40px; }
            .workspace { padding: 40px 30px; }
        }
    </style>
</head>
<body>
    <aside class="sidebar">
        <div class="logo-area">
            <div class="logo-icon"><i class="fas fa-microscope"></i></div>
            <div class="logo-text">
                <h2>The Clinical Architect</h2>
            </div>
        </div>

        <nav style="flex: 1;">
            <span class="nav-label">Enterprise Data</span>
            <div class="nav-item"><i class="fas fa-tachometer-alt"></i> <span>Pulse Dashboard</span></div>
            <div class="nav-item"><i class="fas fa-stethoscope"></i> <span>Clinical Lab</span></div>
            <div class="nav-item"><i class="fas fa-users"></i> <span>Provider Hub</span></div>
        </nav>

        <div class="system-status">
            <div style="font-size: 0.85rem; font-weight: 600; margin-bottom: 6px; color: #fff;">
                <span class="status-pulse"></span> Logic Active
            </div>
            <div style="font-size: 0.7rem; color: var(--text-dim);">Engine: Vanna 2.5 Multi-Agent</div>
        </div>
    </aside>

    <main class="workspace">
        <header>
            <h1 class="animate__animated animate__fadeInDown">Intelligence Discovery</h1>
            <p class="subtitle animate__animated animate__fadeInUp">Transforming multi-year clinical complexities into precise, surgical-grade insights.</p>
        </header>

        <div class="input-curator animate__animated animate__fadeInUp">
            <input type="text" id="question" class="clinical-input" placeholder="Query the clinical architecture (e.g., 'Historical revenue trends')...">
            <button class="btn-analyze" onclick="askQuestion()">
                <i class="fas fa-bolt"></i> Analyze Insight
            </button>
        </div>

        <div id="loader" class="loader"><div class="spinner"></div></div>

        <section id="output" class="intelligence-output">
            <!-- Insight Layer -->
            <div class="glass-card animate__animated animate__fadeInUp">
                <span class="section-label">Medical Inference</span>
                <div id="analysis-text"></div>
                
                <div class="sql-architect">
                    <button class="copy-sql" onclick="copySql()">Copy SQL</button>
                    <code id="sql-display"></code>
                </div>
            </div>

            <!-- Evidence Layer -->
            <div class="data-grid">
                <div class="grid-panel animate__animated animate__fadeInLeft">
                    <span class="section-label">Tabular Evidence</span>
                    <div class="table-wrap" id="table-box"></div>
                </div>
                <div id="visual-section" class="grid-panel animate__animated animate__fadeInRight">
                    <span class="section-label">Visual Perspective</span>
                    <div id="chart-box" style="width: 100%; min-height: 480px;"></div>
                </div>
            </div>
        </section>
    </main>

    <script>
        async function askQuestion() {
            const question = document.getElementById('question').value;
            if (!question) return;

            const loader = document.getElementById('loader');
            const output = document.getElementById('output');
            
            loader.style.display = 'block';
            output.style.display = 'none';
            
            // Step 15: Structural Reset - Hide Visual section completely until new data arrives
            document.getElementById('table-box').innerHTML = "";
            const visualSection = document.getElementById('visual-section');
            const chartBox = document.getElementById('chart-box');
            
            visualSection.style.display = 'none'; // Hide the entire panel
            if (window.Plotly) Plotly.purge('chart-box'); // Memory-safe purge
            chartBox.innerHTML = "";
            
            document.getElementById('sql-display').innerText = "";
            document.getElementById('analysis-text').innerText = "Analyzing Clinical Intelligence...";

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });

                const data = await response.json();
                loader.style.display = 'none';
                output.style.display = 'flex';

                // Update Text Summary
                document.getElementById('analysis-text').innerText = data.message;
                
                // Update SQL
                document.getElementById('sql-display').innerText = data.sql_query || "Direct Engine Execution";

                // Update Table
                if (data.rows && data.rows.length > 0) {
                    let tableHtml = '<table><thead><tr>';
                    data.columns.forEach(col => tableHtml += `<th>${col}</th>`);
                    tableHtml += '</tr></thead><tbody>';
                    data.rows.forEach(row => {
                        tableHtml += '<tr>';
                        row.forEach(cell => tableHtml += `<td>${cell}</td>`);
                        tableHtml += '</tr>';
                    });
                    tableHtml += '</tbody></table>';
                    document.getElementById('table-box').innerHTML = tableHtml;
                }

                // Render High-Resolution Chart (Plotly)
                if (data.chart) {
                    visualSection.style.display = 'block'; // Show the structural panel
                    const figure = (typeof data.chart === 'string') ? JSON.parse(data.chart) : data.chart;
                    
                    figure.layout = figure.layout || {};
                    figure.layout.paper_bgcolor = 'rgba(0,0,0,0)';
                    figure.layout.plot_bgcolor = 'rgba(0,0,0,0)';
                    figure.layout.font = { color: '#f8fafc', family: 'Inter', size: 12 };
                    figure.layout.margin = { t: 40, r: 40, b: 60, l: 60 };
                    
                    if (figure.data) {
                        figure.data.forEach(trace => {
                            trace.marker = trace.marker || {};
                            if (!trace.marker.color && trace.type === 'bar') {
                                trace.marker.color = '#00d2ff';
                            }
                        });
                    }

                    Plotly.newPlot('chart-box', figure.data, figure.layout, {
                        responsive: true, 
                        displayModeBar: false
                    });
                }

            } catch (err) {
                loader.style.display = 'none';
                alert("Clinical synchronization failed. Reconnecting to Core...");
            }
        }

        function copySql() {
            const sql = document.getElementById('sql-display').innerText;
            navigator.clipboard.writeText(sql);
            alert("Surgical Logic Copied.");
        }

        document.getElementById('question').addEventListener('keypress', function (e) {
            if (e.key === 'Enter') askQuestion();
        });
    </script>
</body>
</html>
"""

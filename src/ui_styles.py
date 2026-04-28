from datetime import datetime

def get_custom_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
        
        :root {
            --primary: #6366f1;
            --secondary: #06b6d4;
            --accent: #8b5cf6;
            --bg: #0f172a;
            --sidebar-bg: #0b0f1a;
            --card-bg: rgba(30, 41, 59, 0.4);
        }

        /* Neural Pulse Background */
        .stApp {
            background: #0f172a;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 0% 100%, rgba(236, 72, 153, 0.15) 0px, transparent 50%),
                linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 100% 100%, 100% 100%, 100% 100%, 40px 40px, 40px 40px;
            color: #f8fafc;
            overflow-x: hidden;
        }

        /* Floating Glass Orbs */
        .stApp::before {
            content: "";
            position: fixed;
            top: -10%; left: -10%;
            width: 40%; height: 40%;
            background: radial-gradient(circle, rgba(99, 102, 241, 0.1) 0%, transparent 70%);
            animation: drift 25s infinite alternate ease-in-out;
            z-index: -1;
        }

        .stApp::after {
            content: "";
            position: fixed;
            bottom: -10%; right: -10%;
            width: 50%; height: 50%;
            background: radial-gradient(circle, rgba(6, 182, 212, 0.1) 0%, transparent 70%);
            animation: drift 30s infinite alternate-reverse ease-in-out;
            z-index: -1;
        }

        @keyframes drift {
            from { transform: translate(0, 0) rotate(0deg); }
            to { transform: translate(20%, 15%) rotate(20deg); }
        }

        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

        /* Cyberpunk Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: rgba(11, 15, 26, 0.5); }
        ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, var(--primary), var(--secondary)); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

        /* Glassmorphism Cards */
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 28px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, border 0.3s ease;
            animation: fadeIn 0.8s ease-out;
            position: relative;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Scanline Card Effect */
        .glass-card::after {
            content: "";
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 4px, 3px 100%;
            pointer-events: none;
            opacity: 0.1;
        }

        .main-header {
            font-size: 5.5rem;
            font-weight: 800;
            letter-spacing: -0.06em;
            color: #fff;
            text-shadow: 0 0 10px rgba(99, 102, 241, 0.8), 0 0 20px rgba(99, 102, 241, 0.4);
            margin-bottom: 5px;
            position: relative;
            animation: titleFloat 4s infinite ease-in-out;
        }
        @keyframes titleFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        /* Top Neural Link Bar */
        .top-nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 32px;
            background: rgba(11, 15, 26, 0.6);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 30px;
            font-size: 0.6rem;
            letter-spacing: 0.12em;
            color: #94a3b8;
        }
        .status-dot { width: 5px; height: 5px; background: #10b981; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #10b981; }

        /* Sidebar Modular Sections with Neon Animation */
        .sidebar-section {
            background: rgba(11, 15, 26, 0.6);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            position: relative;
            overflow: hidden;
            transition: all 0.4s ease;
            animation: borderPulse 4s infinite ease-in-out;
        }
        @keyframes borderPulse {
            0% { border-color: rgba(99, 102, 241, 0.2); }
            50% { border-color: var(--secondary); }
            100% { border-color: rgba(99, 102, 241, 0.2); }
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b0f1a 0%, #1e1b4b 50%, #0f172a 100%) !important;
            background-size: 100% 200%;
            animation: gradientMove 10s infinite alternate linear;
        }
        @keyframes gradientMove {
            0% { background-position: 0% 0%; }
            100% { background-position: 0% 100%; }
        }

        .skill-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.7rem;
            font-weight: 600;
            margin: 4px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .matched-badge { background: rgba(16, 185, 129, 0.1); color: #10b981; border-color: rgba(16, 185, 129, 0.2); }
        .gap-critical { background: rgba(239, 68, 68, 0.1); color: #ef4444; border-color: rgba(239, 68, 68, 0.2); }
        .gap-partial { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border-color: rgba(245, 158, 11, 0.2); }
        .soft-badge { background: rgba(99, 102, 241, 0.1); color: #a5b4fc; }

        .radial-score {
            width: 100px; height: 100px;
            border-radius: 50%;
            background: conic-gradient(var(--primary) var(--percentage), rgba(255,255,255,0.05) 0);
            display: flex; align-items: center; justify-content: center;
            position: relative;
        }
        .radial-score::before {
            content: "";
            position: absolute;
            width: 85px; height: 85px;
            background: #0f172a;
            border-radius: 50%;
        }
        .score-text { position: relative; font-weight: 800; font-size: 1.2rem; color: #fff; }

        .verdict-tag { padding: 4px 12px; border-radius: 8px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; }
        .verdict-high { background: #10b981; color: #fff; }
        .verdict-med { background: #f59e0b; color: #fff; }
        .verdict-low { background: #ef4444; color: #fff; }

        .interview-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 4px solid var(--primary);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .hint-box { font-size: 0.8rem; color: #10b981; margin-top: 10px; font-weight: 600; }
        .warning-box { font-size: 0.8rem; color: #ef4444; margin-top: 5px; font-weight: 600; }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """

def get_top_nav():
    return f"""
    <div class="top-nav">
        <div><span class="status-dot"></span>NEURAL LINK ACTIVE • PLATINUM ENGINE v3.2.0</div>
        <div>LATENCY: 18ms • LOAD: 0.12 • CORE: SBERT-MINILM • {datetime.now().strftime('%H:%M:%S')}</div>
    </div>
    """

import streamlit as st
import streamlit.components.v1 as components

def render_neural_canvas():
    components.html("""
    <canvas id="neuralCanvas" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; opacity: 0.3;"></canvas>
    <script>
    const canvas = document.getElementById('neuralCanvas');
    const ctx = canvas.getContext('2d');
    let particles = [];

    function init() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        particles = [];
        for (let i = 0; i < 80; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1
            });
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#6366f1';
        
        particles.forEach((p, i) => {
            p.x += p.vx;
            p.y += p.vy;
            
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fill();
            
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
                if (dist < 150) {
                    ctx.strokeStyle = `rgba(99, 102, 241, ${1 - dist/150})`;
                    ctx.lineWidth = 0.5;
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        });
        requestAnimationFrame(animate);
    }

    window.addEventListener('resize', init);
    init();
    animate();
    </script>
    """, height=0)

def render_radial_score(score):
    return f'<div class="radial-score" style="--percentage: {score*360}deg;"><span class="score-text">{(score*100):.1f}%</span></div>'

def render_skill_badges(skills, type="matched"):
    class_map = {
        "matched": "matched-badge",
        "critical": "gap-critical",
        "partial": "gap-partial",
        "soft": "soft-badge"
    }
    badges = "".join([f'<span class="skill-badge {class_map.get(type)}">{s}</span>' for s in skills])
    return badges


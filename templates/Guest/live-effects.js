// Enhanced JavaScript with LIVE interactive effects
const style = document.createElement('style');
style.textContent = `
    @keyframes trail-fade {
        to { transform: scale(2); opacity: 0; }
    }
    @keyframes ripple-animation {
        to { transform: scale(4); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Scroll Animation Observer
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animated');
            
            if (entry.target.querySelector('.counter')) {
                const counters = entry.target.querySelectorAll('.counter');
                counters.forEach(counter => {
                    animateCounter(counter);
                });
            }
        }
    });
}, observerOptions);

// Counter Animation
function animateCounter(element) {
    const target = parseFloat(element.getAttribute('data-target'));
    const duration = 2000;
    const increment = target / (duration / 16);
    let current = 0;
    
    const updateCounter = () => {
        current += increment;
        if (current < target) {
            element.textContent = target % 1 === 0 ? Math.floor(current) : current.toFixed(1);
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target % 1 === 0 ? target : target.toFixed(1);
        }
    };
    
    updateCounter();
}

// Initialize all effects
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.fade-in-up, .fade-in-left, .fade-in-right, .scale-in');
    animatedElements.forEach(el => observer.observe(el));

    // LIVE EFFECT 1: Cursor Trail
    document.addEventListener('mousemove', (e) => {
        if (Math.random() > 0.7) {
            const trail = document.createElement('div');
            trail.style.cssText = `
                position: fixed; width: 15px; height: 15px; border-radius: 50%;
                background: radial-gradient(circle, rgba(201, 169, 97, 0.4), transparent);
                pointer-events: none; z-index: 9999;
                left: ${e.clientX}px; top: ${e.clientY}px;
                animation: trail-fade 0.8s ease-out forwards;
            `;
            document.body.appendChild(trail);
            setTimeout(() => trail.remove(), 800);
        }
    });

    // LIVE EFFECT 2: Mouse Follower
    const follower = document.createElement('div');
    follower.style.cssText = `
        position: fixed; width: 40px; height: 40px;
        border: 2px solid rgba(201, 169, 97, 0.3); border-radius: 50%;
        pointer-events: none; z-index: 9998;
    `;
    document.body.appendChild(follower);
    
    let mouseX = 0, mouseY = 0, followerX = 0, followerY = 0;
    document.addEventListener('mousemove', (e) => { mouseX = e.clientX; mouseY = e.clientY; });
    
    function animateFollower() {
        followerX += (mouseX - followerX) * 0.1;
        followerY += (mouseY - followerY) * 0.1;
        follower.style.left = (followerX - 20) + 'px';
        follower.style.top = (followerY - 20) + 'px';
        requestAnimationFrame(animateFollower);
    }
    animateFollower();

    // LIVE EFFECT 3: Ripple on Click
    document.querySelectorAll('.btn-primary-custom, .btn-outline-custom').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            ripple.style.cssText = `
                position: absolute; border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                width: ${size}px; height: ${size}px;
                left: ${e.clientX - rect.left - size/2}px;
                top: ${e.clientY - rect.top - size/2}px;
                transform: scale(0); animation: ripple-animation 0.6s ease-out;
                pointer-events: none;
            `;
            this.appendChild(ripple);
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // LIVE EFFECT 4: Parallax Movement
    document.addEventListener('mousemove', (e) => {
        const moveX = (e.clientX - window.innerWidth / 2) * 0.01;
        const moveY = (e.clientY - window.innerHeight / 2) * 0.01;
        document.querySelectorAll('.geometric-shape, .decorative-circle').forEach((shape, i) => {
            shape.style.transform = `translate(${moveX * (i + 1) * 0.5}px, ${moveY * (i + 1) * 0.5}px)`;
        });
    });

    // LIVE EFFECT 5: Dynamic Particles
    const particlesContainer = document.querySelector('.particles-container');
    setInterval(() => {
        if (document.querySelectorAll('.particle').length < 15) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 5 + 's';
            particlesContainer.appendChild(particle);
            setTimeout(() => particle.remove(), 15000);
        }
    }, 3000);

    // LIVE EFFECT 6: 3D Card Tilt
    document.querySelectorAll('.feature-card, .dashboard-card').forEach(card => {
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const rotateX = (y - rect.height / 2) / 15;
            const rotateY = (rect.width / 2 - x) / 15;
            this.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-10px) scale(1.02)`;
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });

    // LIVE EFFECT 7: Pulsing Stats
    setInterval(() => {
        document.querySelectorAll('.stat-number').forEach(stat => {
            stat.style.transform = 'scale(1.08)';
            setTimeout(() => stat.style.transform = 'scale(1)', 300);
        });
    }, 5000);
});

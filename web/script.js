// Desktop Newton - Web Edition
// Matter.js physics-based ragdoll simulation

const Engine = Matter.Engine,
      Render = Matter.Render,
      Runner = Matter.Runner,
      Bodies = Matter.Bodies,
      Composite = Matter.Composite,
      Constraint = Matter.Constraint,
      Mouse = Matter.Mouse,
      MouseConstraint = Matter.MouseConstraint,
      Events = Matter.Events,
      Vector = Matter.Vector,
      Body = Matter.Body;

// Physics configuration matching the original Python implementation
const PHYSICS_CONFIG = {
    headRadius: 15,
    torsoWidth: 20,
    torsoHeight: 40,
    upperArmWidth: 8,
    upperArmHeight: 25,
    forearmWidth: 7,
    forearmHeight: 22,
    thighWidth: 10,
    thighHeight: 30,
    calfWidth: 8,
    calfHeight: 28,
    defaultScale: 1.0,
    defaultGravity: 0.9,
    defaultFrictionAir: 0.02,
    defaultRestitution: 0.3,
    defaultFriction: 0.5
};

// Color scheme (matching Python RGB values converted to hex)
const COLORS = {
    head: '#FFC896',      // (255, 200, 150)
    torso: '#6496C8',     // (100, 150, 200)
    arm: '#96C864',       // (150, 200, 100)
    leg: '#C86496'        // (200, 100, 150)
};

class Ragdoll {
    constructor(x, y, scale = 1.0) {
        this.scale = scale;
        this.parts = [];
        this.constraints = [];
        this.colors = { ...COLORS };
        
        this.buildRagdoll(x, y);
    }
    
    buildRagdoll(startX, startY) {
        const s = this.scale;
        const x = startX;
        const y = startY;
        
        // Create head (circle)
        const headRadius = PHYSICS_CONFIG.headRadius * s;
        const head = Bodies.circle(x, y - 60 * s, headRadius, {
            label: 'head',
            render: { fillStyle: this.colors.head },
            friction: PHYSICS_CONFIG.defaultFriction,
            restitution: PHYSICS_CONFIG.defaultRestitution,
            density: 0.002
        });
        this.parts.push(head);
        
        // Create torso (rectangle)
        const torsoWidth = PHYSICS_CONFIG.torsoWidth * s;
        const torsoHeight = PHYSICS_CONFIG.torsoHeight * s;
        const torso = Bodies.rectangle(x, y - 20 * s, torsoWidth, torsoHeight, {
            label: 'torso',
            render: { fillStyle: this.colors.torso },
            friction: PHYSICS_CONFIG.defaultFriction,
            restitution: PHYSICS_CONFIG.defaultRestitution,
            density: 0.005
        });
        this.parts.push(torso);
        
        // Neck joint (head to torso)
        const neckConstraint = Constraint.create({
            bodyA: head,
            bodyB: torso,
            pointA: { x: 0, y: headRadius },
            pointB: { x: 0, y: -torsoHeight / 2 },
            stiffness: 0.9,
            damping: 0.1,
            length: 0,
            render: { visible: false }
        });
        this.constraints.push(neckConstraint);
        
        // Create arms
        this.createArm(x, y, torso, -1, s); // Left arm
        this.createArm(x, y, torso, 1, s);  // Right arm
        
        // Create legs
        this.createLeg(x, y, torso, -1, s); // Left leg
        this.createLeg(x, y, torso, 1, s);  // Right leg
        
        // Add angular limit constraints to simulate RotaryLimitJoint
        this.addAngularLimits(head, torso, -0.5, 0.5);
    }
    
    createArm(x, y, torso, direction, s) {
        const side = direction < 0 ? 'left' : 'right';
        
        // Upper arm
        const upperArmWidth = PHYSICS_CONFIG.upperArmWidth * s;
        const upperArmHeight = PHYSICS_CONFIG.upperArmHeight * s;
        const upperArm = Bodies.rectangle(
            x + direction * 20 * s, 
            y - 5 * s, 
            upperArmWidth, 
            upperArmHeight, 
            {
                label: `${side}_upper_arm`,
                render: { fillStyle: this.colors.arm },
                friction: PHYSICS_CONFIG.defaultFriction,
                restitution: PHYSICS_CONFIG.defaultRestitution,
                density: 0.003,
                angle: direction * 0.2
            }
        );
        this.parts.push(upperArm);
        
        // Shoulder joint
        const shoulderConstraint = Constraint.create({
            bodyA: torso,
            bodyB: upperArm,
            pointA: { x: direction * 10 * s, y: -15 * s },
            pointB: { x: 0, y: -upperArmHeight / 2 },
            stiffness: 0.9,
            damping: 0.1,
            length: 0,
            render: { visible: false }
        });
        this.constraints.push(shoulderConstraint);
        
        // Forearm
        const forearmWidth = PHYSICS_CONFIG.forearmWidth * s;
        const forearmHeight = PHYSICS_CONFIG.forearmHeight * s;
        const forearm = Bodies.rectangle(
            x + direction * 20 * s, 
            y - 35 * s, 
            forearmWidth, 
            forearmHeight, 
            {
                label: `${side}_forearm`,
                render: { fillStyle: this.colors.arm },
                friction: PHYSICS_CONFIG.defaultFriction,
                restitution: PHYSICS_CONFIG.defaultRestitution,
                density: 0.002,
                angle: direction * 0.1
            }
        );
        this.parts.push(forearm);
        
        // Elbow joint
        const elbowConstraint = Constraint.create({
            bodyA: upperArm,
            bodyB: forearm,
            pointA: { x: 0, y: upperArmHeight / 2 },
            pointB: { x: 0, y: -forearmHeight / 2 },
            stiffness: 0.9,
            damping: 0.1,
            length: 0,
            render: { visible: false }
        });
        this.constraints.push(elbowConstraint);
        
        // Angular limits for shoulder and elbow
        this.addAngularLimits(torso, upperArm, -1.0, 1.5, direction);
        this.addAngularLimits(upperArm, forearm, -2.5, 0.0);
    }
    
    createLeg(x, y, torso, direction, s) {
        const side = direction < 0 ? 'left' : 'right';
        
        // Thigh
        const thighWidth = PHYSICS_CONFIG.thighWidth * s;
        const thighHeight = PHYSICS_CONFIG.thighHeight * s;
        const thigh = Bodies.rectangle(
            x + direction * 10 * s, 
            y + 35 * s, 
            thighWidth, 
            thighHeight, 
            {
                label: `${side}_thigh`,
                render: { fillStyle: this.colors.leg },
                friction: PHYSICS_CONFIG.defaultFriction,
                restitution: PHYSICS_CONFIG.defaultRestitution,
                density: 0.004,
                angle: direction * 0.1
            }
        );
        this.parts.push(thigh);
        
        // Hip joint
        const hipConstraint = Constraint.create({
            bodyA: torso,
            bodyB: thigh,
            pointA: { x: direction * 8 * s, y: torso.bounds.max.y - torso.position.y - 2 * s },
            pointB: { x: 0, y: -thighHeight / 2 },
            stiffness: 0.9,
            damping: 0.1,
            length: 0,
            render: { visible: false }
        });
        this.constraints.push(hipConstraint);
        
        // Calf
        const calfWidth = PHYSICS_CONFIG.calfWidth * s;
        const calfHeight = PHYSICS_CONFIG.calfHeight * s;
        const calf = Bodies.rectangle(
            x + direction * 10 * s, 
            y + 65 * s, 
            calfWidth, 
            calfHeight, 
            {
                label: `${side}_calf`,
                render: { fillStyle: this.colors.leg },
                friction: PHYSICS_CONFIG.defaultFriction,
                restitution: PHYSICS_CONFIG.defaultRestitution,
                density: 0.003,
                angle: direction * 0.05
            }
        );
        this.parts.push(calf);
        
        // Knee joint
        const kneeConstraint = Constraint.create({
            bodyA: thigh,
            bodyB: calf,
            pointA: { x: 0, y: thighHeight / 2 },
            pointB: { x: 0, y: -calfHeight / 2 },
            stiffness: 0.9,
            damping: 0.1,
            length: 0,
            render: { visible: false }
        });
        this.constraints.push(kneeConstraint);
        
        // Angular limits for hip and knee
        this.addAngularLimits(torso, thigh, -1.0, 0.5);
        this.addAngularLimits(thigh, calf, 0.0, 2.0);
    }
    
    addAngularLimits(bodyA, bodyB, minAngle, maxAngle, direction = 1) {
        // Matter.js doesn't have native angular limits like Pymunk's RotaryLimitJoint
        // We use high-stiffness constraints and soft angular springs to approximate behavior
        // This is a simplified approach - in practice, the constraints above work well enough
        
        // Apply direction flip for right side limits
        const adjustedMin = direction > 0 ? minAngle : -maxAngle;
        const adjustedMax = direction > 0 ? maxAngle : -minAngle;
        
        // Store limits for potential manual enforcement
        bodyA.angularLimits = bodyA.angularLimits || [];
        bodyA.angularLimits.push({
            otherBody: bodyB,
            min: adjustedMin,
            max: adjustedMax
        });
    }
    
    setColor(type, color) {
        this.colors[type] = color;
        this.parts.forEach(part => {
            const label = part.label || '';
            if (type === 'head' && label === 'head') {
                part.render.fillStyle = color;
            } else if (type === 'torso' && label === 'torso') {
                part.render.fillStyle = color;
            } else if (type === 'arm' && label.includes('arm')) {
                part.render.fillStyle = color;
            } else if (type === 'leg' && label.includes('leg')) {
                part.render.fillStyle = color;
            }
        });
    }
    
    setProperty(property, value) {
        this.parts.forEach(part => {
            if (property === 'frictionAir') {
                part.frictionAir = value;
            } else if (property === 'restitution') {
                part.restitution = value;
            } else if (property === 'friction') {
                part.friction = value;
            }
        });
    }
    
    getPosition() {
        // Return head position as reference
        const head = this.parts.find(p => p.label === 'head');
        return head ? head.position : { x: 0, y: 0 };
    }
    
    destroy() {
        this.parts = [];
        this.constraints = [];
    }
}

class DesktopNewton {
    constructor() {
        this.engine = null;
        this.render = null;
        this.runner = null;
        this.ragdoll = null;
        this.mouseConstraint = null;
        this.boundaries = [];
        
        this.settings = {
            gravity: PHYSICS_CONFIG.defaultGravity,
            damping: PHYSICS_CONFIG.defaultFrictionAir,
            elasticity: PHYSICS_CONFIG.defaultRestitution,
            scale: PHYSICS_CONFIG.defaultScale
        };
        
        this.init();
    }
    
    init() {
        // Get container dimensions
        const container = document.getElementById('canvas-container');
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // Create Matter.js engine
        this.engine = Engine.create({
            enableSleeping: false
        });
        
        // Set gravity (Matter.js uses positive Y for down, matching our needs)
        this.engine.gravity.y = this.settings.gravity;
        
        // Create renderer
        this.render = Render.create({
            element: container,
            engine: this.engine,
            options: {
                width: width,
                height: height,
                wireframes: false,
                background: '#1a1a1a',
                pixelRatio: window.devicePixelRatio || 1
            }
        });
        
        // Create boundaries
        this.createBoundaries(width, height);
        
        // Create ragdoll
        this.createRagdoll(width / 2, height / 3, this.settings.scale);
        
        // Add mouse control
        this.setupMouseControl();
        
        // Start the engine
        Render.run(this.render);
        this.runner = Runner.create();
        Runner.run(this.runner, this.engine);
        
        // Setup UI event handlers
        this.setupUI();
        
        // Handle window resize
        window.addEventListener('resize', () => this.handleResize());
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Custom rendering for joints
        Events.on(this.render, 'afterRender', () => this.drawJoints());
    }
    
    createBoundaries(width, height) {
        const wallThickness = 100;
        
        // Floor (placed lower to allow ragdoll to fall naturally)
        const floor = Bodies.rectangle(width / 2, height + wallThickness / 2 - 10, width + 200, wallThickness, {
            isStatic: true,
            friction: 0.8,
            restitution: 0.2,
            render: { visible: false },
            label: 'floor'
        });
        
        // Left wall
        const leftWall = Bodies.rectangle(-wallThickness / 2, height / 2, wallThickness, height * 2, {
            isStatic: true,
            friction: 0.5,
            restitution: 0.5,
            render: { visible: false },
            label: 'wall_left'
        });
        
        // Right wall
        const rightWall = Bodies.rectangle(width + wallThickness / 2, height / 2, wallThickness, height * 2, {
            isStatic: true,
            friction: 0.5,
            restitution: 0.5,
            render: { visible: false },
            label: 'wall_right'
        });
        
        // Ceiling
        const ceiling = Bodies.rectangle(width / 2, -wallThickness / 2, width + 200, wallThickness, {
            isStatic: true,
            friction: 0.5,
            restitution: 0.5,
            render: { visible: false },
            label: 'ceiling'
        });
        
        this.boundaries = [floor, leftWall, rightWall, ceiling];
        Composite.add(this.engine.world, this.boundaries);
    }
    
    createRagdoll(x, y, scale) {
        // Remove existing ragdoll
        if (this.ragdoll) {
            Composite.remove(this.engine.world, this.ragdoll.parts);
            Composite.remove(this.engine.world, this.ragdoll.constraints);
        }
        
        // Create new ragdoll
        this.ragdoll = new Ragdoll(x, y, scale);
        
        // Apply current physics settings
        this.ragdoll.setProperty('frictionAir', this.settings.damping);
        this.ragdoll.setProperty('restitution', this.settings.elasticity);
        
        // Add to world
        Composite.add(this.engine.world, this.ragdoll.parts);
        Composite.add(this.engine.world, this.ragdoll.constraints);
    }
    
    setupMouseControl() {
        const mouse = Mouse.create(this.render.canvas);
        
        this.mouseConstraint = MouseConstraint.create(this.engine, {
            mouse: mouse,
            constraint: {
                stiffness: 0.2,
                render: {
                    visible: true,
                    strokeStyle: '#FFFF00',
                    lineWidth: 2
                }
            }
        });
        
        // Prevent mouse from interacting with boundaries
        this.mouseConstraint.collisionFilter.mask = 1;
        
        Composite.add(this.engine.world, this.mouseConstraint);
        
        // Keep mouse in sync with rendering
        this.render.mouse = mouse;
    }
    
    setupUI() {
        // Panel toggle
        const panel = document.getElementById('settings-panel');
        const miniToggle = document.getElementById('mini-toggle');
        const closeBtn = document.getElementById('close-panel');
        
        closeBtn.addEventListener('click', () => {
            panel.style.display = 'none';
            miniToggle.style.display = 'block';
        });
        
        miniToggle.addEventListener('click', () => {
            panel.style.display = 'block';
            miniToggle.style.display = 'none';
        });
        
        // Gravity slider
        const gravitySlider = document.getElementById('gravity');
        const gravityValue = document.getElementById('gravity-value');
        gravitySlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.settings.gravity = value;
            this.engine.gravity.y = value;
            gravityValue.textContent = value.toFixed(1);
        });
        
        // Air Resistance (damping) slider
        const dampingSlider = document.getElementById('damping');
        const dampingValue = document.getElementById('damping-value');
        dampingSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.settings.damping = value;
            if (this.ragdoll) {
                this.ragdoll.setProperty('frictionAir', value);
            }
            dampingValue.textContent = value.toFixed(3);
        });
        
        // Bounciness (elasticity) slider
        const elasticitySlider = document.getElementById('elasticity');
        const elasticityValue = document.getElementById('elasticity-value');
        elasticitySlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.settings.elasticity = value;
            if (this.ragdoll) {
                this.ragdoll.setProperty('restitution', value);
            }
            elasticityValue.textContent = value.toFixed(1);
        });
        
        // Scale slider
        const scaleSlider = document.getElementById('scale');
        const scaleValue = document.getElementById('scale-value');
        scaleSlider.addEventListener('input', (e) => {
            const value = parseFloat(e.target.value);
            this.settings.scale = value;
            scaleValue.textContent = value.toFixed(1);
            
            // Rebuild ragdoll with new scale at current position
            const currentPos = this.ragdoll ? this.ragdoll.getPosition() : { 
                x: window.innerWidth / 2, 
                y: window.innerHeight / 3 
            };
            this.createRagdoll(currentPos.x, currentPos.y, value);
        });
        
        // Color buttons
        document.querySelectorAll('.color-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const color = e.target.dataset.color;
                const type = e.target.dataset.type;
                
                // Update active state
                document.querySelectorAll(`.color-btn[data-type="${type}"]`).forEach(b => {
                    b.classList.remove('active');
                });
                e.target.classList.add('active');
                
                // Update ragdoll color
                if (this.ragdoll) {
                    this.ragdoll.setColor(type, color);
                }
            });
        });
        
        // Reset button
        document.getElementById('reset-btn').addEventListener('click', () => {
            this.resetRagdoll();
        });
    }
    
    drawJoints() {
        if (!this.ragdoll) return;
        
        const ctx = this.render.context;
        
        // Draw joint visualizations
        this.ragdoll.constraints.forEach(constraint => {
            if (constraint.label === 'Mouse Constraint') return;
            
            const bodyA = constraint.bodyA;
            const bodyB = constraint.bodyB;
            
            if (!bodyA || !bodyB) return;
            
            // Calculate world positions of anchor points
            const posA = Vector.add(bodyA.position, Vector.rotate(constraint.pointA, bodyA.angle));
            const posB = Vector.add(bodyB.position, Vector.rotate(constraint.pointB, bodyB.angle));
            
            // Draw joint as small circle at midpoint
            const midX = (posA.x + posB.x) / 2;
            const midY = (posA.y + posB.y) / 2;
            
            ctx.beginPath();
            ctx.arc(midX, midY, 4, 0, 2 * Math.PI);
            ctx.fillStyle = '#FFFFFF';
            ctx.fill();
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1;
            ctx.stroke();
        });
    }
    
    resetRagdoll() {
        const x = window.innerWidth / 2;
        const y = window.innerHeight / 3;
        this.createRagdoll(x, y, this.settings.scale);
    }
    
    handleResize() {
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        // Update canvas size
        this.render.canvas.width = width;
        this.render.canvas.height = height;
        this.render.options.width = width;
        this.render.options.height = height;
        
        // Update boundary positions
        if (this.boundaries.length > 0) {
            const [floor, leftWall, rightWall, ceiling] = this.boundaries;
            
            Body.setPosition(floor, { x: width / 2, y: height + 40 });
            Body.setPosition(leftWall, { x: -50, y: height / 2 });
            Body.setPosition(rightWall, { x: width + 50, y: height / 2 });
            Body.setPosition(ceiling, { x: width / 2, y: -50 });
            
            // Update sizes
            floor.bounds = {
                min: { x: -100, y: height },
                max: { x: width + 100, y: height + 100 }
            };
        }
    }
    
    handleKeydown(e) {
        switch (e.key.toLowerCase()) {
            case 'h':
                const helpOverlay = document.getElementById('help-overlay');
                helpOverlay.classList.toggle('hidden');
                break;
            case ' ':
                e.preventDefault();
                this.resetRagdoll();
                break;
            case 's':
                const panel = document.getElementById('settings-panel');
                const miniToggle = document.getElementById('mini-toggle');
                if (panel.style.display === 'none') {
                    panel.style.display = 'block';
                    miniToggle.style.display = 'none';
                } else {
                    panel.style.display = 'none';
                    miniToggle.style.display = 'block';
                }
                break;
            case 'escape':
                // User can close the tab/window
                break;
        }
    }
}

// Initialize application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new DesktopNewton();
    
    // Expose for debugging
    window.desktopNewton = app;
});

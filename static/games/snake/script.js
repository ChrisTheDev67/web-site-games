const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const startBtn = document.getElementById('startBtn');

const gridSize = 20;
const tileCount = canvas.width / gridSize;

let score = 0;
let snake = [];
let food = { x: 15, y: 15 };
let velocity = { x: 0, y: 0 };
let gameInterval;
let isGameRunning = false;

function initGame() {
    snake = [
        { x: 10, y: 10 },
        { x: 9, y: 10 },
        { x: 8, y: 10 }
    ];
    score = 0;
    velocity = { x: 1, y: 0 }; // Start moving right
    scoreElement.textContent = score;
    placeFood();
    if (gameInterval) clearInterval(gameInterval);
    gameInterval = setInterval(gameLoop, 100);
    isGameRunning = true;
    startBtn.style.display = 'none';
}

function gameLoop() {
    update();
    draw();
}

function update() {
    // Move snake
    const head = { x: snake[0].x + velocity.x, y: snake[0].y + velocity.y };

    // Wall collision (Wrap around)
    if (head.x < 0) head.x = tileCount - 1;
    if (head.x >= tileCount) head.x = 0;
    if (head.y < 0) head.y = tileCount - 1;
    if (head.y >= tileCount) head.y = 0;

    // Self collision
    for (let part of snake) {
        if (head.x === part.x && head.y === part.y) {
            gameOver();
            return;
        }
    }

    snake.unshift(head);

    // Eat food
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreElement.textContent = score;
        placeFood();
    } else {
        snake.pop();
    }
}

function draw() {
    // Clear screen
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw Food
    ctx.fillStyle = '#ff0000';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#ff0000';
    ctx.fillRect(food.x * gridSize, food.y * gridSize, gridSize - 2, gridSize - 2);

    // Draw Snake
    ctx.shadowBlur = 0;
    snake.forEach((part, index) => {
        if (index === 0) {
            ctx.fillStyle = '#fff'; // Head
        } else {
            ctx.fillStyle = '#0f0'; // Body
        }
        ctx.fillRect(part.x * gridSize, part.y * gridSize, gridSize - 2, gridSize - 2);
    });
}

function placeFood() {
    food = {
        x: Math.floor(Math.random() * tileCount),
        y: Math.floor(Math.random() * tileCount)
    };
    // Don't place food on snake
    for (let part of snake) {
        if (part.x === food.x && part.y === food.y) {
            placeFood();
            break;
        }
    }
}

function gameOver() {
    isGameRunning = false;
    clearInterval(gameInterval);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#0f0';
    ctx.font = '30px Courier New';
    ctx.textAlign = 'center';
    ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2);

    startBtn.textContent = 'Play Again';
    startBtn.style.display = 'inline-block';
}

// Input handling
document.addEventListener('keydown', (e) => {
    if (!isGameRunning && (e.code === 'Enter' || e.code === 'Space')) {
        initGame();
        return;
    }

    switch (e.code) {
        case 'ArrowUp':
            if (velocity.y !== 1) velocity = { x: 0, y: -1 };
            break;
        case 'ArrowDown':
            if (velocity.y !== -1) velocity = { x: 0, y: 1 };
            break;
        case 'ArrowLeft':
            if (velocity.x !== 1) velocity = { x: -1, y: 0 };
            break;
        case 'ArrowRight':
            if (velocity.x !== -1) velocity = { x: 1, y: 0 };
            break;
    }
});

// Touch controls (Swipe)
let touchStartX = 0;
let touchStartY = 0;

canvas.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
    e.preventDefault();
}, { passive: false });

canvas.addEventListener('touchmove', (e) => {
    e.preventDefault(); // Prevent scrolling
}, { passive: false });

canvas.addEventListener('touchend', (e) => {
    if (!isGameRunning) return;

    const touchEndX = e.changedTouches[0].clientX;
    const touchEndY = e.changedTouches[0].clientY;

    const dx = touchEndX - touchStartX;
    const dy = touchEndY - touchStartY;

    if (Math.abs(dx) > Math.abs(dy)) {
        // Horizontal
        if (dx > 0 && velocity.x !== -1) velocity = { x: 1, y: 0 };
        else if (dx < 0 && velocity.x !== 1) velocity = { x: -1, y: 0 };
    } else {
        // Vertical
        if (dy > 0 && velocity.y !== -1) velocity = { x: 0, y: 1 };
        else if (dy < 0 && velocity.y !== 1) velocity = { x: 0, y: -1 };
    }
}, { passive: false });

startBtn.addEventListener('click', initGame);

// Initial draw
ctx.fillStyle = '#000';
ctx.fillRect(0, 0, canvas.width, canvas.height);

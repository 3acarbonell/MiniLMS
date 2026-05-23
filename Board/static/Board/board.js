const $canvas = document.querySelector("#canvas");
const ctx = $canvas.getContext("2d");

$canvas.addEventListener("mousedown", startDrawing);
$canvas.addEventListener("mousemove", draw);
$canvas.addEventListener("mouseup", stopDrawing);
$canvas.addEventListener("mouseleave", stopDrawing);


const ws = new WebSocket('ws://' + window.location.host + '/ws/board/');

function sizeOfCanvas() {
    const rect = $canvas.getBoundingClientRect();

    $canvas.width = rect.width;
    $canvas.height = rect.height;
}

sizeOfCanvas()

ws.onmessage = function (event) {
    const data = JSON.parse(event.data);

    if (data.type === "draw") {
        const [x1, y1, x2, y2, color] = [
            data.x1,
            data.y1,
            data.x2,
            data.y2,
            data.color
        ];

        drawLine(x1, y1, x2, y2, color);
    }
};

ws.onclose = function (e) {
    console.error('Chat socket closed unexptedly');
}

let isDrawing = false;
let startX, startY;
let lastX = 0;
let lastY = 0;

function startDrawing(event) {
    isDrawing = true;

    const { offsetX, offsetY } = event;

    [startX, startY] = [offsetX, offsetY];
    [lastX, lastY] = [offsetX, offsetY];
}

function draw(event) {
    if (!isDrawing) return;

    const { offsetX, offsetY } = event;

    drawLine(lastX, lastY, offsetX, offsetY, "#000000");

    sendDrawLine(lastX, lastY, offsetX, offsetY, "#000000");

    [lastX, lastY] = [offsetX, offsetY];
}

function stopDrawing(event) {
    isDrawing = false;
}

function drawLine(x1, y1, x2, y2, color) {
    ctx.strokeStyle = "#000000";
    ctx.lineWidth = 8;
    ctx.lineCap = "round"

    ctx.beginPath();

    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);

    ctx.stroke();
}

function sendDrawLine(x1, y1, x2, y2, color) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: "draw", x1, y1, x2, y2, color
        }));
    }
}
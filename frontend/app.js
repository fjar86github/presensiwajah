const video = document.getElementById("video");
const statusText = document.getElementById("status");

let state = "look"; // look -> right -> left -> done
let xPositions = [];
const THRESHOLD = 15; // gerakan kepala minimal
const STABLE_FRAMES = 15; // jumlah frame wajah stabil

// =====================
// Inisialisasi Face Mesh
// =====================
const faceMesh = new FaceMesh({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
});

faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.7,
  minTrackingConfidence: 0.7
});

// =====================
// Event results
// =====================
faceMesh.onResults((results) => {
  if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
    statusText.innerText = "Arahkan wajah ke kamera 👀";
    xPositions = [];
    return;
  }

  const landmarks = results.multiFaceLandmarks[0];

  // Ambil posisi hidung sebagai referensi
  const nose = landmarks[1]; // landmark hidung tip
  const x = nose.x * video.videoWidth;
  xPositions.push(x);
  if (xPositions.length > STABLE_FRAMES) xPositions.shift();

  const maxX = Math.max(...xPositions);
  const minX = Math.min(...xPositions);

  switch(state) {
    case "look":
      if (maxX - minX < THRESHOLD / 2 && xPositions.length >= STABLE_FRAMES) {
        state = "right";
        xPositions = [];
        statusText.innerText = "Gerakkan kepala ke kanan 👉";
      } else {
        statusText.innerText = "Tahan wajah stabil di posisi tengah";
      }
      break;

    case "right":
      if (maxX - minX > THRESHOLD) {
        state = "left";
        xPositions = [];
        statusText.innerText = "Gerakkan kepala ke kiri 👈";
      } else {
        statusText.innerText = "Gerakkan kepala ke kanan 👉";
      }
      break;

    case "left":
      if (maxX - minX > THRESHOLD) {
        state = "done";
        statusText.innerText = "Liveness OK ✅";
        capture();
      } else {
        statusText.innerText = "Gerakkan kepala ke kiri 👈";
      }
      break;

    case "done":
      break;
  }
});

// =====================
// Start kamera
// =====================
let camera = null;
async function startCamera() {
  camera = new Camera(video, {
    onFrame: async () => {
      await faceMesh.send({ image: video });
    },
    width: 480,
    height: 360
  });
  camera.start();
}

// =====================
// Capture & kirim ke backend
// =====================
function capture() {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);
  const base64 = canvas.toDataURL("image/jpeg");
  sendToBackend(base64);
}

async function sendToBackend(image) {
  try {
    const res = await fetch("http://localhost:5000/presensi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image }),
    });
    const data = await res.json();
    statusText.innerText = "Presensi berhasil 🚀";
    console.log("Response backend:", data);
  } catch (err) {
    console.error("Send error:", err);
    statusText.innerText = "Gagal kirim ke server ❌";
  }
}

// =====================
// Tombol start
// =====================
async function start() {
  state = "look";
  xPositions = [];
  statusText.innerText = "Memulai...";
  await startCamera();
  statusText.innerText = "Camera ready ✅";
}
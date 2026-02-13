// Global variables
let player;
let isYoutubeReady = false;
let userManuallyPaused = false; // Flag to track if the user paused the video manually
let isSystemPause = false; // Flag to indicate if the pause was triggered by the system

// DOM Elements
const urlInput = document.getElementById('video-url');
const loadBtn = document.getElementById('load-btn');
const statusDiv = document.getElementById('status');

// MediaPipe Elements
const videoElement = document.querySelector('.input_video');
const canvasElement = document.querySelector('.output_canvas');
const canvasCtx = canvasElement.getContext('2d');

// 1. Load the IFrame Player API code asynchronously.
const tag = document.createElement('script');
tag.src = "https://www.youtube.com/iframe_api";
const firstScriptTag = document.getElementsByTagName('script')[0];
firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

// 2. This function creates an <iframe> (and YouTube player)
//    after the API code downloads.
function onYouTubeIframeAPIReady() {
    isYoutubeReady = true;
    // console.log("YouTube API Ready");

    player = new YT.Player('player', {
        height: '100%',
        width: '100%',
        videoId: '', // Initial video (can be empty or a default)
        playerVars: {
            'playsinline': 1,
            'autoplay': 0 // Don't autoplay initially
        },
        events: {
            'onReady': onPlayerReady,
            'onStateChange': onPlayerStateChange
        }
    });
}

function onPlayerReady(event) {
    updateStatus("Player Ready. Enter a URL and click Load.");
}

function onPlayerStateChange(event) {
    // YT.PlayerState.PLAYING = 1
    // YT.PlayerState.PAUSED = 2

    if (event.data === YT.PlayerState.PLAYING) {
        userManuallyPaused = false;
        // console.log("User playing (or system resumed). Manual pause cleared.");
    } else if (event.data === YT.PlayerState.PAUSED) {
        if (isSystemPause) {
            // console.log("System paused the video.");
            isSystemPause = false; // Reset the flag
        } else {
            // User paused it
            userManuallyPaused = true;
            // console.log("User manually paused.");
        }
    }
}

// 3. Load Video Logic
loadBtn.addEventListener('click', () => {
    const url = urlInput.value.trim();
    if (!url) {
        alert("Please enter a YouTube URL.");
        return;
    }

    const videoId = extractVideoID(url);
    if (videoId) {
        if (isYoutubeReady && player) {
            player.loadVideoById(videoId);
            userManuallyPaused = false; // Reset manual pause on new video load
            updateStatus("Video loaded.");
        } else {
            alert("Player is not ready yet.");
        }
    } else {
        alert("Invalid YouTube URL.");
    }
});

function extractVideoID(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);

    if (match && match[2].length === 11) {
        return match[2];
    } else {
        return null;
    }
}

function updateStatus(msg) {
    statusDiv.textContent = "Status: " + msg;
}

// --- MediaPipe FaceMesh & Camera Integration ---

function onResults(results) {
  // We do not need to draw on the canvas for the final product,
  // but we must process the landmarks.
  // Keeping the drawImage for basic debugging feedback (seeing yourself is useful for setup),
  // but removing the heavy mesh drawing.

  canvasCtx.save();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

  if (results.multiFaceLandmarks) {
    for (const landmarks of results.multiFaceLandmarks) {
      checkFocus(landmarks);
    }
  }
  canvasCtx.restore();
}

const faceMesh = new FaceMesh({locateFile: (file) => {
  return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
}});

faceMesh.setOptions({
  maxNumFaces: 1,
  refineLandmarks: true,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

faceMesh.onResults(onResults);

const camera = new Camera(videoElement, {
  onFrame: async () => {
    await faceMesh.send({image: videoElement});
  },
  width: 480,
  height: 360
});

camera.start()
  .then(() => {
      // console.log("Camera started successfully");
  })
  .catch((err) => {
      console.error("Error starting camera:", err);
      updateStatus("Error: Camera not accessible.");
  });

// Focus State Management
let isFocused = true; // Stable state
let lastStateChangeAttemptTime = Date.now();
const FOCUS_GRACE_PERIOD = 1000; // 1 second to confirm look-away
const GAIN_FOCUS_DELAY = 200; // 0.2 second to confirm look-back

function checkFocus(landmarks) {
    const nose = landmarks[1];
    const leftEar = landmarks[234];
    const rightEar = landmarks[454];
    const forehead = landmarks[10];
    const chin = landmarks[152];

    // Calculate Yaw (Horizontal)
    // Ratio of distances from nose to ears
    const distToLeftEar = Math.abs(nose.x - leftEar.x);
    const distToRightEar = Math.abs(nose.x - rightEar.x);
    // Add small epsilon to avoid division by zero
    const yawRatio = distToLeftEar / (distToRightEar + 0.0001);

    // Calculate Pitch (Vertical)
    // Ratio of distances from nose to forehead/chin
    const distToForehead = Math.abs(nose.y - forehead.y);
    const distToChin = Math.abs(nose.y - chin.y);
    const pitchRatio = distToForehead / (distToChin + 0.0001);

    // Thresholds
    // Yaw: 1.0 is centered. < 0.2 (looking right) or > 5.0 (looking left) is extreme.
    // Let's use 0.4 to 2.5 as "focused" range.
    const isYawFocused = yawRatio > 0.4 && yawRatio < 2.5;

    // Pitch: 1.0 is centered.
    // Let's use 0.5 to 2.0.
    const isPitchFocused = pitchRatio > 0.5 && pitchRatio < 2.0;

    const instantFocusState = isYawFocused && isPitchFocused;

    handleFocusState(instantFocusState);
}

function handleFocusState(instantFocusState) {
    const now = Date.now();

    if (instantFocusState === isFocused) {
        // If the instant state matches our stable state, reset the timer
        // effectively canceling any pending change.
        lastStateChangeAttemptTime = now;
        return;
    }

    // State differs. Check duration.
    const duration = now - lastStateChangeAttemptTime;
    const threshold = instantFocusState ? GAIN_FOCUS_DELAY : FOCUS_GRACE_PERIOD;

    if (duration > threshold) {
        isFocused = instantFocusState;
        lastStateChangeAttemptTime = now;

        if (isFocused) {
            onFocusGained();
        } else {
            onFocusLost();
        }
    }
}

function onFocusGained() {
    // console.log("Focus GAINED");
    updateStatus("User is focused.");
    document.getElementById('status').style.color = "green";

    // Hide overlay
    document.getElementById('warning-overlay').classList.add('hidden');

    // Resume video if not manually paused
    if (isYoutubeReady && !userManuallyPaused && player && typeof player.playVideo === 'function' && player.getPlayerState() === YT.PlayerState.PAUSED) {
        player.playVideo();
    }
}

function onFocusLost() {
    // console.log("Focus LOST");
    updateStatus("User looked away!");
    document.getElementById('status').style.color = "red";

    // Show overlay
    document.getElementById('warning-overlay').classList.remove('hidden');

    // Pause video if playing
    if (isYoutubeReady && player && typeof player.pauseVideo === 'function' && player.getPlayerState() === YT.PlayerState.PLAYING) {
        isSystemPause = true; // Set flag BEFORE calling pause
        player.pauseVideo();
    }
}

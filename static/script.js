document.getElementById('video-file').addEventListener('change', handleFileSelect);
document.getElementById('audio-file').addEventListener('change', handleAudioSelect);
document.getElementById('trim-form').addEventListener('submit', handleTrimSubmit);
document.getElementById('audio-form').addEventListener('submit', handleAudioSubmit);
document.getElementById('transition-form').addEventListener('submit', handleTransitionSubmit);

let videoElement = document.getElementById('video-preview');
let startTimeInput = document.getElementById('start-time');
let endTimeInput = document.getElementById('end-time');
let audioStartTimeInput = document.getElementById('audio-start-time');
let audioEndTimeInput = document.getElementById('audio-end-time');
let originalVideoURL = ''; // Variable to store the original video URL
let trimmedVideoURL = ''; // Variable to store the trimmed video URL
let originalAudioURL = ''; // Variable to store the original audio URL
let selectedTransition = null; // Variable to store selected transition

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const videoURL = URL.createObjectURL(file);
        videoElement.src = videoURL;
        videoElement.style.display = 'block';
        originalVideoURL = videoURL; // Store the original video URL
        trimmedVideoURL = videoURL; // Initially set the trimmed video URL to original video URL
    }
}

function handleAudioSelect(event) {
    const file = event.target.files[0];
    if (file) {
        const audioURL = URL.createObjectURL(file);
        // Store or use this URL as needed
        originalAudioURL = audioURL; // Store the original audio URL
    }
}

async function handleTrimSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    const response = await fetch('/trim', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    trimmedVideoURL = result.fileUrl; // Update the trimmed video URL
    videoElement.src = trimmedVideoURL;
    videoElement.style.display = 'block';
    
    const downloadLink = document.getElementById('download-link');
    downloadLink.href = trimmedVideoURL;
    downloadLink.style.display = 'inline';
}

async function handleAudioSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    formData.append('video', trimmedVideoURL); // Use the trimmed video URL
    formData.append('audio-start', audioStartTimeInput.value);
    formData.append('audio-end', audioEndTimeInput.value);

    const response = await fetch('/add_audio', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (result.error) {
        alert(result.error);
        return;
    }

    videoElement.src = result.fileUrl;
    videoElement.style.display = 'block';
    
    const downloadLink = document.getElementById('download-link');
    downloadLink.href = result.fileUrl;
    downloadLink.style.display = 'inline';
}

// Reset button functionality for video
document.getElementById('reset-times').addEventListener('click', () => {
    startTimeInput.value = '';
    endTimeInput.value = '';
    if (originalVideoURL) {
        videoElement.src = originalVideoURL;
        videoElement.style.display = 'block';
        trimmedVideoURL = originalVideoURL; // Reset trimmed video URL
    }
});

// Reset button functionality for audio
document.getElementById('reset-audio-times').addEventListener('click', async () => {
    audioStartTimeInput.value = '';
    audioEndTimeInput.value = '';

    const response = await fetch('/remove_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ video_path: trimmedVideoURL })
    });

    const result = await response.json();

    if (result.error) {
        alert(result.error);
        return;
    }

    videoElement.src = result.fileUrl;
    videoElement.style.display = 'block';
    
    const downloadLink = document.getElementById('download-link');
    downloadLink.href = result.fileUrl;
    downloadLink.style.display = 'inline';
});

function updatePreview() {
    const start = parseFloat(startTimeInput.value) || 0;
    const end = parseFloat(endTimeInput.value) || videoElement.duration;

    if (videoElement.src) {
        videoElement.currentTime = start;

        videoElement.onseeked = () => {
            if (videoElement.currentTime >= end) {
                videoElement.pause();
                videoElement.currentTime = start;
            }
        };
    }
}

document.getElementById('fade-transition').addEventListener('click', () => {
    setTransition('fade');
});
document.getElementById('flip-transition').addEventListener('click', () => {
    setTransition('flip');
});
document.getElementById('rotate-transition').addEventListener('click', () => {
    setTransition('rotate');
});

document.getElementById('preview-transition').addEventListener('click', previewTransition);

async function setTransition(type) {
    selectedTransition = type;
    document.getElementById('transition-message').style.display = 'none'; // Hide warning
}

function previewTransition() {
    if (!selectedTransition) {
        document.getElementById('transition-message').style.display = 'block';
        document.getElementById('transition-message').innerText = 'Please select a transition';
        return;
    }

    const startTime = parseFloat(document.getElementById('transition-start-time').value) || 0;
    const endTime = parseFloat(document.getElementById('transition-end-time').value) || videoElement.duration;

    if (videoElement.src) {
        videoElement.currentTime = startTime;
        videoElement.play();
        
        videoElement.onseeked = () => {
            if (videoElement.currentTime >= endTime) {
                videoElement.pause();
                videoElement.currentTime = startTime;
            }
        };
    }
}

async function handleTransitionSubmit(event) {
    event.preventDefault();

    if (!selectedTransition) {
        document.getElementById('transition-message').style.display = 'block';
        document.getElementById('transition-message').innerText = 'Please select a transition';
        return;
    }

    const formData = new FormData();
    formData.append('transition', selectedTransition);
    formData.append('start', document.getElementById('transition-start-time').value);
    formData.append('end', document.getElementById('transition-end-time').value);
    formData.append('video', trimmedVideoURL); // Use trimmed video URL

    const response = await fetch('/apply_transition', {
        method: 'POST',
        body: formData
    });

    const result = await response.json();

    if (result.error) {
        alert(result.error);
        return;
    }

    videoElement.src = result.fileUrl;
    videoElement.style.display = 'block';
    
    const downloadLink = document.getElementById('download-link');
    downloadLink.href = result.fileUrl;
    downloadLink.style.display = 'inline';
}

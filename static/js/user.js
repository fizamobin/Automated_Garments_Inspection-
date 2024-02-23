document.addEventListener('DOMContentLoaded', (event) => {
const startCameraBtn = document.getElementById('startCamera');
const takeDefectPicBtn = document.getElementById('takeDefectPic');
const resumeCameraBtn = document.getElementById('resumeCamera');
const stopCameraBtn = document.getElementById('stopCamera');
const cameraFeed = document.getElementById('cameraFeed');
const defectImagesContainer = document.querySelector('.defect-images');
const printReportBtn = document.getElementById('printReport');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d'); 

let stream = null;
let mediaRecorder = null;
let chunks = [];

startCameraBtn.addEventListener('click', async () => {
  try {
    if (stream) {
      // If the camera is already started, stop it first
      stream.getTracks().forEach((track) => track.stop());
    }
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    cameraFeed.srcObject = stream;
    mediaRecorder = new MediaRecorder(stream);
    chunks = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      const videoUrl = URL.createObjectURL(blob);
      const videoElement = document.createElement('video');
      videoElement.src = videoUrl;
      videoElement.controls = true;
      defectImagesContainer.appendChild(videoElement);
    };
  } catch (error) {
    console.error('Error accessing the camera:', error);
  }
});

takeDefectPicBtn.addEventListener('click', () => {
    if (!stream) {
      console.error('Camera is not started.');
      return;
    }
  
    ctx.drawImage(cameraFeed, 0, 0, canvas.width, canvas.height);
    const imageUrl = canvas.toDataURL('image/png');
    addDefectImage(imageUrl);
  });

resumeCameraBtn.addEventListener('click', async () => {
    try {
      if (stream) {
        // If the camera is already started, stop it first
        stream.getTracks().forEach((track) => track.stop());
      }
      stream = await navigator.mediaDevices.getUserMedia({ video: true });
      cameraFeed.srcObject = stream;
      mediaRecorder = new MediaRecorder(stream);
      chunks = [];
  
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
  
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        const videoUrl = URL.createObjectURL(blob);
        const videoElement = document.createElement('video');
        videoElement.src = videoUrl;
        videoElement.controls = true;
        defectImagesContainer.appendChild(videoElement);
      };
    } catch (error) {
      console.error('Error accessing the camera:', error);
    }
  });

stopCameraBtn.addEventListener('click', () => {
  if (stream) {
    stream.getTracks().forEach((track) => track.stop());
    stream = null;
    mediaRecorder = null;
    chunks = [];
  }
});

// Function to create and add defect image to the container
function addDefectImage(imageUrl) {
  const imgElement = document.createElement('img');
  imgElement.src = imageUrl;
  imgElement.alt = 'Defect Image';
  defectImagesContainer.appendChild(imgElement);
}
});
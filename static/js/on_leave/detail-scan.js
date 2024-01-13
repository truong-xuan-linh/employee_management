let videoStream;
        let frontCamera = false;
        const video = document.getElementById('video');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        async function openCamera() {
            try {
                videoStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: (frontCamera ? 'user' : 'environment') } });
                video.srcObject = videoStream;
                intervalId = setInterval(capturePhoto, 500);
            } catch (err) {
                console.error('Error accessing the camera: ', err);
            }
        }

        function toggleCamera() {
            frontCamera = !frontCamera;
            if (videoStream) {
                videoStream.getTracks().forEach(track => track.stop());
            }
            openCamera();
        }

        function capturePhoto() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            // document.getElementById('captureButton').disabled = true;
            // Chuyển ảnh thành base64 để gửi về server
            const imageBase64 = canvas.toDataURL('image/png');
            
            // Gửi ảnh về server
            fetch('/on-leave/detail/scan', {
                method: 'POST',
                body: JSON.stringify({ image: imageBase64 }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then((response) => response.json())
            .then((data) => {
                // console.error('Error:', data);
                
                var statusElement = document.getElementById('status');
                statusElement.innerText = data.status;
                if (data.status === 'Thành công') {
                    statusElement.style.backgroundColor = 'green';
                    window.location.href = data.redirect_url;
                    
                } else {
                    statusElement.style.backgroundColor = 'red';
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
        openCamera();
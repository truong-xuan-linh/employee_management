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

        function getParameterByName(name, url) {
            if (!url) url = window.location.href;
            name = name.replace(/[\[\]]/g, "\\$&");
            var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
                results = regex.exec(url);
            if (!results) return null;
            if (!results[2]) return '';
            return decodeURIComponent(results[2].replace(/\+/g, " "));
        }

        function capturePhoto() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            // document.getElementById('captureButton').disabled = true;
            // Chuyển ảnh thành base64 để gửi về server
            const imageBase64 = canvas.toDataURL('image/png');
            const guardType = getParameterByName('guard_type');
            // Gửi ảnh về server
            fetch('/guard/qr-scan?guard_type='+guardType, {
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
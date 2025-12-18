async function startCamera(): Promise<void> {
    const stream = await navigator.mediaDevices.getUserMedia({
        video: true
    });

    const video = document.getElementById("camera") as HTMLVideoElement;
    video.srcObject = stream;
}

startCamera();

setInterval(() => {
    const video = document.getElementById("camera") as HTMLVideoElement;
    if (!video || video.videoWidth === 0) return; // kamera belum siap

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
        if (!blob) return;

        const formData = new FormData();
        formData.append("file", blob, "frame.jpg");

        try {
            const res = await fetch("http://localhost:8000/upload_frame", {
                method: "POST",
                body: formData
            });

            const json = await res.json();
        } catch (err) {
            console.error("Upload error:", err);
        }
    }, "image/jpeg");
}, 5000);
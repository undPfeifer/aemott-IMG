document.getElementById('imageForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    
    try {
        const response = await fetch('/.netlify/functions/process-image', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Image processing failed');
        
        const result = await response.json();
        
        document.getElementById('processedImage').src = `data:image/png;base64,${result.processedImage}`;
        document.getElementById('maskImage').src = `data:image/png;base64,${result.mask}`;
        document.getElementById('downloadProcessed').href = `data:image/png;base64,${result.processedImage}`;
        document.getElementById('downloadMask').href = `data:image/png;base64,${result.mask}`;
        document.getElementById('result').style.display = 'block';
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while processing the image.');
    }
});

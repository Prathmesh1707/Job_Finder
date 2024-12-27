document.getElementById('upload-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById('resume');
    formData.append('resume', fileInput.files[0]);

    const response = await fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '<h2>Matching Jobs</h2>';

    if (data.jobs && data.jobs.length > 0) {
        data.jobs.forEach(job => {
            resultsDiv.innerHTML += `<p><strong>${job.title}</strong> at ${job.company}<br>
            <a href="${job.link}" target="_blank">Apply Here</a></p>`;
        });
    } else {
        resultsDiv.innerHTML += '<p>No matching jobs found.</p>';
    }
});

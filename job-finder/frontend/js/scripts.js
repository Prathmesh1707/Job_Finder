document.getElementById('resumeForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData();
    const fileInput = document.querySelector('input[type="file"]');
    formData.append('resume', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const resultsDiv = document.getElementById('resumeResults');
        if (data.error) {
            resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            const resumeDetails = data.resume_details;
            const jobs = data.jobs;
            
            let resultsHTML = `
                <h2>Resume Details</h2>
                <p><strong>Skills:</strong> ${resumeDetails.skills.join(', ')}</p>
                <h3>Job Listings</h3>
                <ul>
            `;
            
            jobs.forEach(job => {
                resultsHTML += `
                    <li>
                        <strong>${job.title}</strong><br>
                        Company: ${job.company}<br>
                        <a href="${job.link}" target="_blank">Apply Here</a>
                    </li>
                `;
            });
            
            resultsHTML += '</ul>';
            resultsDiv.innerHTML = resultsHTML;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

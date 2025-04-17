document.getElementById('searchForm').onsubmit = async function(e) {
    e.preventDefault();
    const query = document.getElementById('query').value;
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = 'Searching...';

    const res = await fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'query=' + encodeURIComponent(query)
    });

    const data = await res.json();
    resultsDiv.innerHTML = '';

    data.forEach(video => {
        const div = document.createElement('div');
        div.className = 'result';
        div.innerHTML = `
            <p><b>${video.title}</b></p>
            <button onclick="convert('${video.id}', 'mp3', '${video.title.replace(/'/g, "\\'")}')">Convert to MP3</button>
            <button onclick="convert('${video.id}', 'mp4', '${video.title.replace(/'/g, "\\'")}')">Convert to MP4</button>
            <div class="progress"><div class="progress-bar" id="progress-${video.id}"></div></div>
            <div id="preview-${video.id}"></div>
        `;
        resultsDiv.appendChild(div);
    });
};

async function convert(id, format, title) {
    const progressBar = document.getElementById('progress-' + id);
    progressBar.style.width = '10%';

    const res = await fetch('/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, format, title })
    });

    progressBar.style.width = '100%';

    const data = await res.json();
    const preview = document.getElementById('preview-' + id);
    const url = data.url;

    if (format === 'mp3') {
        preview.innerHTML = `
            <audio controls src="${url}"></audio><br>
            <a href="${url}" class="btn" download>Download MP3</a>
        `;
    } else {
        preview.innerHTML = `
            <video width="320" controls src="${url}"></video><br>
            <a href="${url}" class="btn" download>Download MP4</a>
        `;
    }

    progressBar.style.width = '0%';
}

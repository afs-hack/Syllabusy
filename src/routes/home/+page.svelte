<script lang="ts">
  export const trailingSlash = 'always';
  let files: File[] = [];
  let summary = "";
  let loading = false;
  const BACKEND_URL = "http://localhost:5000/api/upload-pdf";
  const STATUS_URL = "http://localhost:5000/api/status"; // New status endpoint

  function handleFiles(selectedFiles: FileList) {
    const newFiles = Array.from(selectedFiles);
    // avoid duplicates
    files = [...files, ...newFiles.filter(f => !files.some(existing => existing.name === f.name))];
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    if (event.dataTransfer?.files) handleFiles(event.dataTransfer.files);
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault(); // needed to allow drop
  }

  function removeFile(index: number) {
    files.splice(index, 1);
    files = [...files]; // trigger reactivity
  }

  async function handleUpload() {
    if (files.length === 0) {
      alert("Please select at least one file.");
      return;
    }

    loading = true;
    summary = "";

    const formData = new FormData();
    files.forEach(file => formData.append("files", file));

    try {
      const res = await fetch(BACKEND_URL, {
        method: "POST",
        body: formData,
        headers: {
             'User-ID': 'Swaggy McBaggums' // Example header, modify as needed
        },
      });

      if (!res.ok) throw new Error("Backend error");

      const data = await res.json();
      summary = data.summary || "No summary returned.";
    } catch (err) {
      summary = "Error: " + (err instanceof Error ? err.message : err);
    } finally {
      loading = false;
    }
  }

    // --- NEW FUNCTION TO CHECK BACKEND STATUS ---
  async function checkStatus() {
    loading = true;
    summary = "Checking backend status...";
    try {
      // Sends a GET request to the new /api/status endpoint
      const res = await fetch(STATUS_URL, {
        method: "POST"
      });

      if (!res.ok) throw new Error("Server down or unreachable: " + res.statusText);

      const data = await res.json();
      // Format the status message nicely for the textarea
      summary = `Backend Status Check Successful:\n\nStatus: ${data.status}\nMessage: ${data.message}\nFirebase: ${data.firebase_status}`;

    } catch (err) {
      summary = "Connection Error: Cannot reach Flask server. Check server console for CORS/network issues.";
    } finally {
      loading = false;
    }
  }
</script>

<style>
  /* Google Font loaded in app.html head */
  main {
    max-width: 600px;
    margin: 3em auto;
    padding: 2em;
    background: #fff5f8;
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    font-family: 'Roboto', 'Segoe UI Emoji', sans-serif;
    color: #333;
  }

  h1 {
    font-family: 'Roboto', 'Segoe UI Emoji', sans-serif;
    font-weight: 700;
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 1.5em;
  }

  .dropzone {
    border: 2px dashed #ff77a9;
    border-radius: 12px;
    padding: 2em;
    text-align: center;
    cursor: pointer;
    margin-bottom: 1em;
    background-color: #ffe6f0;
    transition: background-color 0.2s;
  }

  .dropzone:hover {
    background-color: #ffd0e0;
  }

  .file-button, button.upload {
    padding: 0.6em 1.2em;
    background: #ff77a9;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-bottom: 1em;
    transition: background 0.2s;
  }

  /* New style for the status button */
  button.status-check {
    padding: 0.6em 1.2em;
    background: #a977ff; /* A different color for distinction */
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-bottom: 1em;
    transition: background 0.2s;
  }

  .file-button:hover, button.upload:hover {
    background: #ff4d85;
  }

  .file-button:disabled, button.upload:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  ul {
    margin: 1em 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5em;
  }

  li {
    background: #ffb6c1;
    color: white;
    padding: 0.4em 0.8em;
    border-radius: 6px;
    display: flex;
    align-items: center;
  }

  li button {
    background: transparent;
    border: none;
    color: white;
    font-weight: bold;
    margin-left: 0.5em;
    cursor: pointer;
  }

  li button:hover {
    color: #ffdddd;
  }

  textarea {
    width: 100%;
    height: 250px;
    margin-top: 1em;
    padding: 1em;
    border-radius: 8px;
    font-family: 'Roboto', monospace;
    font-size: 1rem;
    border: 1px solid #ff77a9;
    resize: vertical;
  }
</style>

<main>
  <h1>🌷 AI Syllabus Summarizer</h1>

  <!-- Drag and Drop -->
  <div
  class="dropzone"
  on:drop={handleDrop}
  on:dragover={handleDragOver}
  on:click={() => {
    const input = document.getElementById('fileInput') as HTMLInputElement;
    input?.click();
  }}
  role="button"
  tabindex="0"
  on:keydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      const input = document.getElementById('fileInput') as HTMLInputElement;
      input?.click();
    }
  }}
>
  Drag & Drop files here or click to select
</div>

  <!-- File select button -->
  <button class="file-button" type="button" on:click={() => {
  const input = document.getElementById('fileInput') as HTMLInputElement;
  input?.click();
}}>
    Select Files
  </button>

 <input
  type="file"
  multiple
  id="fileInput"
  style="display: none"
  on:change={(e) => {
  const target = e.target as HTMLInputElement;
  if (target.files) handleFiles(target.files);
}}
/>
  <!-- File list -->
  {#if files.length > 0}
    <ul>
      {#each files as f, i}
        <li>
          {f.name} <button type="button" on:click={() => removeFile(i)}>×</button>
        </li>
      {/each}
    </ul>
  {/if}

<!-- NEW STATUS CHECK BUTTON -->
  <button class="status-check" on:click={checkStatus} disabled={loading}>
    {loading ? "Checking..." : "Check API Status"}
  </button>

  <button class="upload" on:click={handleUpload} disabled={loading}>
    {loading ? "Analyzing..." : "Upload and Summarize"}
  </button>

  {#if summary}
    <h2>Summary</h2>
    <textarea readonly>{summary}</textarea>
  {/if}
</main>
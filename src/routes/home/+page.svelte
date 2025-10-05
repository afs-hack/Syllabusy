<script lang="ts">
  import { onMount } from 'svelte';
  
  let files: File[] = [];
  let summary = "";
  let loading = false;
  let starsContainer: HTMLDivElement;
  const BACKEND_URL = "http://localhost:5000/upload";

  onMount(() => {
    for (let i = 0; i < 50; i++) {
      const star = document.createElement('div');
      star.className = 'star';
      star.style.left = `${Math.random() * 100}%`;
      star.style.top = `${Math.random() * 100}%`;
      star.style.animationDelay = `${Math.random() * 3}s`;
      starsContainer?.appendChild(star);
    }
  });

  function handleFiles(selectedFiles: FileList) {
    const newFiles = Array.from(selectedFiles);
    files = [...files, ...newFiles.filter(f => !files.some(existing => existing.name === f.name))];
  }

  function handleDrop(event: DragEvent) {
    event.preventDefault();
    if (event.dataTransfer?.files) handleFiles(event.dataTransfer.files);
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
  }

  function removeFile(index: number) {
    files.splice(index, 1);
    files = [...files];
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
        body: formData
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
</script>

<style>
  :global(body) {
    margin: 0;
    font-family: 'Fredoka', 'Inter', sans-serif;
    background-color: #0D1117;
    color: #F9F9FB;
    min-height: 100vh;
  }

  .stars {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
  }

  :global(.star) {
    position: absolute;
    width: 2px;
    height: 2px;
    background: white;
    border-radius: 50%;
    animation: twinkle 3s ease-in-out infinite;
    box-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
  }

  @keyframes twinkle {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
  }

  main {
    position: relative;
    z-index: 1;
    max-width: 700px;
    margin: 3rem auto;
    padding: 2rem;
    text-align: center;
  }

  .owl-container {
    font-size: 100px;
    margin-bottom: 1rem;
    animation: float 3s ease-in-out infinite;
    filter: drop-shadow(0 8px 16px rgba(94, 234, 212, 0.3));
  }

  @keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-15px); }
  }

  h1 {
    font-family: 'Fredoka', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    color: #5EEAD4;
    margin: 0 0 0.5rem 0;
    line-height: 1;
    letter-spacing: -2px;
  }

  .subtitle {
    font-size: 1.25rem;
    font-weight: 300;
    color: #BAC2C9;
    margin-bottom: 3rem;
  }

  .dropzone {
    border: 3px dashed #5EEAD4;
    border-radius: 16px;
    padding: 3rem 2rem;
    cursor: pointer;
    margin-bottom: 2rem;
    background-color: rgba(94, 234, 212, 0.05);
    transition: all 0.3s;
  }

  .dropzone:hover {
    background-color: rgba(94, 234, 212, 0.1);
    border-color: #5EEAD4;
    transform: translateY(-2px);
  }

  .dropzone p {
    color: #F9F9FB;
    font-size: 1.1rem;
  }

  .file-list {
    background: rgba(94, 234, 212, 0.05);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }

  .file-list h3 {
    color: #5EEAD4;
    margin: 0 0 1rem 0;
  }

  .file-list ul {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .file-list li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    background: rgba(13, 17, 23, 0.5);
    border-radius: 8px;
  }

  .file-name {
    color: #F9F9FB;
  }

  .remove-btn {
    background: #ff4757;
    color: white;
    border: none;
    border-radius: 50%;
    width: 28px;
    height: 28px;
    font-size: 1.5rem;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .remove-btn:hover {
    transform: scale(1.1);
  }

  .upload-btn {
    padding: 1rem 3rem;
    font-size: 1.2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #5EEAD4 0%, #4285f4 100%);
    color: #0D1117;
    border: none;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(94, 234, 212, 0.4);
  }

  .upload-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(94, 234, 212, 0.5);
  }

  .upload-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .summary-section {
    background: rgba(94, 234, 212, 0.05);
    border-radius: 16px;
    padding: 2rem;
    margin-top: 3rem;
    animation: slideUp 0.5s ease-out;
  }

  .summary-section h2 {
    color: #5EEAD4;
    margin: 0 0 1.5rem 0;
  }

  .summary-content {
    color: #F9F9FB;
    line-height: 1.8;
    white-space: pre-wrap;
    text-align: left;
  }

  @keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>

<div class="stars" bind:this={starsContainer}></div>

<main>
  <div class="owl-container">🦉</div>
  
  <h1>Syllabusy</h1>
  <p class="subtitle">AI-Powered Syllabus Analyzer</p>

  <div
    class="dropzone"
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:click={() => document.getElementById('fileInput')?.click()}
    on:keydown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      document.getElementById('fileInput')?.click();
    }
  }}
  role="button"
  tabindex="0"
>
  <p>Drag & Drop syllabi here or click to select</p>
  </div>

  <input
    type="file"
    multiple
    id="fileInput"
    style="display: none"
    accept=".pdf"
    on:change={(e) => {
      const target = e.currentTarget;
      if (target.files) handleFiles(target.files);
    }}
  />

  {#if files.length > 0}
    <div class="file-list">
      <h3>Selected Files ({files.length})</h3>
      <ul>
        {#each files as f, i}
          <li>
            <span class="file-name">{f.name}</span>
            <button type="button" class="remove-btn" on:click={() => removeFile(i)}>×</button>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  <button class="upload-btn" on:click={handleUpload} disabled={loading || files.length === 0}>
    {loading ? "✨ Analyzing..." : "🦉 Analyze"}
  </button>

  {#if summary}
    <div class="summary-section">
      <h2>📚 Your Semester Overview</h2>
      <div class="summary-content">{summary}</div>
    </div>
  {/if}
</main>
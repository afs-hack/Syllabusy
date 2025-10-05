<script lang="ts">
  import { onMount } from 'svelte';
  import { user, isAuthenticated, login, logout } from "$lib/auth";
  const WELCOME_TEXT = "Welcome to";
  const TITLE = "Syllabusy";
  const SUBTITLE = "Your AI-Powered Syllabus Summarizer";

  let starsContainer: HTMLDivElement;

onMount(() => {
  // Create 50 random stars
  for (let i = 0; i < 50; i++) {
    const star = document.createElement('div');
    star.className = 'star';
    star.style.left = `${Math.random() * 100}%`;
    star.style.top = `${Math.random() * 100}%`;
    star.style.animationDelay = `${Math.random() * 3}s`;
    starsContainer?.appendChild(star);
  }
});

  async function goHome() {
    window.location.href = "/home"
  }

  // Automatically redirect after login
  $: if ($isAuthenticated) {
    goHome();
  }
</script>

<style>
  /* Make sure content is above stars */
.landing-container {
  position: relative;
  z-index: 1;
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


  .owl-container {
  font-size: 120px;
  margin-bottom: 1rem;
  animation: float 3s ease-in-out infinite;
  filter: drop-shadow(0 8px 16px rgba(94, 234, 212, 0.3));
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}
  /* NEW COLOR PALETTE: Dark Slate with Electric Mint Accent */
  :global(body) {
    margin: 0;
    font-family: 'Inter', sans-serif;
    background-color: #0D1117; 
    color: #F9F9FB;
    min-height: 100vh;
  }

  .landing-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    padding: 10vh 2rem 2rem;
    text-align: center;
  }

  .title-group {
    margin-bottom: 2rem;
  }

  .welcome {
  font-size: 3.5vw; /* Made much bigger */
  font-weight: 300;
  color: #BAC2C9; /* Softer color to match subtitle */
  margin: 0 0 0.5rem 0; /* Increased spacing below */
  letter-spacing: 2px; /* Added spacing between letters */ 
  }

  .title {
    /* MUCH LARGER: Increased font size for impact */
    font-size: 12vw; 
  font-weight: 900;
  font-family: 'Fredoka', sans-serif;
  color: #5EEAD4;
  margin: 0; /* Removed bottom margin */
  line-height: 0.85;
  letter-spacing: -4px;
  }

  .subtitle {
    font-size: 1.55vw;
  font-weight: 100;
  color: #BAC2C9;
  margin-top: 0.75rem; /* Reduced from 1rem */
  }

  .auth-button {
    background-color: #4285f4;
    color: white;
    font-weight: 700;
    padding: 0.75rem 2rem;
    border: none;
    border-radius: 0.5rem;
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    cursor: pointer;
    margin-top: 1.5rem;
    transition: background-color 0.2s, box-shadow 0.2s;
  }

  .auth-button:hover {
    background-color: #357ae8;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.6);
  }

  .google-icon {
    width: 24px;
    height: 24px;
    fill: white;
  }

  @media (max-width: 600px) {
    .welcome { font-size: 5vw; margin-bottom: 0.1rem; }
    .title { font-size: 20vw; letter-spacing: -2px; }
    .subtitle { font-size: 5vw; }
  }
</style>

<div class="stars" bind:this={starsContainer}></div>

<main class="landing-container">

  <!-- Owl icon -->
  <div class="owl-container">🦉</div>

  <div class="title-group">
    <p class="welcome">{WELCOME_TEXT}</p>
    <h1 class="title">{TITLE}</h1>
    <p class="subtitle">{SUBTITLE}</p>
  </div>

  <div class="flex flex-col items-center justify-center min-h-screen bg-gray-50 text-gray-800">
  {#if !$isAuthenticated}
    <div class="p-4 text-center">
      <button class="auth-button" on:click={login} aria-label="Sign in with Google Account">
        Sign In with Google
      </button>
    </div>
  {/if}
</div>
</main>
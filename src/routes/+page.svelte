<script lang="ts">
  import { user, isAuthenticated, login, logout } from "$lib/auth";

  const WELCOME_TEXT = "Welcome to";
  const TITLE = "Syllabusy";
  const SUBTITLE = "Organize your courses effortlessly";
</script>

<style>
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
    font-size: 1.5vw;
    font-weight: 400;
    color: #F9F9FB;
    margin: 0 0 0.25rem 0;
  }

  .title {
    font-size: 12vw;
    font-weight: 900;
    color: #5EEAD4;
    margin-bottom: 0;
    line-height: 0.85;
    letter-spacing: -4px;
  }

  .subtitle {
    font-size: 2vw;
    font-weight: 300;
    color: #BAC2C9;
    margin-top: 1rem;
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

<main class="landing-container">
  <div class="title-group">
    <p class="welcome">{WELCOME_TEXT}</p>
    <h1 class="title">{TITLE}</h1>
    <p class="subtitle">{SUBTITLE}</p>
  </div>

  {#if $isAuthenticated}
    <div class="p-4 text-center">
      <p class="text-lg font-semibold">Welcome, {$user?.name}</p>
      <img src="{$user?.picture}" alt="Profile picture" class="rounded-full mx-auto my-2" width="80" />
      <button on:click={logout} class="auth-button bg-red-500 hover:bg-red-600">
        Logout
      </button>
    </div>
  {:else}
    <div class="p-4 text-center">
      <button on:click={login} class="auth-button">
        Login with Auth0
      </button>
    </div>
  {/if}
</main>
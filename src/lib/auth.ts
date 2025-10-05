// $lib/auth.ts
import { writable } from 'svelte/store';
import { createAuth0Client, type Auth0Client } from '@auth0/auth0-spa-js';

export const user = writable(null);
export const isAuthenticated = writable(false);
export const googleAccessToken = writable<string | null>(null);
export const googleRefreshToken = writable<string | null>(null);

let auth0Client: Auth0Client;
const AUTH0_DOMAIN = "dev-g2otnhbqcj5kojjn.us.auth0.com";
const AUTH0_CLIENT_ID = "rHBgweejupAzx1LJ2nRweHbuA4KR281n";
const NAMESPACE = "https://syllabusy.app";

export async function initAuth0() {
  auth0Client = await createAuth0Client({
    domain: AUTH0_DOMAIN,
    clientId: AUTH0_CLIENT_ID,
    authorizationParams: {
      redirect_uri: window.location.origin,
      scope: 'openid profile email'
    }
  });

  // Check if already authenticated
  const authenticated = await auth0Client.isAuthenticated();
  isAuthenticated.set(authenticated);

  if (authenticated) {
    await loadUserData();
  }

  // Handle redirect callback
  if (window.location.search.includes('code=')) {
    await auth0Client.handleRedirectCallback();
    window.history.replaceState({}, document.title, window.location.pathname);
    await loadUserData();
  }
}

async function loadUserData() {
  const userData = await auth0Client.getUser();
  user.set(userData);
  isAuthenticated.set(true);

  // Get ID token claims (contains our custom Google token)
  const claims = await auth0Client.getIdTokenClaims();
  
  if (claims) {
    const googleToken = claims[`${NAMESPACE}/google_access_token`];
    const googleRefresh = claims[`${NAMESPACE}/google_refresh_token`];
    
    if (googleToken) {
      googleAccessToken.set(googleToken);
      console.log('✓ Google access token retrieved');
    }
    
    if (googleRefresh) {
      googleRefreshToken.set(googleRefresh);
      console.log('✓ Google refresh token retrieved');
    }
  }
}

export async function login() {
  console.log("here");
  await auth0Client.loginWithPopup({
    authorizationParams: {
      connection: 'google-oauth2',
      // Request offline access for refresh token
      access_type: 'offline',
      prompt: 'consent' // Force consent to ensure we get refresh token
    }
  });

  await loadUserData();
}

export async function logout() {
  await auth0Client.logout({
    logoutParams: {
      returnTo: window.location.origin
    }
  });
  
  user.set(null);
  isAuthenticated.set(false);
  googleAccessToken.set(null);
  googleRefreshToken.set(null);
}

// Initialize on module load
if (typeof window !== 'undefined') {
  initAuth0();
}

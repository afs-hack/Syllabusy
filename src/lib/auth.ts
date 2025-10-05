// src/lib/auth.ts
import { createAuth0Client, type Auth0Client, type User } from "@auth0/auth0-spa-js";
import { writable, type Writable } from "svelte/store";

export const user: Writable<User | null> = writable(null);
export const isAuthenticated = writable(false);
export const auth0Client: Writable<Auth0Client | null> = writable(null);
export const googleAccessToken = writable<string | null>(null);
export const googleRefreshToken = writable<string | null>(null);

const NAMESPACE = 'https://syllabusy.app'; // Must match your Action

export async function initAuth() {
  if (typeof window === "undefined") return;

  const client = await createAuth0Client({
    domain: "dev-g2otnhbqcj5kojjn.us.auth0.com",
    clientId: "rHBgweejupAzx1LJ2nRweHbuA4KR281n",
    authorizationParams: {
      redirect_uri: window.location.origin,
      scope: 'openid profile email'
    }
  });

  auth0Client.set(client);

  // Handle Auth0 redirect callback
  if (window.location.search.includes("code=") && window.location.search.includes("state=")) {
    await client.handleRedirectCallback();
    window.history.replaceState({}, document.title, window.location.pathname);
  }

  const loggedIn = await client.isAuthenticated();
  isAuthenticated.set(loggedIn);

  if (loggedIn) {
    await loadUserData(client);
  }
}

async function loadUserData(client: Auth0Client) {
  const profile = await client.getUser();
  user.set(profile ?? null);

  // Get Google access token from custom claims
  const claims = await client.getIdTokenClaims();
  
  if (claims) {
    const googleToken = claims[`${NAMESPACE}/google_access_token`];
    const googleRefresh = claims[`${NAMESPACE}/google_refresh_token`];
    
    if (googleToken) {
      googleAccessToken.set(googleToken);
      console.log('✓ Google access token retrieved for Calendar API');
    }
    
    if (googleRefresh) {
      googleRefreshToken.set(googleRefresh);
      console.log('✓ Google refresh token retrieved');
    }
  }
}

export async function login() {
  const client = get(auth0Client);
  if (client) {
    await client.loginWithRedirect({
      authorizationParams: {
        connection: 'google-oauth2',
        access_type: 'offline', // Request refresh token
        prompt: 'consent' // Force consent to get Calendar permissions
      }
    });
  }
}

export async function logout() {
  const client = get(auth0Client);
  if (client) {
    await client.logout({ 
      logoutParams: { returnTo: window.location.origin } 
    });
  }
  user.set(null);
  isAuthenticated.set(false);
  googleAccessToken.set(null);
  googleRefreshToken.set(null);
}

function get<T>(store: Writable<T>): T {
  let value: T;
  store.subscribe((v) => (value = v))();
  return value!;
}
import { createAuth0Client, type Auth0Client, type User } from "@auth0/auth0-spa-js";
import { writable, type Writable } from "svelte/store";

export const user: Writable<User | null> = writable(null);
export const isAuthenticated = writable(false);
export const auth0Client: Writable<Auth0Client | null> = writable(null);

export async function initAuth() {
  if (typeof window === "undefined") {
    // Don't run on the server
    return;
  }

  const client = await createAuth0Client({
    domain: "dev-g2otnhbqcj5kojjn.us.auth0.com",
    clientId: "rHBgweejupAzx1LJ2nRweHbuA4KR281n",
    authorizationParams: {
      redirect_uri: window.location.origin
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
    const profile = (await client.getUser()) ?? null;
    user.set(profile);
  }
}

export async function login() {
  const client = get(auth0Client);
  if (client) await client.loginWithRedirect();
}

export async function logout() {
  const client = get(auth0Client);
  if (client) await client.logout({ logoutParams: { returnTo: window.location.origin } });
}

function get<T>(store: Writable<T>): T {
  let value: T;
  store.subscribe((v) => (value = v))();
  return value!;
}

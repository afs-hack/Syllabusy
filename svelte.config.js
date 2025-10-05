import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	// Consult https://svelte.dev/docs/kit/integrations
	// for more information about preprocessors
	preprocess: vitePreprocess(),

	kit: {
		// We use adapter-static because Flask is serving the compiled files
        // and we do not need a Node server environment.
        adapter: adapter({
            // Ensure the final output folder matches Flask's static_folder
            pages: 'dist',
            assets: 'dist',
            fallback: 'index.html', // Needed for Flask routing compatibility
            precompress: false,
            strict: true
        }),
        
        // This is often required when not running at the root of a domain.
        // If your Svelte app is served directly from the root (http://localhost:5000/), 
        // you might not need the 'base' value, but it's often safer to include.
        paths: {
            // Tells Svelte that the app is served from the root.
            base: '', 
        },

        // Prevents SvelteKit from generating paths that are incompatible with Flask's routing
        // This is generally a good practice for static/server-side hosting.
        //trailingSlash: 'always', 
	}
};

export default config;

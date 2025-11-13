import { defineConfig } from "vite";

export default defineConfig({
    build: {
        lib: {
            entry: "src/index.js",
            name: "AuthSDK",                // window.AuthSDK.*
            fileName: (format) => `auth-sdk.${format}.js`,
            formats: ["es", "umd"],
        },
        rollupOptions: {
            output: {
                exports: "named",
            },
        },
        minify: "terser",
        outDir: "dist",
    },
});

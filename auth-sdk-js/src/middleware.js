// src/middleware.js
import { TokenStorage } from "./storage.js";

export class AuthFetch {
    /**
     * authClient: instance of AuthClient
     * storage: optional TokenStorage instance. If not provided, we create one using tenant from authClient
     */
    constructor(authClient, storage = null) {
        this.client = authClient;
        // create storage with tenant-aware prefix if not provided
        if (storage) {
            this.storage = storage;
        } else {
            this.storage = new TokenStorage("auth", authClient.tenant || null);
        }
    }

    /**
     * fetch wrapper that injects Authorization header (Bearer)
     * on 401 it will try refresh once (if refresh token exists), then retry original request
     */
    async fetch(input, options = {}) {
        const token = this.storage.accessToken;
        const headers = new Headers(options.headers || {});
        if (token) headers.set("Authorization", `Bearer ${token}`);

        let response = await fetch(input, { ...options, headers });

        if (response.status === 401 && this.storage.refreshToken) {
            try {
                const newTokens = await this.client.refresh(this.storage.refreshToken);

                // Expecting fields: access_token, refresh_token
                if (newTokens.access_token) this.storage.accessToken = newTokens.access_token;
                if (newTokens.refresh_token) this.storage.refreshToken = newTokens.refresh_token;

                headers.set("Authorization", `Bearer ${this.storage.accessToken}`);
                response = await fetch(input, { ...options, headers });
            } catch (e) {
                // clear tokens and surface auth error
                this.storage.clear();
                throw new Error("Unauthorized, please login again");
            }
        }
        return response;
    }
}

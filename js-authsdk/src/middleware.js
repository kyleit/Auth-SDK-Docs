// src/middleware.js
import { TokenStorage } from "./storage.js";

export class AuthFetch {
    constructor(authClient, storage = new TokenStorage()) {
        this.client = authClient;
        this.storage = storage;
    }

    async fetch(input, options = {}) {
        const token = this.storage.accessToken;
        const headers = new Headers(options.headers || {});
        if (token) headers.set("Authorization", `Bearer ${token}`);

        let response = await fetch(input, { ...options, headers });

        // Nếu token hết hạn → refresh và retry
        if (response.status === 401 && this.storage.refreshToken) {
            try {
                const newTokens = await this.client.refresh(this.storage.refreshToken);
                this.storage.accessToken = newTokens.access_token;
                this.storage.refreshToken = newTokens.refresh_token;

                headers.set("Authorization", `Bearer ${this.storage.accessToken}`);
                response = await fetch(input, { ...options, headers });
            } catch (e) {
                this.storage.clear();
                throw new Error("Unauthorized, please login again");
            }
        }
        return response;
    }
}

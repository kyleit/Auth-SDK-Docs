// src/client.js
export default class AuthClient {
    /**
     * options:
     *  - baseUrl (required) e.g. "https://auth.example.com"
     *  - tenant (optional) e.g. "demo" -> will target /api/v1/{tenant}/auth/*
     *  - loginPath / refreshPath / introspectPath (optional overrides)
     *  - headers (optional)
     */
    constructor({
        baseUrl,
        tenant = null,
        loginPath = null,
        refreshPath = null,
        introspectPath = null,
        headers = {},
    }) {
        if (!baseUrl) throw new Error("baseUrl is required");
        this.baseUrl = baseUrl.replace(/\/$/, "");

        // default path builder: tenant-aware
        const prefix = tenant ? `/api/v1/${tenant}/auth` : `/api/v1/auth`;

        this.loginUrl = this.baseUrl + (loginPath || `${prefix}/login`);
        this.refreshUrl = this.baseUrl + (refreshPath || `${prefix}/refresh`);
        this.introspectUrl = this.baseUrl + (introspectPath || `${prefix}/introspect`);

        this.tenant = tenant; // keep for storage prefix
        this.headers = { "Content-Type": "application/json", ...headers };
    }

    /**
     * Login payload uses identifier + password + client_id (+ optional totp)
     * extra is optional object for backward-compat or extra fields
     */
    async login(identifier, password, client_id, totp = null, extra = {}) {
        const body = {
            identifier,
            password,
            client_id,
            ...extra,
        };
        if (totp) body.totp = totp;

        const res = await fetch(this.loginUrl, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify(body),
        });

        if (!res.ok) {
            const text = await res.text().catch(() => res.statusText);
            throw new Error(`Login failed: ${res.status} ${text}`);
        }
        return res.json();
    }

    async refresh(refreshToken) {
        const res = await fetch(this.refreshUrl, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) {
            const text = await res.text().catch(() => res.statusText);
            throw new Error(`Refresh failed: ${res.status} ${text}`);
        }
        return res.json();
    }

    async introspect(token) {
        const res = await fetch(this.introspectUrl, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify({ token }),
        });
        if (!res.ok) {
            const text = await res.text().catch(() => res.statusText);
            throw new Error(`Introspect failed: ${res.status} ${text}`);
        }
        return res.json();
    }
}

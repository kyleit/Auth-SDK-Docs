// src/client.js
export default class AuthClient {
    constructor({
        baseUrl,
        loginPath = "/api/v1/auth/login",
        refreshPath = "/api/v1/auth/refresh",
        introspectPath = "/api/v1/auth/introspect",
        headers = {},
    }) {
        this.baseUrl = baseUrl.replace(/\/$/, "");
        this.loginUrl = this.baseUrl + loginPath;
        this.refreshUrl = this.baseUrl + refreshPath;
        this.introspectUrl = this.baseUrl + introspectPath;
        this.headers = { "Content-Type": "application/json", ...headers };
    }

    async login(username, password, totp = null, extra = {}) {
        const body = { username, password, ...extra };
        if (totp) body.totp = totp;
        const res = await fetch(this.loginUrl, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`Login failed: ${res.statusText}`);
        return res.json();
    }

    async refresh(refreshToken) {
        const res = await fetch(this.refreshUrl, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify({ refresh_token: refreshToken }),
        });
        if (!res.ok) throw new Error(`Refresh failed: ${res.statusText}`);
        return res.json();
    }

    async introspect(token) {
        const res = await fetch(this.introspectUrl, {
            method: "POST",
            headers: this.headers,
            body: JSON.stringify({ token }),
        });
        if (!res.ok) throw new Error(`Introspect failed: ${res.statusText}`);
        return res.json();
    }
}

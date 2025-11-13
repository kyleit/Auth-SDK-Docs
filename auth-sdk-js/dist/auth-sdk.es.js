class AuthClient {
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
    headers = {}
  }) {
    if (!baseUrl) throw new Error("baseUrl is required");
    this.baseUrl = baseUrl.replace(/\/$/, "");
    const prefix = tenant ? `/api/v1/${tenant}/auth` : `/api/v1/auth`;
    this.loginUrl = this.baseUrl + (loginPath || `${prefix}/login`);
    this.refreshUrl = this.baseUrl + (refreshPath || `${prefix}/refresh`);
    this.introspectUrl = this.baseUrl + (introspectPath || `${prefix}/introspect`);
    this.tenant = tenant;
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
      ...extra
    };
    if (totp) body.totp = totp;
    const res = await fetch(this.loginUrl, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(body)
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
      body: JSON.stringify({ refresh_token: refreshToken })
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
      body: JSON.stringify({ token })
    });
    if (!res.ok) {
      const text = await res.text().catch(() => res.statusText);
      throw new Error(`Introspect failed: ${res.status} ${text}`);
    }
    return res.json();
  }
}
class TokenStorage {
  /**
   * prefix: base prefix (default "auth")
   * tenant: optional tenant string -> final key = `${prefix}:${tenant}_access_token`
   */
  constructor(prefix = "auth", tenant = null) {
    this.prefix = prefix;
    this.tenant = tenant;
  }
  _key(name) {
    return this.tenant ? `${this.prefix}:${this.tenant}_${name}` : `${this.prefix}_${name}`;
  }
  get accessToken() {
    return localStorage.getItem(this._key("access_token"));
  }
  set accessToken(val) {
    if (val === null || val === void 0) {
      localStorage.removeItem(this._key("access_token"));
    } else {
      localStorage.setItem(this._key("access_token"), val);
    }
  }
  get refreshToken() {
    return localStorage.getItem(this._key("refresh_token"));
  }
  set refreshToken(val) {
    if (val === null || val === void 0) {
      localStorage.removeItem(this._key("refresh_token"));
    } else {
      localStorage.setItem(this._key("refresh_token"), val);
    }
  }
  clear() {
    localStorage.removeItem(this._key("access_token"));
    localStorage.removeItem(this._key("refresh_token"));
  }
}
class AuthFetch {
  /**
   * authClient: instance of AuthClient
   * storage: optional TokenStorage instance. If not provided, we create one using tenant from authClient
   */
  constructor(authClient, storage = null) {
    this.client = authClient;
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
        if (newTokens.access_token) this.storage.accessToken = newTokens.access_token;
        if (newTokens.refresh_token) this.storage.refreshToken = newTokens.refresh_token;
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
const index = { AuthClient, AuthFetch, TokenStorage };
export {
  AuthClient,
  AuthFetch,
  TokenStorage,
  index as default
};

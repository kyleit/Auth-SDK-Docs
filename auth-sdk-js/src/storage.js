// src/storage.js
export class TokenStorage {
    /**
     * prefix: base prefix (default "auth")
     * tenant: optional tenant string -> final key = `${prefix}:${tenant}_access_token`
     */
    constructor(prefix = "auth", tenant = null) {
        this.prefix = prefix;
        this.tenant = tenant;
    }

    _key(name) {
        // include tenant to isolate tokens between tenants if provided
        return this.tenant ? `${this.prefix}:${this.tenant}_${name}` : `${this.prefix}_${name}`;
    }

    get accessToken() {
        return localStorage.getItem(this._key("access_token"));
    }
    set accessToken(val) {
        if (val === null || val === undefined) {
            localStorage.removeItem(this._key("access_token"));
        } else {
            localStorage.setItem(this._key("access_token"), val);
        }
    }

    get refreshToken() {
        return localStorage.getItem(this._key("refresh_token"));
    }
    set refreshToken(val) {
        if (val === null || val === undefined) {
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

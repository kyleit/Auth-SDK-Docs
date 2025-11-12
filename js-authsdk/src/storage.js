// src/storage.js
export class TokenStorage {
    constructor(prefix = "auth") {
        this.prefix = prefix;
    }

    get accessToken() {
        return localStorage.getItem(`${this.prefix}_access_token`);
    }
    set accessToken(val) {
        localStorage.setItem(`${this.prefix}_access_token`, val);
    }

    get refreshToken() {
        return localStorage.getItem(`${this.prefix}_refresh_token`);
    }
    set refreshToken(val) {
        localStorage.setItem(`${this.prefix}_refresh_token`, val);
    }

    clear() {
        localStorage.removeItem(`${this.prefix}_access_token`);
        localStorage.removeItem(`${this.prefix}_refresh_token`);
    }
}

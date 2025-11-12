# 🛡️ GH Platform – JavaScript Auth SDK

SDK JavaScript đơn giản, dùng để đăng nhập (login), làm mới token (refresh), kiểm tra token (introspect),
và tự động xác thực các request HTTP khi gọi API của hệ thống Authenticate.

---

## 🚀 Tính năng chính

✅ Hỗ trợ `login`, `refresh`, `introspect`
✅ Middleware `AuthFetch` tự động gắn Bearer token vào các request
✅ Tự động gọi refresh khi access_token hết hạn
✅ Hoạt động tốt cả **browser** và **Node.js**
✅ Có thể nhúng trực tiếp vào web (file `auth-sdk.min.js`) hoặc cài qua npm

---

## 📦 Cài đặt

### 🔹 Cách 1 – Cài qua NPM (dành cho React / Vue / Svelte / Node.js)
```bash
npm install @gh-platform/auth-sdk
```

Import:
```js
import { AuthClient, AuthFetch, TokenStorage } from "@gh-platform/auth-sdk";
```

### 🔹 Cách 2 – Dùng trực tiếp trên Web (HTML thuần)
```html
<script src="https://cdn.yourdomain.com/auth-sdk.min.js"></script>
<script>
  const { AuthClient, AuthFetch, TokenStorage } = window.AuthSDK;
</script>
```

---

## 🔧 Build hướng dẫn
```bash
npm install vite terser -D
npm run build
npx terser dist/auth-sdk.umd.js -o dist/auth-sdk.min.js --compress --mangle
```

---

## 🌐 Demo HTML

```html
<!DOCTYPE html>
<html>
  <head><title>Auth SDK Demo</title></head>
  <body>
    <button id="login">Login</button>
    <button id="getUser">Get Profile</button>
    <script src="./dist/auth-sdk.min.js"></script>
    <script>
      const { AuthClient, TokenStorage, AuthFetch } = window.AuthSDK;
      const client = new AuthClient({ baseUrl: "https://auth.example.com" });
      const store = new TokenStorage();
      const fetcher = new AuthFetch(client, store);

      document.getElementById("login").onclick = async () => {
        const res = await client.login("alice", "password");
        store.accessToken = res.access_token;
        store.refreshToken = res.refresh_token;
        alert("Login success!");
      };

      document.getElementById("getUser").onclick = async () => {
        const r = await fetcher.fetch("https://api.example.com/me");
        const d = await r.json();
        console.log("User:", d);
      };
    </script>
  </body>
</html>
```

---

## 🧾 License

Bản quyền © 2025 GH Platform – Phát hành theo giấy phép MIT

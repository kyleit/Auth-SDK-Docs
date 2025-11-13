# 🛡️ GH Platform – JavaScript Auth SDK (Multi‑Tenant Version)

SDK JavaScript hỗ trợ đăng nhập (**login**), làm mới token (**refresh**), kiểm tra token (**introspect**),  
và tự động xác thực request HTTP trong kiến trúc **multi‑tenant** của GH Platform.

---

## 🚀 Tính năng chính

- ✅ Hỗ trợ **login**, **refresh**, **introspect**  
- ✅ **Tenant‑aware client**: mọi API tự động gắn `{tenant}` vào URL  
- ✅ Middleware **AuthFetch** tự động gắn Bearer token + auto refresh  
- ✅ Hoạt động cả **browser** & **Node.js**  
- ✅ Hỗ trợ nhúng trực tiếp (`auth-sdk.min.js`) hoặc cài qua **npm**

---

## 🧱 Kiến trúc Multi‑Tenant

Mọi API của GH Platform Authenticate đều sử dụng dạng:

```endpoint
/api/v1/{tenant}/auth/login
/api/v1/{tenant}/auth/refresh
/api/v1/{tenant}/auth/introspect
```

JavaScript SDK tự động truyền tenant trong mọi request.

### ✳️ Khởi tạo client theo tenant

```js
const tenant = "demo"; // hoặc trích xuất từ email: alice@example.com → example.com

const client = new AuthClient({
  baseUrl: "https://auth.example.com",
  tenant
});

const storage = new TokenStorage("auth", tenant);
const fetcher = new AuthFetch(client, storage);
```

### 📌 TokenStorage cũng tách token theo tenant

```js
// Lưu token theo từng tenant
storage.accessToken = res.access_token;
storage.refreshToken = res.refresh_token;

// Key lưu trong localStorage sẽ giống:
// auth.demo.access_token
// auth.demo.refresh_token
```

---

## 📦 Cài đặt

### 🔹 Cách 1 – Cài qua NPM

```bash
npm install @gh-platform/auth-sdk
```

Import:

```js
import { AuthClient, AuthFetch, TokenStorage } from "@gh-platform/auth-sdk";
```

---

### 🔹 Cách 2 – Dùng trực tiếp trên Web (HTML thuần)

```html
<script src="https://cdn.yourdomain.com/auth-sdk.min.js"></script>
<script>
  const { AuthClient, AuthFetch, TokenStorage } = window.AuthSDK;
</script>
```

---

## 🔐 Ví dụ Multi‑Tenant Login

```js
const tenant = "example";
const client = new AuthClient({
  baseUrl: "https://auth.example.com",
  tenant
});

async function login() {
  const res = await client.login(
    "alice@example.com", // identifier
    "User@123",          // password
    "gh-platform-admin"  // client_id
  );

  storage.accessToken = res.access_token;
  storage.refreshToken = res.refresh_token;

  console.log("Login success!", res);
}
```

---

## 🌐 Fetch API với AuthFetch (auto refresh + retry)

```js
const fetcher = new AuthFetch(client, storage);

const resp = await fetcher.fetch(
  client.baseUrl + "/api/v1/" + tenant + "/auth/me"
);

const user = await resp.json();
console.log("User:", user);
```

Tự động:

- Gắn `Authorization: Bearer <access_token>`
- Nếu token hết hạn → tự refresh → retry request
- Lưu token đúng tenant

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
    const tenant = "demo";

    const { AuthClient, TokenStorage, AuthFetch } = window.AuthSDK;
    const client = new AuthClient({ baseUrl: "https://auth.example.com", tenant });
    const storage = new TokenStorage("auth", tenant);
    const fetcher = new AuthFetch(client, storage);

    document.getElementById("login").onclick = async () => {
      const res = await client.login("alice@example.com", "User@123", "gh-platform-admin");
      storage.accessToken = res.access_token;
      storage.refreshToken = res.refresh_token;
      alert("Login success!");
    };

    document.getElementById("getUser").onclick = async () => {
      const r = await fetcher.fetch(client.baseUrl + "/api/v1/" + tenant + "/auth/me");
      console.log("User:", await r.json());
    };
  </script>
</body>
</html>
```

---

## 🧾 License

Bản quyền © 2025 **GH Platform** – Phát hành theo giấy phép **MIT**

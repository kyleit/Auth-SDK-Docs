# 🧩 GH Platform – Golang Auth SDK (Multi‑Tenant Version)

Golang SDK hỗ trợ xác thực cho hệ thống **GH Platform Authenticate**, bao gồm:

- Login  
- Refresh Token  
- Introspect  
- Middleware cho **Gin** & **Fiber**  
- Hỗ trợ kiến trúc **đa‑tenant** theo chuẩn `/api/v1/{tenant}/auth/...`

---

## 🚀 Tính năng chính

✅ Hỗ trợ multi‑tenant (mỗi request gắn với tenant riêng)  
✅ Đăng nhập bằng `identifier + password + client_id`  
✅ Hỗ trợ TOTP (nếu bật 2FA)  
✅ Middleware Gin & Fiber tự động introspect token  
✅ Sử dụng độc lập hoặc trong môi trường mono‑repo  
✅ Chuẩn Go module – có thể publish lên pkg.go.dev  

---

## 📦 Cài đặt qua Go module

Nếu SDK đã được public:

```bash
go get github.com/gh-platform/core/auth-sdk@latest
```

Hoặc chỉ định version cụ thể:

```bash
go get github.com/gh-platform/core/auth-sdk@v1.0.0
```

Import:

```go
import "github.com/gh-platform/core/auth-sdk/client"
```

---

## 🧱 Kiến trúc Multi‑Tenant

Mỗi tenant có route riêng:

```
/api/v1/{tenant}/auth/login
/api/v1/{tenant}/auth/refresh
/api/v1/{tenant}/auth/introspect
```

SDK được khởi tạo theo tenant:

```go
auth := client.NewAuthClient("demo", "https://auth.example.com")
```

---

## ⚙️ Định nghĩa LoginRequest (chuẩn backend)

```go
type LoginRequest struct {
    Identifier string  `json:"identifier"`
    Password   string  `json:"password"`
    ClientID   string  `json:"client_id"`
    Totp       *string `json:"totp,omitempty"`
}
```

---

## 🔐 Ví dụ sử dụng

### ✳️ Login

```go
import (
    "context"
    "fmt"
    "github.com/gh-platform/core/auth-sdk/client"
)

func main() {
    c := client.NewAuthClient("demo", "https://auth.example.com")

    res, err := c.Login(context.Background(), client.LoginRequest{
        Identifier: "alice@example.com",
        Password:   "User@123",
        ClientID:   "gh-platform-admin",
    })

    if err != nil {
        panic(err)
    }

    fmt.Println("Access Token:", res.AccessToken)
}
```

---

## ✳️ Middleware – Gin

```go
import (
    "github.com/gin-gonic/gin"
    "github.com/gh-platform/core/auth-sdk/middleware"
)

func main() {
    r := gin.Default()

    r.Use(middleware.GinAuthMiddleware(
        "demo",
        "https://auth.example.com",
    ))

    r.GET("/protected", func(c *gin.Context) {
        user, _ := c.Get("user")
        c.JSON(200, user)
    })

    r.Run(":8080")
}
```

---

## ✳️ Middleware – Fiber

```go
import (
    "github.com/gofiber/fiber/v2"
    "github.com/gh-platform/core/auth-sdk/middleware"
)

func main() {
    app := fiber.New()

    app.Use(middleware.FiberAuthMiddleware(
        "demo",
        "https://auth.example.com",
    ))

    app.Get("/protected", func(c *fiber.Ctx) error {
        user := c.Locals("user")
        return c.JSON(user)
    })

    app.Listen(":8080")
}
```

---

## 🧩 Cấu trúc SDK

```
auth-sdk/
├── client/
│   ├── client.go
│   ├── dto.go
│   └── errors.go
├── middleware/
│   ├── gin_middleware.go
│   └── fiber_middleware.go
├── go.mod
├── go.sum
└── README.md
```

---

## 🧰 Môi trường Mono‑Repo (go.work)

Tạo file:

```bash
go work init ./backend ./auth-sdk ./share-library
```

Ví dụ:

```go
go 1.23

use (
    ./backend
    ./auth-sdk
    ./share-library
)

replace github.com/gh-platform/core/auth-sdk => ./auth-sdk
replace github.com/gh-platform/core/share-library => ./share-library
```

Đồng bộ:

```bash
go work sync
```

---

## 🌐 Publish lên Go Packages

```bash
git tag v1.0.0
git push origin v1.0.0
```

Kiểm tra tại:

```
https://pkg.go.dev/github.com/gh-platform/core/auth-sdk
```

---

## 🔐 Repo Private

Nếu repo private:

```bash
go env -w GOPRIVATE=github.com/gh-platform/*
```

---

## 🧾 License

MIT License © 2025 GH Platform

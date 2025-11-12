# 🧩 GH Platform – Golang Auth SDK

Golang SDK hỗ trợ xác thực (`Login`, `Refresh`, `Introspect`) và Middleware cho **Gin** & **Fiber** framework.  
Đây là SDK dùng chung cho các service trong hệ thống **GH Platform Authenticate**.

---

## 🚀 Tính năng chính

✅ Đăng nhập và lấy token (login / refresh / introspect)  
✅ Middleware bảo vệ route cho **Gin** và **Fiber**  
✅ Có thể sử dụng riêng biệt hoặc trong workspace mono-repo  
✅ Chuẩn Go module, sẵn sàng publish lên [pkg.go.dev](https://pkg.go.dev)

---

## 📦 Cài đặt (sử dụng qua Go module)

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

## ⚙️ Cấu hình cho môi trường phát triển nội bộ (Mono-repo)

Nếu bạn đang làm việc trong **repo chứa nhiều module** (ví dụ `backend`, `auth-sdk`, `share-library`),
thì bạn nên cấu hình `go.work` để dễ dàng dùng local module mà không cần publish lên GitHub.

### 🔹 1. Tạo file `go.work` ở root project

```bash
go work init ./backend ./auth-sdk ./share-library
```

File `go.work` mẫu:

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

Lệnh đồng bộ workspace:
```bash
go work sync
```

> 🧠 Lưu ý:
> - `replace` chỉ áp dụng khi bạn **develop nội bộ** (local path)
> - Khi build production hoặc publish SDK, bạn cần **xoá replace** hoặc chuyển sang `go get` version cụ thể

---

### 🔹 2. Nếu không dùng workspace (`go.work`)

Bạn có thể thêm `replace` thủ công trong module chính (vd: `backend/go.mod`):

```go
replace github.com/gh-platform/core/auth-sdk => ../auth-sdk
```

và chạy:
```bash
go mod tidy
```

---

## 🧠 Sử dụng SDK

### ✳️ Login

```go
import (
    "context"
    "fmt"
    "github.com/gh-platform/core/auth-sdk/client"
)

func main() {
    c := client.NewAuthClient("https://auth.example.com")
    res, err := c.Login(context.Background(), "alice", "secret", "")
    if err != nil {
        panic(err)
    }
    fmt.Println("Access Token:", res.AccessToken)
}
```

---

### ✳️ Middleware – Gin

```go
import (
    "github.com/gin-gonic/gin"
    "github.com/gh-platform/core/auth-sdk/client"
    "github.com/gh-platform/core/auth-sdk/middleware"
)

func main() {
    r := gin.Default()
    authClient := client.NewAuthClient("https://auth.example.com")
    r.Use(middleware.GinAuthMiddleware(authClient))

    r.GET("/protected", func(c *gin.Context) {
        user, _ := c.Get("user")
        c.JSON(200, user)
    })

    r.Run(":8080")
}
```

---

### ✳️ Middleware – Fiber

```go
import (
    "github.com/gofiber/fiber/v2"
    "github.com/gh-platform/core/auth-sdk/client"
    "github.com/gh-platform/core/auth-sdk/middleware"
)

func main() {
    app := fiber.New()
    authClient := client.NewAuthClient("https://auth.example.com")
    app.Use(middleware.FiberAuthMiddleware(authClient))

    app.Get("/protected", func(c *fiber.Ctx) error {
        user := c.Locals("user")
        return c.JSON(user)
    })

    app.Listen(":8080")
}
```

---

## 🧱 Cấu trúc thư mục

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

## 🌐 Public lên Go Packages

1️⃣ Commit & push SDK lên GitHub  
2️⃣ Tạo tag version:
```bash
git tag v1.0.0
git push origin v1.0.0
```

3️⃣ Kiểm tra tại:
👉 https://pkg.go.dev/github.com/gh-platform/core/auth-sdk

hoặc ép Go tải:
```bash
go list -m github.com/gh-platform/core/auth-sdk@v1.0.0
```

---

## 🔐 Repo Private (nếu không public)

Cấu hình để Go tải module private:
```bash
go env -w GOPRIVATE=github.com/gh-platform/*
```

---

## 🧾 License

Bản quyền © 2025 GH Platform – MIT License

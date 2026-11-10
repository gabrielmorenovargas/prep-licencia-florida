# 🚗 Florida DMV Premium Flashcards Studio

Una plataforma de micro-aprendizaje interactiva y comercial de alto rendimiento, diseñada para la preparación del examen oficial de conducción del DMV de Florida (Leyes y Señales de Tránsito). Construida bajo una arquitectura moderna monolítica contenerizada de dos capas que simula un entorno serverless de AWS en producción.

---

## 🏗️ Arquitectura de la Aplicación (Local / Transición a AWS)

El proyecto está diseñado bajo el principio de **"AWS Ready"**, lo que significa que la lógica local replica de forma idéntica el ecosistema serverless en la nube, garantizando una migración suave a producción con costo fijo inicial de \$0 USD.

*   **Frontend & Lógica (Monolito Ligero):** Python + Streamlit (Gestiona las vistas interactivas, grids de respuestas 2x2, medidores en anillo y control de estados de sesión).
*   **Base de Datos (NoSQL Documental):** Amazon DynamoDB Local (Contenedor oficial que emula el comportamiento, particiones y almacenamiento de AWS mediante Single-Table Design).
*   **Orquestación y Entorno:** Docker + Docker Compose (Aísla los servicios y levanta una red local cifrada por tokens alfanuméricos).

---

## 🎨 Características Comerciales Incorporadas

*   **Interfaz de Alta Fidelidad:** Paleta de colores optimizada inspirada en las autopistas de Florida (Azul marino profundo de confianza `#002f6c` y Amarillo tránsito vial `#ffc72c`).
*   **Grid de Respuestas Adaptativo 2x2:** Las opciones múltiples tradicionales en lista se transforman en cuadrantes interactivos por cuadrículas para reducir la fatiga visual.
*   **Tablero de Analíticas en Tiempo Real:** Panel lateral derecho con contadores de aciertos, errores y medidor radial de progreso de sets cerrados mediante gradientes cónicos CSS.
*   **Capa de Autenticación Segura:** Flujo integrado de Login, Registro y validación por código OTP (Emulación nativa de AWS Cognito) con ocultamiento estricto de contraseñas.
*   **Control de Privacidad Administrativo:** Panel de control enterprise que audita el streaming de NoSQL y despliega un directorio limpio de usuarios, protegiendo las credenciales.

---

## 🛠️ Guía Paso a Paso para Replicar el Proyecto

Sigue estas instrucciones secuenciales para levantar el entorno de desarrollo contenerizado en tu máquina local:

### 📋 Prerrequisitos
1. Tener instalado [Git](https://git-scm.com).
2. Tener instalado [Docker Desktop](https://docker.com) (Asegúrate de que esté abierto y el motor marque **"Engine Running"** en color verde).
3. Tener instalado **VS Code** (o tu editor de código preferido).

---

### 📦 1. Clonar y Organizar la Estructura de Archivos
Asegúrate de tener los siguientes archivos en la raíz de tu directorio de trabajo local:

```text
📁 prep-licencia-florida/
├── 📄 app.py                  # Código unificado de la Aplicación (Streamlit)
├── 📄 init_db.py              # Script de Migración y Siembra por Lotes NoSQL
├── 📄 preguntas_parte1.json    # Banco de preguntas (Lote 1)
├── 📄 preguntas_parte2.json    # Banco de preguntas (Lote 2)
├── 📄 requirements.txt        # Dependencias de Python fijadas
└── 📄 Dockerfile              # Instrucciones de construcción del contenedor Linux
```

### 🚀 2. Construir e Iniciar la Infraestructura (Docker)
Abre tu terminal (PowerShell en Windows o Terminal en Mac/Linux) posicionándote en la carpeta de tu proyecto y ejecuta los siguientes comandos por separado:

```bash
# Descargar imágenes oficiales, empaquetar el frontend y encender servicios en segundo plano
docker compose up --build -d
```

### 📥 3. Sembrar el Banco de 60 Preguntas en la Base de Datos
Una vez que ambos contenedores marquen estado `Started`, ejecuta el script unificador de datos para poblar tu motor NoSQL de forma masiva:

```bash
docker compose exec web-app python init_db.py
```

### 💻 4. Acceso y Credenciales de Prueba
Abre tu navegador web e ingresa a la siguiente dirección local:
👉 **`http://localhost:8501`**

Para auditar las herramientas operativas y el flujo comercial del sistema, puedes iniciar sesión utilizando las credenciales maestras precargadas:

*   **Perfil Administrador Enterprise:**
    *   **Correo Electrónico:** `admin@floridadrive.com`
    *   **Contraseña:** `admin123`
*   **Perfil Cliente (Estudiante):**
    *   **Correo Electrónico:** `user@floridadrive.com`
    *   **Contraseña:** `user123`
    *   Puedes hacer clic directamente en el botón **"Crear Cuenta"**, registrar un correo simulado, rellenar el formulario e introducir el token OTP dinámico que se desplegará en la barra azul para validar tu identidad de alumno.

---

## 📈 Hoja de Ruta del Producto Comercial (Next Steps)
1.  **Modelo de Negocio Freemium:** Implementación del muro de pago (*Paywall*) con Stripe para bloquear el acceso a las flashcards a partir del Set 2 (Pregunta 5) para usuarios Free.
2.  **Ilustraciones Dinámicas de Tránsito:** Integración de campos `"url_ilustracion"` en NoSQL para renderizar diagramas vectoriales interactivos y simular escenarios viales en el cuadrante de estudio.
3.  **Despliegue Serverless en AWS:** Migración definitiva de la lógica e identidades a AWS Lambda y Amazon Cognito para soportar tráfico masivo pagando $0 USD en horas inactivas.

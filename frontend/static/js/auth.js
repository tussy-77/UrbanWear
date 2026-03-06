/**
 * Auth Utility Module
 * Gestiona tokens JWT, autenticación y sesiones
 */

const AuthUtils = {
    // Claves para localStorage
    TOKEN_KEY: 'access_token',
    USER_KEY: 'user',
    REMEMBER_KEY: 'remember_me',

    /**
     * Almacenar token JWT en localStorage
     * @param {string} token - Token JWT del servidor
     */
    setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    },

    /**
     * Obtener token JWT del localStorage
     * @returns {string|null} Token JWT o null si no existe
     */
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    /**
     * Verificar si el usuario está autenticado
     * @returns {boolean} true si hay token, false si no
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Almacenar datos del usuario en localStorage
     * @param {object} user - Objeto con datos del usuario
     */
    setUser(user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    },

    /**
     * Obtener datos del usuario desde localStorage
     * @returns {object|null} Objeto usuario o null
     */
    getUser() {
        const user = localStorage.getItem(this.USER_KEY);
        return user ? JSON.parse(user) : null;
    },

    /**
     * Cerrar sesión - limpiar localStorage y redirigir a login
     */
    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        localStorage.removeItem(this.REMEMBER_KEY);
        window.location.href = '/login';
    },

    /**
     * Crear headers HTTP con token para peticiones autenticadas
     * @returns {object} Headers con Content-Type y Authorization
     */
    getAuthHeaders() {
        const token = this.getToken();
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    },

    /**
     * Hacer petición HTTP con token automáticamente
     * @param {string} url - URL del endpoint
     * @param {object} options - Opciones fetch (method, body, etc)
     * @returns {Promise<Response|null>} Response o null si no autenticado
     */
    async authenticatedFetch(url, options = {}) {
        const token = this.getToken();

        if (!token) {
            window.location.href = '/login';
            return null;
        }

        const headers = {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        };

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Si el token expiró (401), redirigir a login
            if (response.status === 401) {
                this.logout();
                return null;
            }

            return response;
        } catch (error) {
            console.error('Error en petición autenticada:', error);
            throw error;
        }
    },

    /**
     * Proteger ruta - redirigir a login si no está autenticado
     * @returns {boolean} true si autenticado, false si no
     */
    protectRoute() {
        if (!this.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }
        return true;
    },

    /**
     * Guardar preferencia "recuérdame"
     * @param {boolean} remember
     */
    setRememberMe(remember) {
        if (remember) {
            localStorage.setItem(this.REMEMBER_KEY, 'true');
        } else {
            localStorage.removeItem(this.REMEMBER_KEY);
        }
    },

    /**
     * Obtener preferencia "recuérdame"
     * @returns {boolean}
     */
    getRememberMe() {
        return localStorage.getItem(this.REMEMBER_KEY) === 'true';
    },

    /**
     * Obtener información del token (sin verificar firma)
     * @returns {object|null} Payload del token
     */
    decodeToken() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
                atob(base64).split('').map(c => {
                    return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                }).join('')
            );
            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Error decodificando token:', error);
            return null;
        }
    },

    /**
     * Verificar si el token ha expirado
     * @returns {boolean} true si expirado
     */
    isTokenExpired() {
        const payload = this.decodeToken();
        if (!payload || !payload.exp) return true;

        const currentTime = Math.floor(Date.now() / 1000);
        return payload.exp < currentTime;
    },

    /**
     * Limpiar todos los datos de autenticación (sin redirigir)
     */
    clearAuth() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
    }
};

// Soporte para módulos ES6 (si se usa)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthUtils;
}
